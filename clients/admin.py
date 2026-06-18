from django.contrib import admin
from .models import (
    Client,
    ChangeRequest,
    AuditLog,
    Role,
    User,
    WebType,
    WebFeature,
    Collaborator,
)

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Client)
admin.site.register(WebType)
admin.site.register(WebFeature)
admin.site.register(AuditLog)
admin.site.register(ChangeRequest)
admin.site.register(Collaborator)
