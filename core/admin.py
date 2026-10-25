from django.contrib import admin
from .models import Company, Membership, Dashboard, DashboardGrant

# MVP: la administración de todas las empresas queda exclusivamente para el superusuario.
# NO otorgar is_staff a administradores empresariales hasta crear un admin aislado por compañía.
class SuperuserOnlyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

@admin.register(Company)
class CompanyAdmin(SuperuserOnlyAdmin):
    list_display = ("name", "slug", "active")
    search_fields = ("name",)

@admin.register(Membership)
class MembershipAdmin(SuperuserOnlyAdmin):
    list_display = ("user", "company", "role")
    list_filter = ("company", "role")

@admin.register(Dashboard)
class DashboardAdmin(SuperuserOnlyAdmin):
    list_display = ("title", "company", "active", "created_at")
    list_filter = ("company", "active")

@admin.register(DashboardGrant)
class DashboardGrantAdmin(SuperuserOnlyAdmin):
    list_display = ("user", "dashboard")
