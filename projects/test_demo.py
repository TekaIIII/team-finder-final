import shutil
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import Resolver404, resolve, reverse

from .management.commands.seed_demo import DEMO_PASSWORD, DEMO_USERS
from .models import Project


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DemoTests(TestCase):
    def setUp(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory)
        settings_override = override_settings(MEDIA_ROOT=directory)
        settings_override.enable()
        self.addCleanup(settings_override.disable)

    def test_demo_is_repeatable_and_preserves_existing_data(self):
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(get_user_model().objects.count(), 3)
        self.assertEqual(Project.objects.count(), 3)
        for url, *_ in DEMO_USERS:
            user = get_user_model().objects.get(email=url)
            self.assertTrue(user.check_password(DEMO_PASSWORD))
            self.assertFalse(user.is_staff)
            project = user.owned_projects.get()
            self.assertIn(user, project.participants.all())
            self.assertTrue(project.skills.exists())
            self.assertTrue(user.avatar.storage.exists(user.avatar.name))
        user.set_password("ChangedDemoPassword!2026")
        user.save()
        project.description = "Новое описание"
        project.save()
        call_command("seed_demo", stdout=StringIO())
        user.refresh_from_db()
        project.refresh_from_db()
        self.assertEqual(get_user_model().objects.count(), 3)
        self.assertEqual(Project.objects.count(), 3)
        self.assertTrue(user.check_password("ChangedDemoPassword!2026"))
        self.assertEqual(project.description, "Новое описание")

    def test_project_list_preserves_filter(self):
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(reverse("projects:project_list"), "/project/list/")
        with self.assertRaises(Resolver404):
            resolve("/projects/list/")
        response = self.client.get("/project/list/", {"skill": "Python"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_skill"], "Python")
        self.assertEqual(response.context["page_obj"].paginator.count, 2)
