from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project
from skills.models import Skill

DEMO_PAROL = "TeamFinderDemo!2026"
PRIMERY = (
    (
        "anna.demo@example.com",
        "Анна",
        "Иванова",
        "Планировщик учебных задач",
        "Хочу сделать приложение для записи заданий и отслеживания сроков. "
        "Ищу участников, которым интересны Django и работа с интерфейсом.",
        ("Python", "Django"),
    ),
    (
        "ivan.demo@example.com",
        "Иван",
        "Петров",
        "Карта интересных мест",
        "Собираю команду для сайта с местами для прогулок. "
        "Пользователи смогут добавлять свои маршруты и оставлять отзывы.",
        ("JavaScript", "HTML"),
    ),
    (
        "eva.demo@example.com",
        "Ева",
        "Соколова",
        "Каталог прочитанных книг",
        "Небольшой сервис со списком книг, оценками и заметками. "
        "Хочу попробовать совместную разработку и работу с базой данных.",
        ("Python", "PostgreSQL"),
    ),
)


class Command(BaseCommand):
    help = "Добавляет трёх демонстрационных пользователей с проектами."

    @transaction.atomic
    def handle(self, *args, **options):
        dob_polz = 0
        dob_pr = 0
        for adr, imya, fam, nazv, opis, navyki in PRIMERY:
            usr, nov = get_user_model().objects.get_or_create(
                email=adr,
                defaults={
                    "name": imya,
                    "surname": fam,
                    "about": "Учебный аккаунт для знакомства с TeamFinder.",
                    "password": make_password(DEMO_PAROL),
                },
            )
            if nov:
                dob_polz += 1
            pr, nov_pr = Project.objects.get_or_create(
                owner=usr,
                name=nazv,
                defaults={"description": opis, "status": "open"},
            )
            if nov_pr:
                dob_pr += 1
                pr.participants.add(usr)
                for imya_nav in navyki:
                    nav, _ = Skill.objects.get_or_create(name=imya_nav)
                    pr.skills.add(nav)
        self.stdout.write(
            self.style.SUCCESS(
                f"Добавлено пользователей: {dob_polz}, проектов: {dob_pr}. "
                "Существующие записи и пароли не изменены."
            )
        )
