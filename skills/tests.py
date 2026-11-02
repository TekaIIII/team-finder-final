import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from projects.models import Project

from .models import Skill


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class SkillTests(TestCase):
    def setUp(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory)
        settings_override = override_settings(MEDIA_ROOT=directory)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.user = get_user_model().objects.create_user(
            "owner@example.com",
            "ProverkaAccount!975",
            name="Анна",
            surname="Тест",
        )
        self.project = Project.objects.create(name="Проверка навыков", owner=self.user)
        self.url = f"/projects/{self.project.pk}/skills/add/"

    def test_suggestions_are_sorted_and_limited(self):
        Skill.objects.bulk_create([Skill(name=f"Tech {number:02}") for number in range(14)])
        Skill.objects.create(name="Other Tech")
        data = self.client.get("/projects/skills/?q=tech").json()
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0]["name"], "Tech 00")
        self.assertEqual(data[-1]["name"], "Tech 09")
        self.assertEqual(set(data[0]), {"id", "name"})

    def test_invalid_input_does_not_create_skill(self):
        self.client.force_login(self.user)
        for data in [
            {},
            [],
            {"name": " "},
            {"name": "x" * 125},
            {"skill_id": 99999},
        ]:
            with self.subTest(data=data):
                response = self.client.post(
                    self.url, json.dumps(data), content_type="application/json"
                )
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Skill.objects.count(), 0)

    def test_post_requires_csrf_and_preserves_response_format(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.get(self.url).status_code, 405)
        self.assertEqual(client.post(self.url).status_code, 403)
        client.get(f"/projects/{self.project.pk}/")
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.url,
            json.dumps({"name": "Django"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"id", "skill_id", "name", "created", "added"})
        self.assertTrue(self.project.skills.filter(name="Django").exists())
