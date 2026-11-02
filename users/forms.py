from pathlib import Path
from uuid import uuid4

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from common.constants import PASSWORD_MIN_LENGTH, URL_MAX_LENGTH
from common.validators import validate_github_url

from .models import User
from .validators import validate_unique_email, validate_unique_phone


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        min_length=PASSWORD_MIN_LENGTH,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def clean_email(self):
        return validate_unique_email(self.cleaned_data["email"], self.instance.pk)

    def clean_password(self):
        password = self.cleaned_data["password"]
        candidate = User(
            email=self.cleaned_data.get("email", ""),
            name=self.cleaned_data.get("name", ""),
            surname=self.cleaned_data.get("surname", ""),
        )
        validate_password(password, user=candidate)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user = authenticate(
                request=self.request,
                email=email.strip().lower(),
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data


class AvatarInput(forms.ClearableFileInput):
    template_name = "users/widgets/avatar_input.html"
    clear_checkbox_label = "Использовать букву имени"


class ProfileForm(forms.ModelForm):
    github_url = forms.URLField(
        label="Ссылка на GitHub",
        max_length=URL_MAX_LENGTH,
        required=False,
        assume_scheme="https",
        validators=[validate_github_url],
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "avatar", "about", "phone", "github_url")
        widgets = {
            "avatar": AvatarInput(attrs={"accept": "image/*"}),
            "phone": forms.TextInput(attrs={"placeholder": "+79001234567"}),
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True
        self.fields["avatar"].required = False
        self.fields["avatar"].widget.is_required = False
        self.clear_avatar = False

    def clean_email(self):
        return validate_unique_email(self.cleaned_data["email"], self.instance.pk)

    def clean_phone(self):
        return validate_unique_phone(self.cleaned_data["phone"], self.instance.pk)

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar is False:
            self.clear_avatar = True
            return self.instance.avatar
        if self.files.get("avatar") and avatar:
            extension = Path(avatar.name).suffix.lower()
            avatar.name = f"{uuid4().hex}{extension}"
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.clear_avatar:
            user.generate_avatar()
        if commit:
            user.save()
            self.save_m2m()
        return user
