from .views import _managed_companies


def management_navigation(request):
    if not request.user.is_authenticated:
        return {"can_manage_portal": False}
    return {"can_manage_portal": _managed_companies(request.user).exists()}