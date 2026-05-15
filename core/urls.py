from django.contrib import admin
from django.urls import path

# NOTA: el prefijo /admin lo maneja el WSGIMiddleware en api/main.py
urlpatterns = [
    path("", admin.site.urls),
]
