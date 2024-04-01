from django.urls import path
from vests import views
from .views import get_quantities, add_to_cart

urlpatterns = [
    path('', views.home, name='home'),  # url for home page
    path('about/', views.about, name='about'),  # url for about page
    path('product/', views.product, name='product'),  # url for product page
    path('cart/', views.cart, name='cart'),  # url for cart page
    path('get_quantities/', get_quantities, name='get_quantities'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
]


