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
