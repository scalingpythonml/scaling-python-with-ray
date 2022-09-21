from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Enter new email"})
    )

    def clean(self):
        cleaned_data = super(ChangeEmailForm, self).clean()
        email_occupied = User.objects.filter(
            email=cleaned_data["new_email"]
        ).exists()
        if email_occupied:
            self.add_error("new_email", "User with this email exist")

        return cleaned_data


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password"}
        ),
        required=True,
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Create new password"}
        ),
        required=True,
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm new password"}
        ),
        required=True,
    )

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")
        if new_password != confirm_new_password:
            self.add_error("confirm_new_password", "Passwords does not match")

        return cleaned_data
