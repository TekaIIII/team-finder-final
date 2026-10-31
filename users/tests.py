import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from projects.forms import ProjectForm

from .admin import AdminUserCreationForm
from .avatars import sdelat_avu
from .forms import ProfileForm


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class PolzProverki(TestCase):
    def setUp(self):
        papka = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, papka)
        nstr = override_settings(MEDIA_ROOT=papka)
        nstr.enable()
        self.addCleanup(nstr.disable)
        self.par = "ProverkaAccount!975"
        self.usr = get_user_model().objects.create_user(
            "anna@example.com", self.par, name="Анна", surname="Тест"
        )

    def dannye(self, **dop):
        d = {
            "name": "Анна",
            "surname": "Тест",
            "email": self.usr.email,
            "phone": "89001234567",
            "about": "Описание профиля",
            "github_url": "",
        }
        d.update(dop)
        return d

    def test_ava_vosproizvodima(self):
        perv = sdelat_avu("Анна", "anna@example.com").read()
        vtor = sdelat_avu("Анна", "ANNA@EXAMPLE.COM").read()
        self.assertEqual(perv, vtor)
        self.assertTrue(perv.startswith(b"\x89PNG"))

    def test_tel_s_vosmerki_sovpadaet_s_plus_sem(self):
        drug = get_user_model().objects.create_user(
            "ivan@example.com",
            self.par,
            name="Иван",
            surname="Тест",
            phone="89001234567",
        )
        frm = ProfileForm(self.dannye(phone="+79001234567"), instance=self.usr)
        self.assertFalse(frm.is_valid())
        self.assertIn("phone", frm.errors)
        drug.phone = None
        drug.save()
        frm = ProfileForm(self.dannye(), instance=self.usr)
        self.assertTrue(frm.is_valid(), frm.errors)
        self.assertEqual(frm.cleaned_data["phone"], "+79001234567")

    def test_github_odinakovo_proveryaetsya_v_formah(self):
        for adr in [
            "https://example.com",
            "https://github.com.evil.example/x",
        ]:
            with self.subTest(adr=adr):
                frm = ProfileForm(self.dannye(github_url=adr), instance=self.usr)
                self.assertFalse(frm.is_valid())
                self.assertIn("github_url", frm.errors)
                pr_frm = ProjectForm({"name": "Тест", "status": "open", "github_url": adr})
                self.assertFalse(pr_frm.is_valid())
                self.assertIn("github_url", pr_frm.errors)

    def test_admin_ne_prinimaet_povtor_pochty_drugim_registrom(self):
        frm = AdminUserCreationForm(
            {
                "email": self.usr.email.upper(),
                "name": "Иван",
                "surname": "Новый",
                "password1": self.par,
                "password2": self.par,
            }
        )
        self.assertFalse(frm.is_valid())
        self.assertIn("email", frm.errors)

    def test_pravka_vsegda_otnositsya_k_tekushchemu_polz(self):
        drug = get_user_model().objects.create_user(
            "other@example.com", self.par, name="Иван", surname="Петров"
        )
        self.client.force_login(self.usr)
        otv = self.client.post(
            "/users/edit-profile/",
            self.dannye(id=drug.pk, surname="Изменена", is_staff=True),
        )
        self.assertEqual(otv.status_code, 302)
        self.usr.refresh_from_db()
        drug.refresh_from_db()
        self.assertEqual(self.usr.surname, "Изменена")
        self.assertFalse(self.usr.is_staff)
        self.assertEqual(drug.surname, "Петров")

    def test_smena_pochty_i_vhod_s_novoy(self):
        self.client.force_login(self.usr)
        otv = self.client.post("/users/edit-profile/", self.dannye(email="NEW@EXAMPLE.COM"))
        self.assertEqual(otv.status_code, 302)
        self.usr.refresh_from_db()
        self.assertEqual(self.usr.email, "new@example.com")
        self.client.logout()
        self.assertTrue(self.client.login(email="new@example.com", password=self.par))
        self.assertFalse(self.client.login(email="anna@example.com", password=self.par))

    def test_pochta_chuzhogo_profilya_ne_podhodit(self):
        get_user_model().objects.create_user(
            "other@example.com", self.par, name="Иван", surname="Тест"
        )
        self.client.force_login(self.usr)
        otv = self.client.post("/users/edit-profile/", self.dannye(email="OTHER@EXAMPLE.COM"))
        self.assertEqual(otv.status_code, 200)
        self.assertIn("email", otv.context["form"].errors)
        self.usr.refresh_from_db()
        self.assertEqual(self.usr.email, "anna@example.com")
