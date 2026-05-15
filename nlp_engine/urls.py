# nlp_engine/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Alamat URL kita nanti adalah: /cek-teks/
    path('cek-teks/', views.cek_teks, name='cek_teks'),
]