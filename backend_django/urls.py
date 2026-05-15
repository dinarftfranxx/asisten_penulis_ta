# backend_django/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Menyambungkan semua URL dari nlp_engine ke awalan /api/
    path('api/', include('nlp_engine.urls')), 
]