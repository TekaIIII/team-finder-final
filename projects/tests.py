import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from projects.models import Project
from skills.models import Skill

User = get_user_model()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class TeamFinderTests(TestCase):
    def setUp(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory)
        settings_override = override_settings(MEDIA_ROOT=directory)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.password = "TestPassword!482"
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password=self.password,
            name="Анна",
            surname="Иванова",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password=self.password,
            name="Иван",
            surname="Петров",
        )
        self.project = Project.objects.create(name="Учебный проект", owner=self.owner)
        self.project.participants.add(self.owner)
        self.skill = Skill.objects.create(name="Python")

    def test_public_pages(self):
        urls = [
            "/project/list/",
            "/users/list/",
            f"/projects/{self.project.pk}/",
            f"/users/{self.owner.pk}/",
        ]
        for url in urls:
            with self.subTest(path=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_guest_cannot_create_project(self):
        response = self.client.post(
            "/projects/create-project/",
            {"name": "Проект гостя", "status": "open"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/users/login/"))
        self.assertFalse(Project.objects.filter(name="Проект гостя").exists())

    def test_owner_is_added_to_team(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            "/projects/create-project/",
            {"name": "Новый проект", "status": "open", "owner": self.other_user.pk},
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="Новый проект")
        self.assertEqual(project.owner, self.owner)
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_other_user_cannot_edit_project(self):
        self.client.force_login(self.other_user)
        url = f"/projects/{self.project.pk}/edit/"
        self.assertEqual(self.client.get(url).status_code, 403)
        response = self.client.post(url, {"name": "Чужое изменение", "status": "closed"})
        self.assertEqual(response.status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Учебный проект")
        self.assertEqual(self.project.status, "open")

    def test_join_and_leave_project(self):
        self.client.force_login(self.other_user)
        url = f"/projects/{self.project.pk}/toggle-participate/"
        response = self.client.post(url)
        self.assertTrue(response.json()["participant"])
        self.assertTrue(self.project.participants.filter(pk=self.other_user.pk).exists())
        response = self.client.post(url)
        self.assertFalse(response.json()["participant"])
        self.assertFalse(self.project.participants.filter(pk=self.other_user.pk).exists())

    def test_only_owner_can_complete_project(self):
        url = f"/projects/{self.project.pk}/complete/"
        self.client.force_login(self.other_user)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

    def test_cannot_join_closed_project(self):
        self.project.status = "closed"
        self.project.save()
        self.client.force_login(self.other_user)
        response = self.client.post(f"/projects/{self.project.pk}/toggle-participate/")
        self.assertEqual(response.status_code, 409)
        self.assertFalse(self.project.participants.filter(pk=self.other_user.pk).exists())

    def test_project_skill_is_not_duplicated(self):
        self.client.force_login(self.owner)
        url = f"/projects/{self.project.pk}/skills/add/"
        body = json.dumps({"skill_id": self.skill.pk})
        response = self.client.post(url, body, content_type="application/json")
        self.assertTrue(response.json()["added"])
        response = self.client.post(url, body, content_type="application/json")
        self.assertFalse(response.json()["added"])
        self.assertEqual(self.project.skills.count(), 1)

    def test_remove_skill_keeps_dictionary_entry(self):
        self.project.skills.add(self.skill)
        url = f"/projects/{self.project.pk}/skills/{self.skill.pk}/remove/"
        self.client.force_login(self.other_user)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(self.project.skills.filter(pk=self.skill.pk).exists())
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertFalse(self.project.skills.filter(pk=self.skill.pk).exists())
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())

    def test_pagination_with_filter(self):
        self.project.skills.add(self.skill)
        for number in range(12):
            project = Project.objects.create(name=f"Проект {number}", owner=self.owner)
            project.skills.add(self.skill)
        response = self.client.get("/project/list/?skill=Python")
        self.assertEqual(len(response.context["page_obj"]), 12)
        self.assertEqual(response.context["page_obj"].paginator.count, 13)
        response = self.client.get("/project/list/?skill=Python&page=2")
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertEqual(response.context["active_skill"], "Python")

    def test_registration_and_avatar(self):
        response = self.client.post(
            "/users/register/",
            {
                "name": "Мария",
                "surname": "Соколова",
                "email": "NEW@example.com",
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.avatar.storage.exists(user.avatar.name))

    def test_password_change_keeps_session(self):
        self.client.force_login(self.owner)
        new_password = "AnotherPassword!975"
        response = self.client.post(
            "/users/change-password/",
            {
                "old_password": self.password,
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password(new_password))
        self.assertFalse(self.owner.check_password(self.password))
        response = self.client.get("/project/list/")
        self.assertEqual(response.wsgi_request.user.pk, self.owner.pk)
