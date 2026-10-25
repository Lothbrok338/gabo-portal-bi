from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Company, Dashboard, DashboardGrant, Membership, validate_public_powerbi_url


class PortalAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user("alice", password="Password-laboratorio-1!")
        self.bob = User.objects.create_user("bob", password="Password-laboratorio-2!")
        self.superuser = User.objects.create_superuser("root_demo", "root@example.test", "Password-laboratorio-3!")
        self.a = Company.objects.create(name="Alpha ficticia", slug="alpha")
        self.b = Company.objects.create(name="Beta ficticia", slug="beta")
        self.ra = Dashboard.objects.create(company=self.a, title="Resumen Alpha")
        self.rb = Dashboard.objects.create(company=self.b, title="Resumen Beta")
        Membership.objects.create(user=self.alice, company=self.a)
        Membership.objects.create(user=self.bob, company=self.b)
        DashboardGrant.objects.create(user=self.alice, dashboard=self.ra)
        DashboardGrant.objects.create(user=self.bob, dashboard=self.rb)

    def test_login_required(self):
        response = self.client.get(reverse("dashboard_detail", args=[self.ra.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_cross_tenant_not_visible(self):
        self.client.force_login(self.alice)
        page = self.client.get(reverse("dashboard_list"))
        self.assertContains(page, "Resumen Alpha")
        self.assertNotContains(page, "Resumen Beta")
        self.assertEqual(self.client.get(reverse("dashboard_detail", args=[self.rb.id])).status_code, 404)

    def test_membership_alone_is_not_a_grant(self):
        DashboardGrant.objects.filter(user=self.alice).delete()
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse("dashboard_detail", args=[self.ra.id])).status_code, 404)

    def test_superuser_can_view_all(self):
        self.client.force_login(self.superuser)
        for report in [self.ra, self.rb]:
            self.assertEqual(self.client.get(reverse("dashboard_detail", args=[report.id])).status_code, 200)

    def test_disabled_dashboard_not_visible(self):
        self.ra.active = False
        self.ra.save()
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse("dashboard_detail", args=[self.ra.id])).status_code, 404)

    def test_cross_company_grant_rejected(self):
        with self.assertRaises(ValidationError):
            DashboardGrant(user=self.alice, dashboard=self.rb).full_clean()

    def test_public_url_validation(self):
        validate_public_powerbi_url("https://app.powerbi.com/view?r=FAKE_DEMO_TOKEN")
        for url in ["http://app.powerbi.com/view?r=test", "https://evil.example/view?r=test",
                    "https://app.powerbi.com.evil.example/view?r=test", "https://app.powerbi.com/view", 
                    "https://app.powerbi.com/view?r=", "https://app.powerbi.com/view#fragment"]:
            with self.subTest(url=url), self.assertRaises(ValidationError):
                validate_public_powerbi_url(url)

    def test_logout_requires_post(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)


