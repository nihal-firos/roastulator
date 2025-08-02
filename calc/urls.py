# roastulator_project/urls.py
from django.contrib import admin
from django.urls import path, include # Add include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculator.urls')), # Add this line
]