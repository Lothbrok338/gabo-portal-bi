from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Dashboard


def permitted_dashboards(user):
    qs = Dashboard.objects.filter(active=True, company__active=True).select_related("company")
    if user.is_superuser:
        return qs
    return qs.filter(company__memberships__user=user, grants__user=user).distinct()


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


def health(request):
    return JsonResponse({"status": "ok"})
