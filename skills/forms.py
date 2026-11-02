from django import forms

from .models import Skill


class SkillAddForm(forms.ModelForm):
    skill_id = forms.ModelChoiceField(queryset=Skill.objects.all(), required=False)

    class Meta:
        model = Skill
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        # Уже существующий навык можно выбрать и по названию.
        skill = Skill.objects.filter(name__iexact=name).first()
        if skill is not None:
            self.instance = skill
            return skill.name
        return name

    def clean(self):
        cleaned_data = super().clean()
        skill = cleaned_data.get("skill_id")
        name = cleaned_data.get("name")
        if skill and name:
            raise forms.ValidationError("Передайте либо существующий навык, либо новое название.")
        if not skill and not name:
            raise forms.ValidationError("Выберите навык или введите новое название.")
        return cleaned_data
