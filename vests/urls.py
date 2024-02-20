from django.urls import path
from vests import views
urlpatterns = [
    path('', views.home, name='home')
]