from django.db import models
from .ai_utils import get_image_embedding, detect_objects
import pickle

class Product(models.Model):
    name = models.CharField(max_length=100)
    shelf_threshold = models.IntegerField(default=5)
    backroom_stock = models.IntegerField(default=10)
    reference_image = models.ImageField(upload_to='product_refs/')
    feature_vector = models.BinaryField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.reference_image: # Always regenerate to fix bad embeddings
            # if not self.feature_vector: # Removed check to force update
            try:
                # Generate embedding from the uploaded image
                print(f"Generating embedding for {self.name}...")
                
                # Attempt to find the object in the reference image to align with scan logic
                detections = detect_objects(self.reference_image.path)
                if detections:
                    print(f"Object detected in reference image. Using crop for embedding.")
                    target_image = detections[0]['crop']
                else:
                    print(f"No object detected. Using full reference image.")
                    target_image = self.reference_image.path
                
                embedding = get_image_embedding(target_image)
                self.feature_vector = pickle.dumps(embedding)
                # Save again to store the vector
                super().save(update_fields=['feature_vector'])
            except Exception as e:
                print(f"Error generating embedding: {e}")

    def get_embedding(self):
        if self.feature_vector:
            return pickle.loads(self.feature_vector)
        return None

    def __str__(self):
        return self.name
