from django import forms
from core.models import Unit, Equipment

class UnitForm(forms.ModelForm):
    
    class meta:
        model = Unit
        fields = ["id", "name", "location"]


