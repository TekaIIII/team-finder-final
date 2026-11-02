from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from common.pagination import paginate_queryset

from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import User


@require_GET
def user_list(request):
    users = User.objects.order_by("-id")
    page, query_prefix = paginate_queryset(users, request)
    data = {
        "participants": page.object_list,
        "page_obj": page,
        "query_prefix": query_prefix,
    }
    return render(request, "users/participants.html", data)


@require_GET
def user_profile(request, user_id):
    """Открывает публичный профиль и проекты его владельца."""
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants"), pk=user_id
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("projects:project_list")
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:project_list")
    form = LoginForm(request.POST or None, request=request)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:project_list")
    return render(request, "users/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """Связывает форму только с текущим пользователем."""
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect("users:profile", user_id=request.user.pk)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:profile", user_id=user.pk)
    return render(request, "users/change_password.html", {"form": form})
