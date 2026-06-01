# ==============================================================================
# SEED.PY — Comando para poblar la base de datos con datos iniciales
#
# Crea los 5 roles del sistema (Superadmin, Admin, Manager, Editor, Viewer)
# y el usuario Superadmin (Gerente General).
# Ejecución: python manage.py seed
# Idempotencia: si ya existen los datos, no los duplica.
# Nota: Solo crea roles y el Superadmin de forma atómica.
# ==============================================================================

import os
from django.db import transaction
from django.core.management.base import BaseCommand
from clients.models import Role, User


class Command(BaseCommand):
    # #BE054: Comando seed de datos iniciales — crea 5 roles y Superadmin
    # con transacción atómica e idempotencia
    help = "(#BE054) Inicializa los 5 roles del sistema y el perfil Superadmin"

    ROLES = [
        {"name": "Superadmin", "description": "Acceso total al sistema"},
        {"name": "Admin", "description": "Administrador con permisos avanzados"},
        {"name": "Manager", "description": "Gestor de operaciones"},
        {"name": "Editor", "description": "Puede editar contenido"},
        {"name": "Viewer", "description": "Solo lectura"},
    ]

    def handle(self, *args, **options) -> None:
        self.stdout.write("🔧 Iniciando seed de base de datos...\n")

        # Credenciales desde variables de entorno (Sección 3 SDD)
        superadmin_user = os.getenv("SUPERADMIN_USERNAME", "bonatti123")
        superadmin_pass = os.getenv("SUPERADMIN_PASSWORD", "bonatti123")
        superadmin_email = "bonatti@elomux.com"

        try:
            with transaction.atomic():
                # ─── 1. Roles ────────────────────────────────────────────────
                for r in self.ROLES:
                    role, created = Role.objects.get_or_create(
                        name=r["name"],
                        defaults={"description": r["description"]},
                    )
                    status_str = "✅ Creado" if created else "⏭  Ya existe"
                    self.stdout.write(f"{status_str}: Rol {role.name}")

                # ─── 2. Validación de preexistencia ──────────────────────────
                if User.objects.filter(
                    username=superadmin_user, email=superadmin_email
                ).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"⏭  Ya existe: Superadmin "
                            f"({superadmin_user} / {superadmin_email})."
                        )
                    )
                    return

                # ─── 3. Recuperación controlada del rol Superadmin ───────────
                try:
                    superadmin_role = Role.objects.get(name="Superadmin")
                except Role.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            "❌ ERROR CRÍTICO: El rol 'Superadmin' "
                            "no se encuentra en la base de datos."
                        )
                    )
                    raise transaction.TransactionManagementError(
                        "Cancelando transacción por ausencia de rol Superadmin."
                    )

                # ─── 4. Creación del Superadmin ─────────────────────────────
                User.objects.create_user(
                    username=superadmin_user,
                    password=superadmin_pass,
                    email=superadmin_email,
                    first_name="Bon",
                    last_name="Atti",
                    role=superadmin_role,
                    is_staff=True,
                    is_superuser=True,
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Creado: Superadmin '{superadmin_user}' "
                        f"con credenciales de entorno."
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Fallo catastrófico abortando seed: {e}")
            )
            raise
