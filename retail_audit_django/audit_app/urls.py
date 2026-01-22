from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage/', views.manage_inventory, name='manage_inventory'),
    path('scan/', views.scan_shelf, name='scan_shelf'),
    path('confirm/<str:product_name>/', views.confirm_audit, name='confirm_audit'),
    
    # Inventory CRUD
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('stock/', views.StockListView.as_view(), name='view_stock'),
    path('products/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('', views.dashboard, name='home'), # Redirect root to dashboard
]
