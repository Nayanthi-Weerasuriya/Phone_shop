from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("image", "phone", "address_line_1", "address_line_2", "city", "state", "country", "zip_code")
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "address_line_1": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-line1"}),
            "address_line_2": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-line2"}),
            "city": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-level2"}),
            "state": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-level1"}),
            "country": forms.TextInput(attrs={"class": "form-control", "autocomplete": "country-name"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control", "autocomplete": "postal-code"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image

        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
        extension = image.name.lower().rsplit(".", 1)
        extension = f".{extension[-1]}" if len(extension) == 2 else ""
        if extension not in allowed_extensions:
            raise forms.ValidationError("Upload a JPG, PNG, or GIF image.")
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("The image must be 5 MB or smaller.")
        return image
