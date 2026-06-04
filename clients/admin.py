"""Configuración del panel de administración de Django para el módulo de clientes.
Registra los modelos del módulo para que sean gestionables desde la interfaz
admin de Django, permitiendo operaciones CRUD a los superusuarios del sistema.
"""

from django.contrib import admin
from .models import Client, ClientHistory, Role, User

# Registro de modelos principales en el panel de administración
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Client)
admin.site.register(ClientHistory)
