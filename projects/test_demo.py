import shutil
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import Resolver404, resolve, reverse

from .management.commands.seed_demo import DEMO_PAROL, PRIMERY
from .models import Project


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DemoProverki(TestCase):
    def setUp(self):
        papka = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, papka)
        nstr = override_settings(MEDIA_ROOT=papka)
        nstr.enable()
        self.addCleanup(nstr.disable)

    def test_demo_zagruzhaetsya_i_ne_perezapisyvaet_dannye(self):
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(get_user_model().objects.count(), 3)
        self.assertEqual(Project.objects.count(), 3)
        for adr, *_ in PRIMERY:
            usr = get_user_model().objects.get(email=adr)
            self.assertTrue(usr.check_password(DEMO_PAROL))
            self.assertFalse(usr.is_staff)
            pr = usr.owned_projects.get()
            self.assertIn(usr, pr.participants.all())
            self.assertTrue(pr.skills.exists())
            self.assertTrue(usr.avatar.storage.exists(usr.avatar.name))
        usr.set_password("ChangedDemoPassword!2026")
        usr.save()
        pr.description = "Новое описание"
        pr.save()
        call_command("seed_demo", stdout=StringIO())
        usr.refresh_from_db()
        pr.refresh_from_db()
        self.assertEqual(get_user_model().objects.count(), 3)
        self.assertEqual(Project.objects.count(), 3)
        self.assertTrue(usr.check_password("ChangedDemoPassword!2026"))
        self.assertEqual(pr.description, "Новое описание")

    def test_adres_spiska_sohranyaet_filtr(self):
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(reverse("projects:project_list"), "/project/list/")
        with self.assertRaises(Resolver404):
            resolve("/projects/list/")
        otv = self.client.get("/project/list/", {"skill": "Python"})
        self.assertEqual(otv.status_code, 200)
        self.assertEqual(otv.context["active_skill"], "Python")
        self.assertEqual(otv.context["page_obj"].paginator.count, 2)
