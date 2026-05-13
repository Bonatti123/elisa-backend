from django.core.management.base import BaseCommand
from clients.models import Role, User


class Command(BaseCommand):
    help = "Crea los roles del sistema y el usuario Superadmin"

    ROLES = [
        {"name": "Superadmin", "description": "Acceso total al sistema"},
        {"name": "Admin", "description": "Administrador con permisos avanzados"},
        {"name": "Manager", "description": "Gestor de operaciones"},
        {"name": "Editor", "description": "Puede editar contenido"},
        {"name": "Viewer", "description": "Solo lectura"},
    ]

    def handle(self, *args, **options):
        roles_creados = []
        for r in self.ROLES:
            role, created = Role.objects.get_or_create(
                name=r["name"],
                defaults={"description": r["description"]},
            )
            roles_creados.append(role)
            self.stdout.write(
                f"{'Creado' if created else 'Ya existe'} rol: {role.name}"
            )

        superadmin_role = Role.objects.get(name="Superadmin")

        if not User.objects.filter(username="bonatti123").exists():
            User.objects.create_user(
                username="bonatti123",
                password="bonatti123",
                email="bonatti@elomux.com",
                first_name="Bon",
                last_name="Atti",
                role=superadmin_role,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS("Usuario Superadmin 'bonatti123' creado"))
        else:
            self.stdout.write("El usuario 'bonatti123' ya existe")
