from django import forms

from common.constants import URL_MAX_LENGTH
from common.validators import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    github_url = forms.URLField(
        label="Ссылка на GitHub",
        max_length=URL_MAX_LENGTH,
        required=False,
        assume_scheme="https",
        validators=[validate_github_url],
    )

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}
