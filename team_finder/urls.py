from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from projects.views import index

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("", include("projects.urls")),
    path("users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
