from django import forms
from django.contrib.auth import get_user_model, password_validation

from django_countries.widgets import CountrySelectWidget

from apps.core.models import Device


User = get_user_model()

password_help_text = password_validation.password_validators_help_text_html()


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Type your email"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password"}
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm your password"}
        ),
        help_text=password_help_text,
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email_occupied = User.objects.filter(email=cleaned_data.get("email"))
        if email_occupied:
            self.add_error(
                "email", "User with this email address already exists"
            )
        if password != confirm_password:
            self.add_error("confirm_password", "Passwords does not match")
            self.add_error("confirm_password", "Passwords does not match1")

        return cleaned_data


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "company", "country"]
        widgets = {
            "country": CountrySelectWidget(attrs={"class": "form-select"})
        }


class BlockedNumberForm(forms.Form):
    number = forms.CharField(required=True)


class DeviceForm(forms.Form):
    serial_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Serial number of your device"}
        ),
        required=True,
    )
    nickname = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Choose nickname for your device"}
        ),
        required=True,
    )

    def clean(self):
        cleaned_data = super(DeviceForm, self).clean()
        serial_number = cleaned_data["serial_number"]
        serial_number_is_valid = Device.objects.can_register_device(
            serial_number
        )
        if not serial_number_is_valid:
            self.add_error("serial_number", "Invalid serial number")
        return cleaned_data
