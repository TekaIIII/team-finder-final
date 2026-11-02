import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from common.constants import SKILL_SUGGESTIONS_LIMIT
from projects.models import Project

from .forms import SkillAddForm
from .models import Skill


@require_GET
def skill_list(request):
    """Ограничивает подсказки в SQL до загрузки результата."""
    query = request.GET.get("q", "").strip()
    skills = (
        Skill.objects.filter(name__istartswith=query)
        .order_by("name")
        .values("id", "name")[:SKILL_SUGGESTIONS_LIMIT]
    )
    return JsonResponse(list(skills), safe=False)


@login_required
@require_POST
@transaction.atomic
def add_project_skill(request, project_id):
    project = get_object_or_404(Project.objects.select_for_update(), pk=project_id)
    if project.owner_id != request.user.pk:
        return JsonResponse(
            {"error": "Нет прав на изменение проекта."}, status=HTTPStatus.FORBIDDEN
        )
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Некорректный JSON."}, status=HTTPStatus.BAD_REQUEST)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Ожидается JSON-объект."}, status=HTTPStatus.BAD_REQUEST)
    form = SkillAddForm(data)
    if not form.is_valid():
        return JsonResponse(
            {
                "error": "Проверьте название или выбранный навык.",
                "errors": form.errors.get_json_data(),
            },
            status=HTTPStatus.BAD_REQUEST,
        )
    skill = form.cleaned_data["skill_id"]
    created = False
    if skill is None:
        name = form.cleaned_data["name"]
        skill = Skill.objects.filter(name__iexact=name).first()
        if skill is None:
            skill, created = Skill.objects.get_or_create(name=name)
    added = not project.skills.filter(pk=skill.pk).exists()
    project.skills.add(skill)
    return JsonResponse(
        {
            "skill_id": skill.pk,
            "id": skill.pk,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
@transaction.atomic
def remove_project_skill(request, project_id, skill_id):
    """Удаляет связь с проектом, сохраняя общий навык."""
    project = get_object_or_404(Project.objects.select_for_update(), pk=project_id)
    if project.owner_id != request.user.pk:
        return JsonResponse(
            {"error": "Нет прав на изменение проекта."}, status=HTTPStatus.FORBIDDEN
        )
    skill = get_object_or_404(project.skills.all(), pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True})
