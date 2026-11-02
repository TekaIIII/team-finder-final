from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse

from common.constants import (
    ABOUT_MAX_LENGTH,
    AVATAR_PATH_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PERSON_NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    URL_MAX_LENGTH,
)

from .avatars import create_avatar
from .constants import DEFAULT_AVATAR_PREFIX
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Электронная почта", unique=True, max_length=EMAIL_MAX_LENGTH)
    name = models.CharField("Имя", max_length=PERSON_NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=PERSON_NAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/", max_length=AVATAR_PATH_MAX_LENGTH)
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField("Ссылка на GitHub", blank=True, max_length=URL_MAX_LENGTH)
    about = models.TextField("О себе", max_length=ABOUT_MAX_LENGTH, blank=True)
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

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()

        if not self.phone:
            self.phone = None

        if not self.avatar:
            self.generate_avatar()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"user_id": self.pk})

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def get_short_name(self):
        return self.name

    @property
    def avatar_url(self):
        if not self.avatar:
            return ""

        filename = self.avatar.name.rsplit("/", 1)[-1]

        # Стандартный аватар показываем текстовой буквой.
        if filename.startswith(DEFAULT_AVATAR_PREFIX):
            return ""

        # Удалённую картинку не отправляем в браузер.
        if not self.avatar.storage.exists(self.avatar.name):
            return ""

        return self.avatar.url

    def generate_avatar(self):
        filename = f"{DEFAULT_AVATAR_PREFIX}{uuid4().hex}.png"
        self.avatar.save(
            filename,
            create_avatar(self.name, self.email),
            save=False,
        )
