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
    path("health/", views.health, name="health"),
    path("admin/", admin.site.urls),
]
