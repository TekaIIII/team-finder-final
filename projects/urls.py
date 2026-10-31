from django.urls import path

from skills import views as nav_obr

from . import views as obr

app_name = "projects"

urlpatterns = [
    path(
        "project/list/",
        obr.spisok_proektov,
        name="project_list",
    ),
    path(
        "projects/create-project/",
        obr.sozdat_proekt,
        name="create_project",
    ),
    path(
        "projects/skills/",
        nav_obr.poisk_nav,
        name="skill_list",
    ),
    path(
        "projects/<int:pk>/",
        obr.kartochka_proekta,
        name="project_detail",
    ),
    path(
        "projects/<int:pk>/edit/",
        obr.pravit_proekt,
        name="edit_project",
    ),
    path(
        "projects/<int:pk>/toggle-participate/",
        obr.smenit_uchastie,
        name="toggle_participate",
    ),
    path(
        "projects/<int:pk>/complete/",
        obr.zavershit_proekt,
        name="complete_project",
    ),
    path(
        "projects/<int:pk>/skills/add/",
        nav_obr.dobavit_nav,
        name="add_project_skill",
    ),
    path(
        "projects/<int:pk>/skills/<int:skill_id>/remove/",
        nav_obr.ubrat_nav,
        name="remove_project_skill",
    ),
]
