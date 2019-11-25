from django import forms
from .models import GroupMaterialRate


class MaterialRateForm(forms.ModelForm):

    class Meta:
        model = GroupMaterialRate
        fields = ("material", "amount")

