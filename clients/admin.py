"""Configuración del panel de administración de Django para el módulo de clientes.
Registra todos los modelos del módulo para gestionarlos desde la interfaz
admin de Django, permitiendo operaciones CRUD a los superusuarios del sistema.
"""

from django.contrib import admin
from .models import (
    Client,
    ClientHistory,
    ChangeRequest,
    AuditLog,
    Role,
    User,
    WebType,
    WebFeature,
)

# Registro de modelos principales en el panel de administración
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Client)
admin.site.register(ClientHistory)
admin.site.register(WebType)
admin.site.register(WebFeature)
admin.site.register(AuditLog)
admin.site.register(ChangeRequest)
