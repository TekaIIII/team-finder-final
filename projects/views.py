from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from common.stranicy import razbit
from skills.models import Skill

from .forms import ProjectForm
from .models import Project


@require_GET
def glav(zap):
    return redirect("projects:project_list")


@require_GET
def spisok_proektov(zap):
    spis = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )

    vybor = zap.GET.get("skill", "")
    if vybor:
        spis = spis.filter(skills__name=vybor)

    stran, pref = razbit(spis, zap)

    dann = {
        "projects": stran.object_list,
        "page_obj": stran,
        "all_skills": Skill.objects.order_by("name").values_list(
            "name", flat=True
        ),
        "active_skill": vybor,
        "query_prefix": pref,
    }

    return render(zap, "projects/project_list.html", dann)


@ensure_csrf_cookie
@require_GET
def kartochka_proekta(zap, pk):
    pr = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants", "skills"
        ),
        pk=pk,
    )

    return render(
        zap,
        "projects/project-details.html",
        {"project": pr},
    )


@login_required(login_url="/users/login/")
@require_POST
@transaction.atomic
def smenit_uchastie(zap, pk):
    pr = get_object_or_404(Project.objects.select_for_update(), pk=pk)

    if pr.owner_id == zap.user.pk:
        return JsonResponse(
            {"error": "Автор не может отказаться от своего проекта."},
            status=400,
        )

    uch = pr.participants.filter(pk=zap.user.pk).exists()

    if uch:
        pr.participants.remove(zap.user)
    else:
        if pr.status == "closed":
            return JsonResponse(
                {"error": "Набор в проект завершён."},
                status=409,
            )
        pr.participants.add(zap.user)

    return JsonResponse({
        "status": "ok",
        "participant": not uch,
    })


@login_required(login_url="/users/login/")
@require_POST
@transaction.atomic
def zavershit_proekt(zap, pk):
    pr = get_object_or_404(Project.objects.select_for_update(), pk=pk)

    if pr.owner_id != zap.user.pk:
        return JsonResponse(
            {"error": "Завершить проект может только автор."},
            status=403,
        )

    if pr.status != "open":
        return JsonResponse(
            {"error": "Проект уже закрыт."},
            status=409,
        )

    pr.status = "closed"
    pr.save(update_fields=["status"])

    return JsonResponse({
        "status": "ok",
        "project_status": "closed",
    })


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def sozdat_proekt(zap):
    if zap.method == "POST":
        frm = ProjectForm(zap.POST)
    else:
        frm = ProjectForm()

    if zap.method == "POST" and frm.is_valid():
        with transaction.atomic():
            pr = frm.save(commit=False)
            pr.owner = zap.user
            pr.save()
            pr.participants.add(zap.user)

        return redirect("projects:project_detail", pk=pr.pk)

    return render(
        zap,
        "projects/create-project.html",
        {"form": frm, "is_edit": False},
    )


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def pravit_proekt(zap, pk):
    pr = get_object_or_404(Project, pk=pk)

    if pr.owner_id != zap.user.pk:
        return HttpResponseForbidden(
            "Редактировать проект может только его автор."
        )

    if zap.method == "POST":
        frm = ProjectForm(zap.POST, instance=pr)
    else:
        frm = ProjectForm(instance=pr)

    if zap.method == "POST" and frm.is_valid():
        with transaction.atomic():
            pr = frm.save()
            pr.participants.add(pr.owner)

        return redirect("projects:project_detail", pk=pr.pk)

    return render(
        zap,
        "projects/create-project.html",
        {"form": frm, "is_edit": True},
    )
