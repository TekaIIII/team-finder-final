from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from common.proverki import github_adres

from .forms import svobodnaya_pochta, svobodny_nom
from .models import User


class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "name", "surname")

    def clean_email(self):
        return svobodnaya_pochta(self.cleaned_data["email"], self.instance.pk)


class AdminUserChangeForm(UserChangeForm):
    github_url = forms.URLField(
        label="Ссылка на GitHub",
        required=False,
        assume_scheme="https",
        validators=[github_adres],
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def clean_email(self):
        return svobodnaya_pochta(self.cleaned_data["email"], self.instance.pk)

    def clean_phone(self):
        nom = self.cleaned_data.get("phone")
        if nom:
            return svobodny_nom(nom, self.instance.pk)
        return None


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    list_display = ("email", "name", "surname", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "name", "surname")
    ordering = ("-id",)
    readonly_fields = ("last_login",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {
                "fields": (
                    "name",
                    "surname",
                    "avatar",
                    "phone",
                    "github_url",
                    "about",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Последний вход", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")
