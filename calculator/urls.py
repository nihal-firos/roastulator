from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Add this for the main page
    path('api/roast/', views.roast_api, name='roast_api'),
]