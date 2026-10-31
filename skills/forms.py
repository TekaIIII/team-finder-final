from django import forms

from .models import Skill


class SkillAddForm(forms.Form):
    skill_id = forms.ModelChoiceField(queryset=Skill.objects.all(), required=False)
    name = forms.CharField(max_length=124, required=False)

    def clean(self):
        chist = super().clean()
        nav = chist.get("skill_id")
        nazv = chist.get("name")
        if nav and nazv:
            raise forms.ValidationError("Передайте либо существующий навык, либо новое название.")
        if not nav and not nazv:
            raise forms.ValidationError("Выберите навык или введите новое название.")
        return chist
