from django.urls import path

from . import views as views

app_name = "users"

urlpatterns = [
    path(
        "list/",
        views.user_list,
        name="user_list",
    ),
    path(
        "register/",
        views.register,
        name="register",
    ),
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),
    path(
        "edit-profile/",
        views.edit_profile,
        name="edit_profile",
    ),
    path(
        "change-password/",
        views.change_password,
        name="change_password",
    ),
    path(
        "<int:user_id>/",
        views.user_profile,
        name="profile",
    ),
]
