from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Основные настройки.
SECRET_KEY = config("DJANGO_SECRET_KEY")

DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Подключённые приложения.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "skills.apps.SkillsConfig",
    "projects.apps.ProjectsConfig",
]


# Собственная модель пользователя.
AUTH_USER_MODEL = "users.User"


# Промежуточные обработчики запросов и ответов.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Основной файл маршрутов.
ROOT_URLCONF = "team_finder.urls"


# Настройки шаблонов.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / f"templates_var{config('TASK_VERSION', default='3')}"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "team_finder.wsgi.application"


# Подключение к PostgreSQL.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default=5432, cast=int),
    }
}


# Проверки паролей.
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": ("django.contrib.auth.password_validation.UserAttributeSimilarityValidator"),
        "OPTIONS": {
            "user_attributes": [
                "name",
                "surname",
                "email",
            ],
        },
    },
    {
        "NAME": ("django.contrib.auth.password_validation.MinimumLengthValidator"),
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": ("django.contrib.auth.password_validation.CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation.NumericPasswordValidator"),
    },
]


# Язык и часовой пояс.
LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Статические файлы.
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Файлы, загружаемые пользователями.
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# Тип автоматически создаваемого первичного ключа.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
