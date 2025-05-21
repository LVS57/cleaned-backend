from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, ProductViewSet, RegisterView, index, create_product_from_qr, ActivateView

router = DefaultRouter()
router.register('products', ProductViewSet)

urlpatterns = [
    path('', index),  # This will show the JSON with users and products
    path('', include(router.urls)),  # Include viewset routes like /products/
    path('create-product/', create_product_from_qr, name='create-product'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
]
