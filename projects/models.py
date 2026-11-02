from django.conf import settings
from django.db import models
from django.urls import reverse

from common.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_OPEN,
    PROJECT_STATUS_CHOICES,
    PROJECT_STATUS_MAX_LENGTH,
    URL_MAX_LENGTH,
)


class Project(models.Model):
    STATUS_CHOICES = PROJECT_STATUS_CHOICES
    name = models.CharField("Название проекта", max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True, max_length=URL_MAX_LENGTH)
    status = models.CharField(
        "Статус", max_length=PROJECT_STATUS_MAX_LENGTH, choices=STATUS_CHOICES, default=PROJECT_OPEN
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        verbose_name="Участники",
        blank=True,
    )
    skills = models.ManyToManyField(
        "skills.Skill",
        related_name="projects",
        verbose_name="Необходимые навыки",
        blank=True,
    )

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "проекты"
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"project_id": self.pk})
