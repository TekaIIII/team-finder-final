from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from common.constants import PROJECT_OPEN
from projects.models import Project
from skills.models import Skill

DEMO_PASSWORD = "TeamFinderDemo!2026"
DEMO_USERS = (
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
        created_users = 0
        created_projects = 0
        for email, name, surname, name, description, skills in DEMO_USERS:
            user, created = get_user_model().objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "surname": surname,
                    "about": "Учебный аккаунт для знакомства с TeamFinder.",
                    "password": make_password(DEMO_PASSWORD),
                },
            )
            if created:
                created_users += 1
            project, project_created = Project.objects.get_or_create(
                owner=user,
                name=name,
                defaults={"description": description, "status": PROJECT_OPEN},
            )
            if project_created:
                created_projects += 1
                project.participants.add(user)
                for skill_name in skills:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    project.skills.add(skill)
        self.stdout.write(
            self.style.SUCCESS(
                f"Добавлено пользователей: {created_users}, проектов: {created_projects}. "
                "Существующие записи и пароли не изменены."
            )
        )
