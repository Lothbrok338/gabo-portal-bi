from django.db import connection, OperationalError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .forms import DashboardForm, DashboardGrantsForm
from .models import Company, Dashboard, DashboardGrant, Membership


def permitted_dashboards(user):
    qs = Dashboard.objects.filter(active=True, company__active=True).select_related("company")
    if user.is_superuser:
        return qs
    return qs.filter(company__memberships__user=user, grants__user=user).distinct()


def _managed_companies(user):
    qs = Company.objects.filter(active=True)
    if user.is_superuser:
        return qs
    return qs.filter(memberships__user=user, memberships__role="manager").distinct()


def _company_or_404(user, company_id):
    # Una empresa ajena no debe ser identificable por URL: devolver 404.
    return get_object_or_404(_managed_companies(user), pk=company_id)


def index(request):
    return redirect("dashboard_list" if request.user.is_authenticated else "login")


@login_required
def dashboard_list(request):
    dashboards = permitted_dashboards(request.user)
    return render(request, "core/list.html", {"dashboards": dashboards})


@login_required
def dashboard_detail(request, pk):
    dashboard = get_object_or_404(permitted_dashboards(request.user), pk=pk)
    return render(request, "core/detail.html", {"dashboard": dashboard})


@login_required
def manage_index(request):
    companies = _managed_companies(request.user)
    return render(request, "core/manage_index.html", {"companies": companies})


@login_required
def manage_company(request, company_id):
    company = _company_or_404(request.user, company_id)
    dashboards = Dashboard.objects.filter(company=company).prefetch_related("grants")
    members = Membership.objects.filter(company=company).select_related("user").order_by("user__username")
    return render(request, "core/manage_company.html", {
        "company": company, "dashboards": dashboards, "members": members,
    })


@login_required
def manage_dashboard_create(request, company_id):
    company = _company_or_404(request.user, company_id)
    form = DashboardForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.company = company  # nunca confiar en company enviada por el navegador
        report.save()
        messages.success(request, "Informe creado. Ahora puedes asignar acceso a los miembros.")
        return redirect("manage_dashboard_grants", company_id=company.id, pk=report.id)
    return render(request, "core/manage_form.html", {"company": company, "form": form, "creating": True})


@login_required
def manage_dashboard_edit(request, company_id, pk):
    company = _company_or_404(request.user, company_id)
    report = get_object_or_404(Dashboard, pk=pk, company=company)
    form = DashboardForm(request.POST if request.method == "POST" else None, instance=report)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cambios guardados correctamente.")
        return redirect("manage_company", company_id=company.id)
    return render(request, "core/manage_form.html", {
        "company": company, "form": form, "dashboard": report, "creating": False,
    })


@login_required
def manage_dashboard_grants(request, company_id, pk):
    company = _company_or_404(request.user, company_id)
    report = get_object_or_404(Dashboard, pk=pk, company=company)
    initial = {"members": list(report.grants.values_list("user_id", flat=True))}
    form = DashboardGrantsForm(request.POST if request.method == "POST" else None, company=company, initial=initial)
    if request.method == "POST" and form.is_valid():
        selected = set(form.cleaned_data["members"].values_list("pk", flat=True))
        with transaction.atomic():
            # El formulario solo acepta usuarios con membresía activa de esta empresa.
            DashboardGrant.objects.filter(dashboard=report).exclude(user_id__in=selected).delete()
            existing = set(DashboardGrant.objects.filter(dashboard=report).values_list("user_id", flat=True))
            DashboardGrant.objects.bulk_create(
                [DashboardGrant(dashboard=report, user_id=pk) for pk in selected - existing],
                ignore_conflicts=True,
            )
        messages.success(request, "Permisos del portal actualizados.")
        return redirect("manage_company", company_id=company.id)
    return render(request, "core/manage_grants.html", {
        "company": company, "dashboard": report, "form": form,
    })


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})