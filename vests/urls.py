from django.urls import path
from vests import views
from .views import get_quantities

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('product/', views.product, name='product'),
    path('get_quantities/', get_quantities, name='get_quantities'),
]


