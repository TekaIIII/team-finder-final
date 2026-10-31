from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from common.stranicy import razbit

from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import User


@require_GET
def spisok_polz(zap):
    polz = User.objects.order_by("-id")
    stran, pref = razbit(polz, zap)
    dann = {
        "participants": stran.object_list,
        "page_obj": stran,
        "query_prefix": pref,
    }
    return render(zap, "users/participants.html", dann)


@require_GET
def profil_polz(zap, pk):
    """Открывает публичный профиль и проекты его владельца."""
    hoz = get_object_or_404(User.objects.prefetch_related("owned_projects__participants"), pk=pk)
    return render(zap, "users/user-details.html", {"user": hoz})


@require_http_methods(["GET", "POST"])
def registraciya(zap):
    if zap.user.is_authenticated:
        return redirect("projects:project_list")
    frm = RegistrationForm(zap.POST if zap.method == "POST" else None)
    if zap.method == "POST" and frm.is_valid():
        frm.save()
        return redirect("users:login")
    return render(zap, "users/register.html", {"form": frm})


@require_http_methods(["GET", "POST"])
def vhod(zap):
    if zap.user.is_authenticated:
        return redirect("projects:project_list")
    frm = LoginForm(zap.POST if zap.method == "POST" else None, request=zap)
    if zap.method == "POST" and frm.is_valid():
        login(zap, frm.user)
        return redirect("projects:project_list")
    return render(zap, "users/login.html", {"form": frm})


@require_POST
def vyhod(zap):
    logout(zap)
    return redirect("projects:project_list")


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def pravka_profilya(zap):
    """Связывает форму только с текущим пользователем."""
    frm = ProfileForm(
        zap.POST if zap.method == "POST" else None,
        zap.FILES if zap.method == "POST" else None,
        instance=zap.user,
    )
    if zap.method == "POST" and frm.is_valid():
        frm.save()
        return redirect("users:profile", pk=zap.user.pk)
    return render(zap, "users/edit_profile.html", {"form": frm})


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def smena_parolya(zap):
    frm = PasswordChangeForm(user=zap.user, data=zap.POST if zap.method == "POST" else None)
    if zap.method == "POST" and frm.is_valid():
        usr = frm.save()
        update_session_auth_hash(zap, usr)
        return redirect("users:profile", pk=usr.pk)
    return render(zap, "users/change_password.html", {"form": frm})
