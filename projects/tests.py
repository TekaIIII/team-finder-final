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
        papka = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, papka)
        nastroika = override_settings(MEDIA_ROOT=papka)
        nastroika.enable()
        self.addCleanup(nastroika.disable)
        self.par = "TestPassword!482"
        self.avt = User.objects.create_user(
            email="owner@example.com",
            password=self.par,
            name="Анна",
            surname="Иванова",
        )
        self.drug = User.objects.create_user(
            email="other@example.com",
            password=self.par,
            name="Иван",
            surname="Петров",
        )
        self.pr = Project.objects.create(name="Учебный проект", owner=self.avt)
        self.pr.participants.add(self.avt)
        self.nav = Skill.objects.create(name="Python")

    def test_otkrytye_stranicy(self):
        puti = [
            "/project/list/",
            "/users/list/",
            f"/projects/{self.pr.pk}/",
            f"/users/{self.avt.pk}/",
        ]
        for put in puti:
            with self.subTest(path=put):
                otv = self.client.get(put)
                self.assertEqual(otv.status_code, 200)

    def test_gost_ne_sozdaet_proekt(self):
        otv = self.client.post(
            "/projects/create-project/",
            {"name": "Проект гостя", "status": "open"},
        )
        self.assertEqual(otv.status_code, 302)
        self.assertTrue(otv.url.startswith("/users/login/"))
        self.assertFalse(Project.objects.filter(name="Проект гостя").exists())

    def test_avtor_dobavlyaetsya_v_komandu(self):
        self.client.force_login(self.avt)
        otv = self.client.post(
            "/projects/create-project/",
            {"name": "Новый проект", "status": "open", "owner": self.drug.pk},
        )
        self.assertEqual(otv.status_code, 302)
        pr = Project.objects.get(name="Новый проект")
        self.assertEqual(pr.owner, self.avt)
        self.assertTrue(pr.participants.filter(pk=self.avt.pk).exists())

    def test_chuzhaya_pravka_zapreshchena(self):
        self.client.force_login(self.drug)
        put = f"/projects/{self.pr.pk}/edit/"
        self.assertEqual(self.client.get(put).status_code, 403)
        otv = self.client.post(put, {"name": "Чужое изменение", "status": "closed"})
        self.assertEqual(otv.status_code, 403)
        self.pr.refresh_from_db()
        self.assertEqual(self.pr.name, "Учебный проект")
        self.assertEqual(self.pr.status, "open")

    def test_vstuplenie_i_vyhod(self):
        self.client.force_login(self.drug)
        put = f"/projects/{self.pr.pk}/toggle-participate/"
        otv = self.client.post(put)
        self.assertTrue(otv.json()["participant"])
        self.assertTrue(self.pr.participants.filter(pk=self.drug.pk).exists())
        otv = self.client.post(put)
        self.assertFalse(otv.json()["participant"])
        self.assertFalse(self.pr.participants.filter(pk=self.drug.pk).exists())

    def test_zavershaet_tolko_avtor(self):
        put = f"/projects/{self.pr.pk}/complete/"
        self.client.force_login(self.drug)
        self.assertEqual(self.client.post(put).status_code, 403)
        self.client.force_login(self.avt)
        self.assertEqual(self.client.post(put).status_code, 200)
        self.pr.refresh_from_db()
        self.assertEqual(self.pr.status, "closed")

    def test_zakrytyy_nabor(self):
        self.pr.status = "closed"
        self.pr.save()
        self.client.force_login(self.drug)
        otv = self.client.post(f"/projects/{self.pr.pk}/toggle-participate/")
        self.assertEqual(otv.status_code, 409)
        self.assertFalse(self.pr.participants.filter(pk=self.drug.pk).exists())

    def test_nav_ne_dubliruetsya(self):
        self.client.force_login(self.avt)
        put = f"/projects/{self.pr.pk}/skills/add/"
        telo = json.dumps({"skill_id": self.nav.pk})
        otv = self.client.post(put, telo, content_type="application/json")
        self.assertTrue(otv.json()["added"])
        otv = self.client.post(put, telo, content_type="application/json")
        self.assertFalse(otv.json()["added"])
        self.assertEqual(self.pr.skills.count(), 1)

    def test_udalenie_tolko_svyazi_nav(self):
        self.pr.skills.add(self.nav)
        put = f"/projects/{self.pr.pk}/skills/{self.nav.pk}/remove/"
        self.client.force_login(self.drug)
        self.assertEqual(self.client.post(put).status_code, 403)
        self.assertTrue(self.pr.skills.filter(pk=self.nav.pk).exists())
        self.client.force_login(self.avt)
        self.assertEqual(self.client.post(put).status_code, 200)
        self.assertFalse(self.pr.skills.filter(pk=self.nav.pk).exists())
        self.assertTrue(Skill.objects.filter(pk=self.nav.pk).exists())

    def test_stranicy_s_filtrom(self):
        self.pr.skills.add(self.nav)
        for nom in range(12):
            pr = Project.objects.create(name=f"Проект {nom}", owner=self.avt)
            pr.skills.add(self.nav)
        otv = self.client.get("/project/list/?skill=Python")
        self.assertEqual(len(otv.context["page_obj"]), 12)
        self.assertEqual(otv.context["page_obj"].paginator.count, 13)
        otv = self.client.get("/project/list/?skill=Python&page=2")
        self.assertEqual(len(otv.context["page_obj"]), 1)
        self.assertEqual(otv.context["active_skill"], "Python")

    def test_registraciya_i_avatar(self):
        otv = self.client.post(
            "/users/register/",
            {
                "name": "Мария",
                "surname": "Соколова",
                "email": "NEW@example.com",
                "password": self.par,
            },
        )
        self.assertEqual(otv.status_code, 302)
        usr = User.objects.get(email="new@example.com")
        self.assertTrue(usr.check_password(self.par))
        self.assertNotEqual(usr.password, self.par)
        self.assertTrue(usr.avatar.storage.exists(usr.avatar.name))

    def test_smena_parolya_bez_vyhoda(self):
        self.client.force_login(self.avt)
        nov_par = "AnotherPassword!975"
        otv = self.client.post(
            "/users/change-password/",
            {
                "old_password": self.par,
                "new_password1": nov_par,
                "new_password2": nov_par,
            },
        )
        self.assertEqual(otv.status_code, 302)
        self.avt.refresh_from_db()
        self.assertTrue(self.avt.check_password(nov_par))
        self.assertFalse(self.avt.check_password(self.par))
        otv = self.client.get("/project/list/")
        self.assertEqual(otv.wsgi_request.user.pk, self.avt.pk)
