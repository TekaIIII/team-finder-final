from django import forms

from common.proverki import github_adres

from .models import Project


class ProjectForm(forms.ModelForm):
    github_url = forms.URLField(
        label="Ссылка на GitHub",
        required=False,
        assume_scheme="https",
        validators=[github_adres],
    )
    status = forms.ChoiceField(
        label="Статус",
        choices=(("open", "Открыт"), ("closed", "Закрыт")),
        initial="open",
    )

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}
