from pathlib import Path
from uuid import uuid4

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from common.proverki import github_adres, norm_tel

from .models import User


def svobodnaya_pochta(adr, pk=None):
    adr = adr.strip().lower()
    if User.objects.filter(email__iexact=adr).exclude(pk=pk).exists():
        raise forms.ValidationError("Этот email уже зарегистрирован.")
    return adr


def svobodny_nom(nom, pk=None):
    nom = norm_tel(nom)
    nom_s_vosm = "8" + nom[-10:]
    polz = User.objects.filter(phone__in=[nom, nom_s_vosm])
    zanyat = polz.exclude(pk=pk).exists()
    if zanyat:
        raise forms.ValidationError("Этот телефон уже используется.")
    return nom


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        min_length=8,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def clean_email(self):
        return svobodnaya_pochta(self.cleaned_data["email"], self.instance.pk)

    def clean_password(self):
        par = self.cleaned_data["password"]
        kand = User(
            email=self.cleaned_data.get("email", ""),
            name=self.cleaned_data.get("name", ""),
            surname=self.cleaned_data.get("surname", ""),
        )
        validate_password(par, user=kand)
        return par

    def save(self, commit=True):
        usr = super().save(commit=False)
        usr.set_password(self.cleaned_data["password"])
        if commit:
            usr.save()
        return usr


class LoginForm(forms.Form):
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *poz, request=None, **dop):
        super().__init__(*poz, **dop)
        self.request = request
        self.user = None

    def clean(self):
        chist = super().clean()
        pochta = chist.get("email")
        par = chist.get("password")
        if pochta and par:
            self.user = authenticate(
                request=self.request,
                email=pochta.strip().lower(),
                password=par,
            )
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return chist


class ProfileForm(forms.ModelForm):
    sbros_avy = forms.BooleanField(required=False, label="Использовать букву имени")
    phone = forms.CharField(
        label="Телефон",
        max_length=12,
        widget=forms.TextInput(attrs={"placeholder": "+79001234567"}),
    )
    github_url = forms.URLField(
        label="Ссылка на GitHub",
        required=False,
        assume_scheme="https",
        validators=[github_adres],
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "avatar", "about", "phone", "github_url")
        widgets = {
            "avatar": forms.FileInput(attrs={"accept": "image/*"}),
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        return svobodnaya_pochta(self.cleaned_data["email"], self.instance.pk)

    def clean_phone(self):
        return svobodny_nom(self.cleaned_data["phone"], self.instance.pk)

    def clean_avatar(self):
        ava = self.cleaned_data.get("avatar")
        if self.files.get("avatar") and ava:
            ras = Path(ava.name).suffix.lower()
            ava.name = f"{uuid4().hex}{ras}"
        return ava

    def save(self, commit=True):
        usr = super().save(commit=False)
        if self.cleaned_data.get("sbros_avy") and not self.files.get("avatar"):
            usr.dobavit_avu()
        if commit:
            usr.save()
            self.save_m2m()
        return usr
