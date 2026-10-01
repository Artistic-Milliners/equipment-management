from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "is_employee", "is_contractor")  # <-- no 'password' here

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Password and Confirm Password do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # hash the password
        if commit:
            user.save()
        return user