from django.urls import path

from skills import views as skill_views

from . import views as views

app_name = "projects"

urlpatterns = [
    path(
        "project/list/",
        views.project_list,
        name="project_list",
    ),
    path(
        "projects/create-project/",
        views.create_project,
        name="create_project",
    ),
    path(
        "projects/skills/",
        skill_views.skill_list,
        name="skill_list",
    ),
    path(
        "projects/<int:project_id>/",
        views.project_detail,
        name="project_detail",
    ),
    path(
        "projects/<int:project_id>/edit/",
        views.edit_project,
        name="edit_project",
    ),
    path(
        "projects/<int:project_id>/toggle-participate/",
        views.toggle_participation,
        name="toggle_participate",
    ),
    path(
        "projects/<int:project_id>/complete/",
        views.complete_project,
        name="complete_project",
    ),
    path(
        "projects/<int:project_id>/skills/add/",
        skill_views.add_project_skill,
        name="add_project_skill",
    ),
    path(
        "projects/<int:project_id>/skills/<int:skill_id>/remove/",
        skill_views.remove_project_skill,
        name="remove_project_skill",
    ),
]
