from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.validators import normalize_phone


def validate_unique_email(email, user_id=None):
    email = email.strip().lower()
    users = get_user_model().objects.filter(email__iexact=email)
    if users.exclude(pk=user_id).exists():
        raise ValidationError("Этот email уже зарегистрирован.")
    return email


def validate_unique_phone(phone, user_id=None):
    phone = normalize_phone(phone)
    phone_with_eight = "8" + phone[-10:]
    users = get_user_model().objects.filter(phone__in=[phone, phone_with_eight])
    if users.exclude(pk=user_id).exists():
        raise ValidationError("Этот телефон уже используется.")
    return phone
