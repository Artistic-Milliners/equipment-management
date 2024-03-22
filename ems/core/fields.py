from typing import Any
from django.db import models
from django.core.exceptions import ValidationError

class UnitIDField(models.CharField):

    def validate(self, value: Any, model_instance: models.Model) -> None:
        if not value.isdigit() or len(value)!=3:
            raise ValidationError("Value must be three integer characters in the format XXX")
    
    def get_prep_value(self, value: Any) -> Any:
        if not value.startswith('AMX'):
            value = 'AMX'+value
        return value
    
    