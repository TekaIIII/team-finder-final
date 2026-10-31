from django.db import models


class Skill(models.Model):
    name = models.CharField("Название навыка", max_length=124, unique=True)

    class Meta:
        verbose_name = "навык"
        verbose_name_plural = "навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name
