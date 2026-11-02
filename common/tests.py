import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve, reverse

from projects.forms import ProjectForm
from projects.models import Project
from skills.models import Skill
from users.avatars import create_avatar
from users.forms import ProfileForm

from .constants import PROJECT_CLOSED, PROJECT_OPEN
from .pagination import paginate_queryset


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ReviewRegressionTests(TestCase):
    def setUp(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory)
        settings_override = override_settings(MEDIA_ROOT=directory)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.password = "ReviewPassword!2026"
        self.user = get_user_model().objects.create_user(
            "review@example.com", self.password, name="Анна", surname="Тест"
        )
        self.project = Project.objects.create(name="Проверка ревью", owner=self.user)

    def profile_data(self, **extra):
        data = {
            "name": "Анна",
            "surname": "Тест",
            "email": self.user.email,
            "phone": "89001234567",
            "about": "Описание",
            "github_url": "",
        }
        data.update(extra)
        return data

    def test_pagination_accepts_custom_size_and_keeps_filter(self):
        request = RequestFactory().get("/project/list/", {"skill": "Python", "page": "2"})
        page, query_prefix = paginate_queryset(list(range(7)), request, page_size=3)
        self.assertEqual(list(page), [3, 4, 5])
        self.assertEqual(page.paginator.per_page, 3)
        self.assertEqual(query_prefix, "skill=Python&")

    def test_project_form_uses_model_status_choices(self):
        form = ProjectForm(instance=self.project)
        self.assertEqual(form.initial["status"], PROJECT_OPEN)
        self.assertEqual(
            list(form.fields["status"].choices)[-2:],
            [
                (PROJECT_OPEN, "Открыт"),
                (PROJECT_CLOSED, "Закрыт"),
            ],
        )
        form = ProjectForm({"name": "Проект", "status": "invalid"})
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_canonical_urls_and_named_route_parameters(self):
        project_url = reverse("projects:project_detail", kwargs={"project_id": self.project.pk})
        user_url = reverse("users:profile", kwargs={"user_id": self.user.pk})
        self.assertEqual(self.project.get_absolute_url(), project_url)
        self.assertEqual(self.user.get_absolute_url(), user_url)
        self.assertEqual(resolve(project_url).kwargs, {"project_id": self.project.pk})
        self.assertEqual(resolve(user_url).kwargs, {"user_id": self.user.pk})

    def test_empty_get_forms_do_not_create_records(self):
        for url in ["/users/register/", "/users/login/"]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context["form"].is_bound)
        self.client.force_login(self.user)
        for url in [
            "/projects/create-project/",
            f"/projects/{self.project.pk}/edit/",
            "/users/edit-profile/",
            "/users/change-password/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context["form"].is_bound)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(Project.objects.count(), 1)

    def test_login_uses_central_settings_redirect(self):
        with override_settings(LOGIN_URL="/custom-login/"):
            response = self.client.get("/projects/create-project/")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/custom-login/?next="))
            response = self.client.post(f"/projects/{self.project.pk}/skills/add/")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/custom-login/?next="))

    def test_avatar_reset_uses_standard_clear_widget(self):
        form = ProfileForm(instance=self.user)
        self.assertNotIn("sbros_avy", form.fields)
        self.client.force_login(self.user)
        response = self.client.get("/users/edit-profile/")
        self.assertContains(response, 'name="avatar-clear"')
        self.assertContains(response, 'id="avatar-clear_id"')
        response = self.client.post(
            "/users/edit-profile/", self.profile_data(**{"avatar-clear": "on"}, name="Яна")
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar_url, "")
        with self.user.avatar.open("rb") as avatar:
            self.assertEqual(avatar.read(), create_avatar("Яна", self.user.email).read())

    def test_invalid_profile_does_not_reset_existing_avatar(self):
        self.client.force_login(self.user)
        old_name = self.user.avatar.name
        response = self.client.post(
            "/users/edit-profile/", self.profile_data(**{"avatar-clear": "on"}, phone="invalid")
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar.name, old_name)
        self.assertTrue(self.user.avatar.storage.exists(old_name))

    def test_existing_skill_name_is_reused_without_duplicates(self):
        skill = Skill.objects.create(name="Python")
        self.client.force_login(self.user)
        url = f"/projects/{self.project.pk}/skills/add/"
        for name in ["Python", "PYTHON", " Python "]:
            with self.subTest(name=name):
                response = self.client.post(
                    url, json.dumps({"name": name}), content_type="application/json"
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["skill_id"], skill.pk)
                self.assertFalse(response.json()["created"])
        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(self.project.skills.count(), 1)
