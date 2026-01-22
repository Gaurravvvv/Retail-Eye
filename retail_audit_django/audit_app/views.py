from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product
from .ai_utils import detect_objects, get_image_embedding, cosine_similarity
import pickle
import numpy as np
from PIL import ImageDraw
import os

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def manage_inventory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        threshold = request.POST.get('threshold')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        
        if name and image:
            Product.objects.create(
                name=name,
                shelf_threshold=threshold,
                backroom_stock=stock,
                reference_image=image
            )
            messages.success(request, f"Product '{name}' added successfully with AI reference.")
            return redirect('manage_inventory')
            
    products = Product.objects.all()
    return render(request, 'manage_inventory.html', {'products': products})

@login_required
def scan_shelf(request):
    if request.method == 'POST':
        image = request.FILES.get('shelf_image')
        if not image:
            messages.error(request, "Please capture or upload an image.")
            return redirect('scan_shelf')

        try:
            # Save temp file for processing
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            # Ensure we are reading from the start of the file
            image.seek(0)
            file_content = image.read()
            
            if len(file_content) == 0:
                messages.error(request, "Uploaded image is empty.")
                return redirect('scan_shelf')

            path = default_storage.save('tmp/audit.jpg', ContentFile(file_content))
            full_path = default_storage.path(path)

            # Verify it's a valid image before proceeding
            from PIL import Image, UnidentifiedImageError
            try:
                with Image.open(full_path) as test_img:
                    test_img.verify()
            except UnidentifiedImageError:
                # Cleanup and error out
                if os.path.exists(full_path):
                    os.remove(full_path)
                messages.error(request, "The uploaded file is not a valid image.")
                return redirect('scan_shelf')

            # 1. Detection
            detections = detect_objects(full_path)
            
            # 2. Recognition & Visualizing
            all_products = Product.objects.all()
            product_embeddings = {p.id: p.get_embedding() for p in all_products if p.feature_vector}

            results = []
            detected_map = {}
            
            img_pil = Image.open(full_path)
            draw = ImageDraw.Draw(img_pil)

            for det in detections:
                crop_emb = get_image_embedding(det['crop'])
                
                best_score = -1
                best_product = None
                
                for pid, p_emb in product_embeddings.items():
                    if p_emb is not None:
                        score = cosine_similarity(crop_emb, p_emb)
                        if score > best_score:
                            best_score = score
                            best_product = all_products.get(id=pid)
                
                print(f"Detection: Best Score: {best_score}, Match: {best_product.name if best_product else 'None'}")
                
                match_name = "Unknown"
                if best_score > 0.6 and best_product:
                     match_name = best_product.name
                     if best_product.id not in detected_map:
                         detected_map[best_product.id] = {'product': best_product, 'count': 0}
                     detected_map[best_product.id]['count'] += 1
                
                results.append({
                    'box': det['box'],
                    'match': match_name,
                    'score': float(best_score)
                })

                draw.rectangle(det['box'], outline="red", width=3)
                draw.text((det['box'][0], det['box'][1]), f"{match_name} ({best_score:.2f})", fill="red")

            result_path = 'media/tmp/annotated_audit.jpg'
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            img_pil.save(result_path)
            
            context = {
                'image_url': '/media/tmp/annotated_audit.jpg',
                'detected_products': detected_map.values(),
                'raw_results': results
            }
            return render(request, 'scan.html', context)
            
        except Exception as e:
            print(f"Error in scan_shelf: {e}")
            messages.error(request, "An error occurred during scanning. Please try again.")
            return redirect('scan_shelf')

    return render(request, 'scan.html')

@login_required
def confirm_audit(request, product_name):
    product = get_object_or_404(Product, name=product_name)
    messages.info(request, f"Audit Confirmed for {product_name}. Checking thresholds...")
    
    if 0 < product.shelf_threshold:
        if product.backroom_stock > 0:
             messages.warning(request, f"Action: Restock {product_name} from Backroom.")
        else:
             messages.error(request, f"Action: Order {product_name} from supplier!")
    
    return redirect('dashboard')

# --- Inventory CRUD ---

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class StockListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'view_inventory.html'
    context_object_name = 'products'

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'product_update.html'
    fields = ['name', 'shelf_threshold', 'backroom_stock']
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, f"Product '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Product deleted successfully.")
        return super().delete(request, *args, **kwargs)