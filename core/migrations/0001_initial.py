# Migration drafted for laboratory project. Confirm via manage.py makemigrations --check.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import core.models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Company", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=160)), ("slug", models.SlugField(unique=True)),
            ("active", models.BooleanField(default=True)),
        ], options={"verbose_name_plural": "Empresas", "ordering": ["name"]}),
        migrations.CreateModel(name="Membership", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("role", models.CharField(choices=[("manager", "Gestor"), ("viewer", "Lector")], default="viewer", max_length=10)),
            ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="core.company")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portal_memberships", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="Dashboard", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=160)), ("description", models.TextField(blank=True)),
            ("public_url", models.URLField(blank=True, help_text="Solo Publish to web con datos ficticios o públicos. El enlace original NO es privado.", max_length=2048, validators=[core.models.validate_public_powerbi_url])),
            ("active", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboards", to="core.company")),
        ], options={"ordering": ["title"]}),
        migrations.CreateModel(name="DashboardGrant", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("dashboard", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="grants", to="core.dashboard")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboard_grants", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.AddConstraint(model_name="membership", constraint=models.UniqueConstraint(fields=("user", "company"), name="unique_company_membership")),
        migrations.AddConstraint(model_name="dashboardgrant", constraint=models.UniqueConstraint(fields=("dashboard", "user"), name="unique_dashboard_grant")),
    ]
