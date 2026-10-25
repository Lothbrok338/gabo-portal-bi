import secrets
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from core.models import Company, Dashboard, Membership, DashboardGrant


class Command(BaseCommand):
    help = "Generar empresas, usuarios e informes completamente ficticios. NO USAR EN PRODUCCIÓN."

    def handle(self, *args, **kwargs):
        company, _ = Company.objects.get_or_create(slug="laboratorio", defaults={"name": "Empresa Laboratorio (ficticia)"})
        reports = [
            Dashboard.objects.get_or_create(company=company, title="Resumen ejecutivo", defaults={"description": "Indicadores generales ficticios"})[0],
            Dashboard.objects.get_or_create(company=company, title="Ventas y rentabilidad", defaults={"description": "Métricas comerciales ficticias"})[0],
        ]
        User = get_user_model()
        for name, ids in [("gabo_demo", [0, 1]), ("ventas_demo", [1]), ("direccion_demo", [0])]:
            user = User.objects.filter(username=name).first()
            if not user:
                pwd = secrets.token_urlsafe(14)
                user = User.objects.create_user(username=name, password=pwd, is_staff=False, is_superuser=False)
                self.stdout.write(f"Usuario {name} | Contraseña temporal SOLO PARA DEMO: {pwd}")
            else:
                self.stdout.write(f"Usuario {name} ya existe: NO se modifica su contraseña")
            Membership.objects.update_or_create(user=user, company=company, defaults={"role": "manager" if name == "gabo_demo" else "viewer"})
            for i in ids:
                DashboardGrant.objects.get_or_create(user=user, dashboard=reports[i])
        self.stdout.write(self.style.SUCCESS("Demo creada. Informes SIN enlaces Power BI y datos 100% ficticios."))