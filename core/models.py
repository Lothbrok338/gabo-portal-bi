from urllib.parse import urlsplit, parse_qs
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_public_powerbi_url(value):
    if not value:
        return
    p = urlsplit(value)
    if (p.scheme != "https" or p.hostname != "app.powerbi.com" or p.netloc != "app.powerbi.com"
            or p.path != "/view" or p.username or p.password or p.fragment):
        raise ValidationError("Se requiere la URL pública https://app.powerbi.com/view?r=...")
    qs = parse_qs(p.query, keep_blank_values=True)
    if not qs.get("r") or not qs["r"][0] or len(qs["r"]) != 1:
        raise ValidationError("La URL debe contener el parámetro r de Publish to web")


class Company(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Empresas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [("manager", "Gestor"), ("viewer", "Lector")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portal_memberships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="viewer")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "company"], name="unique_company_membership")]

    def __str__(self):
        return f"{self.user} — {self.company}"


class Dashboard(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="dashboards")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    public_url = models.URLField(blank=True, validators=[validate_public_powerbi_url], max_length=2048,
                                 help_text="Solo Publish to web con datos ficticios o públicos. El enlace original NO es privado.")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.company} · {self.title}"


class DashboardGrant(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="grants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_grants")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["dashboard", "user"], name="unique_dashboard_grant")]

    def clean(self):
        super().clean()
        if self.dashboard_id and self.user_id and not Membership.objects.filter(
                company_id=self.dashboard.company_id, user_id=self.user_id).exists():
            raise ValidationError("Solo se puede asignar un informe a miembros de su empresa")

    def __str__(self):
        return f"{self.user} puede ver {self.dashboard}"