class TenantManagementTests(TestCase):
    """Permisos de gestión no deben atravesar el aislamiento de clientes."""

    def setUp(self):
        User = get_user_model()
        self.manager = User.objects.create_user("manager_demo", password="Password-demo-1!")
        self.viewer = User.objects.create_user("viewer_demo", password="Password-demo-2!")
        self.stranger = User.objects.create_user("stranger_demo", password="Password-demo-3!")
        self.manager_b = User.objects.create_user("manager_beta", password="Password-demo-4!")
        self.a = Company.objects.create(name="Empresa Alfa", slug="alfa")
        self.b = Company.objects.create(name="Empresa Beta", slug="beta")
        Membership.objects.create(user=self.manager, company=self.a, role="manager")
        Membership.objects.create(user=self.viewer, company=self.a, role="viewer")
        Membership.objects.create(user=self.manager_b, company=self.b, role="manager")
        self.da = Dashboard.objects.create(company=self.a, title="Alfa existente")
        self.db = Dashboard.objects.create(company=self.b, title="Beta existente")
        DashboardGrant.objects.create(user=self.viewer, dashboard=self.da)

    def test_management_requires_login(self):
        response = self.client.get(reverse("manage_company", args=[self.a.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_viewer_and_stranger_cannot_manage(self):
        for user in (self.viewer, self.stranger):
            self.client.force_login(user)
            for url in (
                reverse("manage_company", args=[self.a.id]),
                reverse("manage_dashboard_create", args=[self.a.id]),
                reverse("manage_dashboard_edit", args=[self.a.id, self.da.id]),
                reverse("manage_dashboard_grants", args=[self.a.id, self.da.id]),
            ):
                with self.subTest(user=user.username, url=url):
                    self.assertEqual(self.client.get(url).status_code, 404)

    def test_manager_sees_only_own_company(self):
        self.client.force_login(self.manager)
        page = self.client.get(reverse("manage_index"))
        self.assertContains(page, "Empresa Alfa")
        self.assertNotContains(page, "Empresa Beta")
        own = self.client.get(reverse("manage_company", args=[self.a.id]))
        self.assertContains(own, "Alfa existente")
        self.assertNotContains(own, "Beta existente")
        self.assertEqual(self.client.get(reverse("manage_company", args=[self.b.id])).status_code, 404)

    def test_manager_can_create_report_only_in_company(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("manage_dashboard_create", args=[self.a.id]), {
            "title": "Nuevo Alfa", "description": "Prueba", "public_url": "", "active": "on",
            "company": self.b.id,  # suplantación de empresa enviada por el navegador
        })
        report = Dashboard.objects.get(title="Nuevo Alfa")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(report.company, self.a)
        self.assertEqual(DashboardGrant.objects.filter(dashboard=report).count(), 0)
        self.assertEqual(self.client.post(reverse("manage_dashboard_create", args=[self.b.id]), {
            "title": "Falso Beta", "active": "on",
        }).status_code, 404)
        self.assertFalse(Dashboard.objects.filter(title="Falso Beta").exists())

    def test_manager_cannot_edit_report_from_other_company(self):
        self.client.force_login(self.manager)
        url = reverse("manage_dashboard_edit", args=[self.a.id, self.db.id])
        self.assertEqual(self.client.post(url, {"title": "Modificado", "active": "on"}).status_code, 404)
        self.db.refresh_from_db()
        self.assertEqual(self.db.title, "Beta existente")
        url_b = reverse("manage_dashboard_grants", args=[self.b.id, self.db.id])
        self.assertEqual(self.client.get(url_b).status_code, 404)

    def test_invalid_powerbi_url_cannot_be_saved(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("manage_dashboard_edit", args=[self.a.id, self.da.id]), {
            "title": "Alfa existente", "public_url": "https://evil.example/view?r=x", "active": "on",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URL pública")
        self.da.refresh_from_db()
        self.assertFalse(self.da.public_url)

    def test_grants_cannot_include_another_company_user(self):
        self.client.force_login(self.manager)
        url = reverse("manage_dashboard_grants", args=[self.a.id, self.da.id])
        response = self.client.post(url, {"members": [str(self.manager_b.id)]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seleccione una opción válida")
        self.assertFalse(DashboardGrant.objects.filter(dashboard=self.da, user=self.manager_b).exists())
        self.assertTrue(DashboardGrant.objects.filter(dashboard=self.da, user=self.viewer).exists())

    def test_revoke_grant_removes_access_immediately(self):
        url = reverse("manage_dashboard_grants", args=[self.a.id, self.da.id])
        self.client.force_login(self.manager)
        response = self.client.post(url, {"members": []})
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(reverse("dashboard_detail", args=[self.da.id])).status_code, 404)

    def test_inactive_company_not_manageable(self):
        self.a.active = False
        self.a.save()
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse("manage_company", args=[self.a.id])).status_code, 404)

    def test_superuser_can_manage_all_companies(self):
        User = get_user_model()
        root = User.objects.create_superuser("root_manager", "root_manager@example.test", "strong-password")
        self.client.force_login(root)
        for company in (self.a, self.b):
            self.assertEqual(self.client.get(reverse("manage_company", args=[company.id])).status_code, 200)

    def test_manager_dashboard_edit_success(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("manage_dashboard_edit", args=[self.a.id, self.da.id]), {
            "title": "Alfa actualizado", "description": "Nuevo resumen", "public_url": "", "active": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.da.refresh_from_db()
        self.assertEqual(self.da.title, "Alfa actualizado")