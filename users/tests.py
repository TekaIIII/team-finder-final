import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from PIL import Image, ImageChops

from projects.forms import ProjectForm

from .admin import AdminUserCreationForm
from .avatars import create_avatar
from .forms import ProfileForm


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class UserTests(TestCase):
    def setUp(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory)

        settings_override = override_settings(MEDIA_ROOT=directory)
        settings_override.enable()
        self.addCleanup(settings_override.disable)

        self.password = "ProverkaAccount!975"
        self.user = get_user_model().objects.create_user(
            "anna@example.com",
            self.password,
            name="Анна",
            surname="Тест",
        )

    def profile_data(self, **kwargs):
        data = {
            "name": "Анна",
            "surname": "Тест",
            "email": self.user.email,
            "phone": "89001234567",
            "about": "Описание профиля",
            "github_url": "",
        }
        data.update(kwargs)
        return data

    def test_avatar_is_reproducible(self):
        first_avatar = create_avatar("Анна", "anna@example.com").read()
        second_avatar = create_avatar("Анна", "ANNA@EXAMPLE.COM").read()

        self.assertEqual(first_avatar, second_avatar)
        self.assertTrue(first_avatar.startswith(b"\x89PNG"))

    def test_phone_formats_are_equivalent(self):
        other_user = get_user_model().objects.create_user(
            "ivan@example.com",
            self.password,
            name="Иван",
            surname="Тест",
            phone="89001234567",
        )

        form = ProfileForm(
            self.profile_data(phone="+79001234567"),
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

        other_user.phone = None
        other_user.save()

        form = ProfileForm(self.profile_data(), instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["phone"], "+79001234567")

    def test_forms_validate_github_consistently(self):
        for url in [
            "https://example.com",
            "https://github.com.evil.example/x",
        ]:
            with self.subTest(url=url):
                form = ProfileForm(
                    self.profile_data(github_url=url),
                    instance=self.user,
                )
                self.assertFalse(form.is_valid())
                self.assertIn("github_url", form.errors)

                project_form = ProjectForm(
                    {
                        "name": "Тест",
                        "status": "open",
                        "github_url": url,
                    }
                )
                self.assertFalse(project_form.is_valid())
                self.assertIn("github_url", project_form.errors)

    def test_admin_rejects_case_insensitive_duplicate_email(self):
        form = AdminUserCreationForm(
            {
                "email": self.user.email.upper(),
                "name": "Иван",
                "surname": "Новый",
                "password1": self.password,
                "password2": self.password,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_edit_profile_always_updates_current_user(self):
        other_user = get_user_model().objects.create_user(
            "other@example.com",
            self.password,
            name="Иван",
            surname="Петров",
        )

        self.client.force_login(self.user)
        response = self.client.post(
            "/users/edit-profile/",
            self.profile_data(
                id=other_user.pk,
                surname="Изменена",
                is_staff=True,
            ),
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        other_user.refresh_from_db()

        self.assertEqual(self.user.surname, "Изменена")
        self.assertFalse(self.user.is_staff)
        self.assertEqual(other_user.surname, "Петров")

    def test_login_after_email_change(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/users/edit-profile/",
            self.profile_data(email="NEW@EXAMPLE.COM"),
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

        self.client.logout()

        self.assertTrue(
            self.client.login(
                email="new@example.com",
                password=self.password,
            )
        )
        self.assertFalse(
            self.client.login(
                email="anna@example.com",
                password=self.password,
            )
        )

    def test_cannot_use_another_users_email(self):
        get_user_model().objects.create_user(
            "other@example.com",
            self.password,
            name="Иван",
            surname="Тест",
        )

        self.client.force_login(self.user)
        response = self.client.post(
            "/users/edit-profile/",
            self.profile_data(email="OTHER@EXAMPLE.COM"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "anna@example.com")

    def test_cyrillic_letters_are_distinct(self):
        first_avatar = Image.open(BytesIO(create_avatar("Анна", "test@example.com").read()))
        second_avatar = Image.open(BytesIO(create_avatar("Яна", "test@example.com").read()))

        self.assertIsNotNone(ImageChops.difference(first_avatar, second_avatar).getbbox())

    def test_avatar_upload_changes_url(self):
        self.client.force_login(self.user)
        urls = []

        for color in ["blue", "red"]:
            buffer = BytesIO()
            Image.new("RGB", (20, 20), color=color).save(
                buffer,
                format="PNG",
            )

            uploaded_file = SimpleUploadedFile(
                "avatar.png",
                buffer.getvalue(),
                content_type="image/png",
            )
            response = self.client.post(
                "/users/edit-profile/",
                self.profile_data(avatar=uploaded_file),
                follow=True,
            )

            self.assertEqual(response.status_code, 200)

            self.user.refresh_from_db()
            self.assertContains(response, self.user.avatar.url)

            with self.user.avatar.open("rb") as avatar:
                self.assertEqual(
                    Image.open(avatar).getpixel((0, 0)),
                    Image.new("RGB", (1, 1), color).getpixel((0, 0)),
                )

            urls.append(self.user.avatar.url)

        self.assertNotEqual(urls[0], urls[1])

    def test_avatar_can_be_reset_to_initial(self):
        self.client.force_login(self.user)
        old_avatar_name = self.user.avatar.name

        response = self.client.post(
            "/users/edit-profile/",
            self.profile_data(**{"avatar-clear": "on"}, name="Яна"),
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.avatar.name, old_avatar_name)

        with self.user.avatar.open("rb") as avatar:
            self.assertEqual(
                avatar.read(),
                create_avatar("Яна", self.user.email).read(),
            )

    def test_missing_avatar_is_rendered_as_initial(self):
        self.user.avatar = ""

        html = render_to_string(
            "includes/avatar.html",
            {"avatar_user": self.user, "avatar_class": "avatar"},
        )

        self.assertInHTML(
            '<span class="buk-ava-letter" aria-hidden="true">А</span>',
            html,
        )
        self.assertNotIn("src=", html)

        self.user.avatar = "avatars/missing.png"

        html = render_to_string(
            "includes/avatar.html",
            {"avatar_user": self.user, "avatar_class": "avatar"},
        )

        self.assertInHTML(
            '<span class="buk-ava-letter" aria-hidden="true">А</span>',
            html,
        )
        self.assertNotIn("src=", html)
        self.assertIn('class="buk-ava-img"', html)
