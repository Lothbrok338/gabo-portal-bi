"""Formularios acotados al contexto de una empresa."""
from django import forms
from django.contrib.auth import get_user_model
from .models import Dashboard


class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = ("title", "description", "public_url", "active")
        labels = {
            "title": "Nombre del informe",
            "description": "Descripción",
            "public_url": "Enlace público de Power BI (opcional)",
            "active": "Informe activo",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Ej. Ventas por sucursal"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "¿Qué información muestra este informe?"}),
            "public_url": forms.URLInput(attrs={"placeholder": "https://app.powerbi.com/view?r=..."}),
        }


class DashboardGrantsForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        label="Personas autorizadas en el portal",
        queryset=get_user_model().objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Solo miembros de esta empresa. El informe original de Publish to web continúa siendo público.",
    )

    def __init__(self, *args, company, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = (
            get_user_model().objects.filter(portal_memberships__company=company, is_active=True)
            .distinct().order_by("username")
        )