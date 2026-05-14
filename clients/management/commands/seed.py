from django.core.management.base import BaseCommand
from clients.models import Role, User


class Command(BaseCommand):
    """Comando para sembrar datos iniciales: roles y usuario Superadmin."""
    help = "Crea los roles del sistema y el usuario Superadmin"

    # Lista de roles predefinidos del sistema
    ROLES = [
        {"name": "Superadmin", "description": "Acceso total al sistema"},
        {"name": "Admin", "description": "Administrador con permisos avanzados"},
        {"name": "Manager", "description": "Gestor de operaciones"},
        {"name": "Editor", "description": "Puede editar contenido"},
        {"name": "Viewer", "description": "Solo lectura"},
    ]

    def handle(self, *args, **options):
        """Ejecuta la creación de roles y el usuario Superadmin por defecto."""
        roles_creados = []
        for r in self.ROLES:
            # Crea cada rol si no existe, o lo obtiene si ya fue creado
            role, created = Role.objects.get_or_create(
                name=r["name"],
                defaults={"description": r["description"]},
            )
            roles_creados.append(role)
            self.stdout.write(
                f"{'Creado' if created else 'Ya existe'} rol: {role.name}"
            )

        superadmin_role = Role.objects.get(name="Superadmin")

        # Crea el usuario Superadmin por defecto si no existe
        if not User.objects.filter(username="bonatti123").exists():
            User.objects.create_user(
                username="bonatti123",
                password="admin123",
                email="bonatti@elomux.com",
                first_name="Bon",
                last_name="Atti",
                role=superadmin_role,
                status="activo",
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS("Usuario Superadmin 'bonatti123' creado"))
        else:
            self.stdout.write("El usuario 'bonatti123' ya existe")

        # Actualiza la contraseña del usuario existente por si ha cambiado
        user = User.objects.get(username="bonatti123")
        if not user.check_password("admin123"):
            user.set_password("admin123")
            user.status = "activo"
            user.save()
            self.stdout.write(self.style.SUCCESS("Contraseña actualizada a admin123"))
