from django.db import models

from common.constants import SKILL_NAME_MAX_LENGTH


class Skill(models.Model):
    name = models.CharField("Название навыка", max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = "навык"
        verbose_name_plural = "навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name
