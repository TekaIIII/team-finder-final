from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "owner__email", "owner__name", "owner__surname")
    readonly_fields = ("created_at",)
    filter_horizontal = ("participants", "skills")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.participants.add(form.instance.owner)
