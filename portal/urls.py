from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from core import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("portal/", views.dashboard_list, name="dashboard_list"),
    path("portal/informes/<int:pk>/", views.dashboard_detail, name="dashboard_detail"),
    path("portal/gestion/", views.manage_index, name="manage_index"),
    path("portal/gestion/<int:company_id>/", views.manage_company, name="manage_company"),
    path("portal/gestion/<int:company_id>/nuevo/", views.manage_dashboard_create, name="manage_dashboard_create"),
    path("portal/gestion/<int:company_id>/informes/<int:pk>/editar/", views.manage_dashboard_edit, name="manage_dashboard_edit"),
    path("portal/gestion/<int:company_id>/informes/<int:pk>/permisos/", views.manage_dashboard_grants, name="manage_dashboard_grants"),
    path("health/", views.health, name="health"),
    path("admin/", admin.site.urls),
]