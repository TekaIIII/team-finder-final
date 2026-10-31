import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError


def github_adres(adr):
    """Проверяет сайт назначения уже разобранной URL-формой ссылки."""
    if not adr:
        return
    razbor = urlsplit(adr)
    if razbor.scheme not in ("http", "https") or razbor.hostname != "github.com":
        raise ValidationError("Укажите ссылку на https://github.com/.")


def norm_tel(nom):
    """Приводит разрешённые форматы российского номера к +7."""
    if not isinstance(nom, str) or not re.fullmatch(r"(8[0-9]{10}|\+7[0-9]{10})", nom):
        raise ValidationError("Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
    return "+7" + nom[-10:]
