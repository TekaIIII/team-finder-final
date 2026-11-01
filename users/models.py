from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .avatars import sdelat_avu


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **dop):
        if not email:
            raise ValueError("Необходимо указать email.")
        if not dop.get("name"):
            raise ValueError("Необходимо указать имя.")
        if not dop.get("surname"):
            raise ValueError("Необходимо указать фамилию.")

        email = self.normalize_email(email).strip().lower()
        usr = self.model(email=email, **dop)
        usr.set_password(password)
        usr.save(using=self._db)
        return usr

    def create_superuser(self, email, password=None, **dop):
        dop.setdefault("is_staff", True)
        dop.setdefault("is_superuser", True)
        dop.setdefault("is_active", True)

        if dop.get("is_staff") is not True:
            raise ValueError("Для суперпользователя is_staff должен быть True.")
        if dop.get("is_superuser") is not True:
            raise ValueError("Для суперпользователя is_superuser должен быть True.")
        if dop.get("is_active") is not True:
            raise ValueError("Суперпользователь должен быть активным.")

        return self.create_user(email, password, **dop)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Электронная почта", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField(
        "Телефон",
        max_length=12,
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    about = models.TextField("О себе", max_length=256, blank=True)
    is_active = models.BooleanField("Активный пользователь", default=True)
    is_staff = models.BooleanField("Доступ к админ-панели", default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def get_short_name(self):
        return self.name

    @property
    def ssylka_avy(self):
        if not self.avatar:
            return ""

        imya_fayla = self.avatar.name.rsplit("/", 1)[-1]

        # Стандартный аватар показываем текстовой буквой.
        if imya_fayla.startswith("bukva_"):
            return ""

        # Удалённую картинку не отправляем в браузер.
        if not self.avatar.storage.exists(self.avatar.name):
            return ""

        return self.avatar.url

    def dobavit_avu(self):
        imya_fayla = f"bukva_{uuid4().hex}.png"
        self.avatar.save(
            imya_fayla,
            sdelat_avu(self.name, self.email),
            save=False,
        )

    def save(self, *poz, **dop):
        self.email = self.email.strip().lower()

        if not self.phone:
            self.phone = None

        if not self.avatar:
            self.dobavit_avu()

        super().save(*poz, **dop)