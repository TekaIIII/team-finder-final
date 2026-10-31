from django.urls import path

from . import views as obr

app_name = "users"

urlpatterns = [
    path(
        "list/",
        obr.spisok_polz,
        name="user_list",
    ),
    path(
        "register/",
        obr.registraciya,
        name="register",
    ),
    path(
        "login/",
        obr.vhod,
        name="login",
    ),
    path(
        "logout/",
        obr.vyhod,
        name="logout",
    ),
    path(
        "edit-profile/",
        obr.pravka_profilya,
        name="edit_profile",
    ),
    path(
        "change-password/",
        obr.smena_parolya,
        name="change_password",
    ),
    path(
        "<int:pk>/",
        obr.profil_polz,
        name="profile",
    ),
]
