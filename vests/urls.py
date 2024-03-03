from django.urls import path
from vests import views

urlpatterns = [
    path('', views.home, name='home'),  # url for home page
    path('about/', views.about, name='about'),  # url for about page
    path('product/', views.product, name='product'),  # url for product page
    path('cart/', views.cart, name='cart'),  # url for cart page
]