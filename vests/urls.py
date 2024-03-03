from django.urls import path
from vests import views
from .views import get_quantities

urlpatterns = [
    path('', views.home, name='home'),  # url for home page
    path('about/', views.about, name='about'),  # url for about page
    path('product/', views.product, name='product'),  # url for product page
    path('cart/', views.cart, name='cart'),  # url for cart page
    path('get_quantities/', get_quantities, name='get_quantities'),
]


