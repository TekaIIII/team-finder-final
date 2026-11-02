from http import HTTPStatus

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

from common.constants import PROJECT_CLOSED, PROJECT_OPEN
from common.pagination import paginate_queryset
from skills.models import Skill

from .forms import ProjectForm
from .models import Project


@require_GET
def index(request):
    return redirect("projects:project_list")


@require_GET
def project_list(request):
    projects = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )

    selected_skill = request.GET.get("skill", "")
    if selected_skill:
        projects = projects.filter(skills__name=selected_skill)

    page, query_prefix = paginate_queryset(projects, request)

    data = {
        "projects": page.object_list,
        "page_obj": page,
        "all_skills": Skill.objects.order_by("name").values_list("name", flat=True),
        "active_skill": selected_skill,
        "query_prefix": query_prefix,
    }

    return render(request, "projects/project_list.html", data)


@ensure_csrf_cookie
@require_GET
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=project_id,
    )

    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
@require_POST
@transaction.atomic
def toggle_participation(request, project_id):
    project = get_object_or_404(Project.objects.select_for_update(), pk=project_id)

    if project.owner_id == request.user.pk:
        return JsonResponse(
            {"error": "Автор не может отказаться от своего проекта."},
            status=HTTPStatus.BAD_REQUEST,
        )

    is_participant = project.participants.filter(pk=request.user.pk).exists()

    if is_participant:
        project.participants.remove(request.user)
    else:
        if project.status == PROJECT_CLOSED:
            return JsonResponse(
                {"error": "Набор в проект завершён."},
                status=HTTPStatus.CONFLICT,
            )
        project.participants.add(request.user)

    return JsonResponse(
        {
            "status": "ok",
            "participant": not is_participant,
        }
    )


@login_required
@require_POST
@transaction.atomic
def complete_project(request, project_id):
    project = get_object_or_404(Project.objects.select_for_update(), pk=project_id)

    if project.owner_id != request.user.pk:
        return JsonResponse(
            {"error": "Завершить проект может только автор."},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != PROJECT_OPEN:
        return JsonResponse(
            {"error": "Проект уже закрыт."},
            status=HTTPStatus.CONFLICT,
        )

    project.status = PROJECT_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": PROJECT_CLOSED,
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        with transaction.atomic():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)

        return redirect("projects:project_detail", project_id=project.pk)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner_id != request.user.pk:
        return HttpResponseForbidden("Редактировать проект может только его автор.")

    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        with transaction.atomic():
            project = form.save()
            project.participants.add(project.owner)

        return redirect("projects:project_detail", project_id=project.pk)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )
