from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = (("open", "Open"), ("closed", "Closed"))
    name = models.CharField("Название проекта", max_length=200)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    status = models.CharField("Статус", max_length=6, choices=STATUS_CHOICES, default="open")
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
