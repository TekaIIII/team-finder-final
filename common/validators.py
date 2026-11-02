import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError


def validate_github_url(url):
    """Проверяет, что ссылка ведёт на GitHub."""
    if not url:
        return
    parsed_url = urlsplit(url)
    if parsed_url.scheme not in ("http", "https") or parsed_url.hostname != "github.com":
        raise ValidationError("Укажите ссылку на https://github.com/.")


def normalize_phone(phone):
    """Приводит российский номер из двух допустимых форматов к +7."""
    if not isinstance(phone, str) or not re.fullmatch(r"(8[0-9]{10}|\+7[0-9]{10})", phone):
        raise ValidationError("Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
    return "+7" + phone[-10:]
