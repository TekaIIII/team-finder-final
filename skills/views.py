import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from projects.models import Project

from .forms import SkillAddForm
from .models import Skill


@require_GET
def poisk_nav(zap):
    """Ограничивает подсказки в SQL до загрузки результата."""
    q = zap.GET.get("q", "").strip()
    navyki = Skill.objects.filter(name__istartswith=q).order_by("name").values("id", "name")[:10]
    return JsonResponse(list(navyki), safe=False)


@login_required(login_url="/users/login/")
@require_POST
@transaction.atomic
def dobavit_nav(zap, pk):
    pr = get_object_or_404(Project.objects.select_for_update(), pk=pk)
    if pr.owner_id != zap.user.pk:
        return JsonResponse({"error": "Нет прав на изменение проекта."}, status=403)
    try:
        dann = json.loads(zap.body)
    except ValueError:
        return JsonResponse({"error": "Некорректный JSON."}, status=400)
    if not isinstance(dann, dict):
        return JsonResponse({"error": "Ожидается JSON-объект."}, status=400)
    frm = SkillAddForm(dann)
    if not frm.is_valid():
        return JsonResponse(
            {
                "error": "Проверьте название или выбранный навык.",
                "errors": frm.errors.get_json_data(),
            },
            status=400,
        )
    nav = frm.cleaned_data["skill_id"]
    nov = False
    if nav is None:
        nazv = frm.cleaned_data["name"]
        nav = Skill.objects.filter(name__iexact=nazv).first()
        if nav is None:
            nav, nov = Skill.objects.get_or_create(name=nazv)
    dob = not pr.skills.filter(pk=nav.pk).exists()
    pr.skills.add(nav)
    return JsonResponse(
        {
            "skill_id": nav.pk,
            "id": nav.pk,
            "name": nav.name,
            "created": nov,
            "added": dob,
        }
    )


@login_required(login_url="/users/login/")
@require_POST
@transaction.atomic
def ubrat_nav(zap, pk, skill_id):
    """Удаляет связь с проектом, сохраняя общий навык."""
    pr = get_object_or_404(Project.objects.select_for_update(), pk=pk)
    if pr.owner_id != zap.user.pk:
        return JsonResponse({"error": "Нет прав на изменение проекта."}, status=403)
    nav = get_object_or_404(pr.skills.all(), pk=skill_id)
    pr.skills.remove(nav)
    return JsonResponse({"status": "ok", "removed": True})
