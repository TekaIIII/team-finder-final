from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Необходимо указать email.")
        if not extra_fields.get("name"):
            raise ValueError("Необходимо указать имя.")
        if not extra_fields.get("surname"):
            raise ValueError("Необходимо указать фамилию.")

        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Для суперпользователя is_staff должен быть True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Для суперпользователя is_superuser должен быть True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Суперпользователь должен быть активным.")

        return self.create_user(email, password, **extra_fields)
