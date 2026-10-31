import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from projects.models import Project

from .models import Skill


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class NavProverki(TestCase):
    def setUp(self):
        papka = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, papka)
        nstr = override_settings(MEDIA_ROOT=papka)
        nstr.enable()
        self.addCleanup(nstr.disable)
        self.usr = get_user_model().objects.create_user(
            "owner@example.com",
            "ProverkaAccount!975",
            name="Анна",
            surname="Тест",
        )
        self.pr = Project.objects.create(name="Проверка навыков", owner=self.usr)
        self.put = f"/projects/{self.pr.pk}/skills/add/"

    def test_podskazki_ogranicheny_i_otsortirovany(self):
        Skill.objects.bulk_create([Skill(name=f"Tech {nom:02}") for nom in range(14)])
        Skill.objects.create(name="Other Tech")
        dann = self.client.get("/projects/skills/?q=tech").json()
        self.assertEqual(len(dann), 10)
        self.assertEqual(dann[0]["name"], "Tech 00")
        self.assertEqual(dann[-1]["name"], "Tech 09")
        self.assertEqual(set(dann[0]), {"id", "name"})

    def test_nevernye_dannye_ne_sozdayut_nav(self):
        self.client.force_login(self.usr)
        for d in [
            {},
            [],
            {"name": " "},
            {"name": "x" * 125},
            {"skill_id": 99999},
        ]:
            with self.subTest(d=d):
                otv = self.client.post(self.put, json.dumps(d), content_type="application/json")
                self.assertEqual(otv.status_code, 400)
        self.assertEqual(Skill.objects.count(), 0)

    def test_post_trebuet_csrf_i_sohranyaet_format_otveta(self):
        klient = Client(enforce_csrf_checks=True)
        klient.force_login(self.usr)
        self.assertEqual(klient.get(self.put).status_code, 405)
        self.assertEqual(klient.post(self.put).status_code, 403)
        klient.get(f"/projects/{self.pr.pk}/")
        token = klient.cookies["csrftoken"].value
        otv = klient.post(
            self.put,
            json.dumps({"name": "Django"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(otv.status_code, 200)
        self.assertEqual(set(otv.json()), {"id", "skill_id", "name", "created", "added"})
        self.assertTrue(self.pr.skills.filter(name="Django").exists())
