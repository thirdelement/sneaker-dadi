from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('products_on_sale/', views.products_on_sale, name='products_on_sale'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('save-review/<int:product_id>/', views.save_review, name='save-review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete-review'),
    # path('edit-review/<int:review_id>/', views.edit_review, name='edit-review'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]