from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from django_countries.widgets import CountrySelectWidget

from apps.core.consts import ProfileStepsEnum


User = get_user_model()


class ProfileForm(forms.ModelForm):
    # device_nickname = forms.CharField(max_length=100)
    # twillion_number = forms.CharField(disabled=True, required=False)
    # company_email = forms.EmailField(disabled=True, required=False)
    # email = forms.EmailField(disabled=True, required=False)

    class Meta:
        model = User
        fields = [
            "full_name",
            # "email",
            "company",
            # "device_nickname",
            # "twillion_number",
            # "company_email",
            # "country",
        ]
        # widgets = {
        #     "country": CountrySelectWidget(attrs={"class": "field__input "})
        # }


class ProfileView(View):
    template = "accounts_form.html"
    form_class = ProfileForm

    def get(self, request):
        form = self.form_class(
            instance=request.user,
            initial={
                "device_nickname": request.user.device_nickname,
            },
        )
        context = {**self.base_context, "form": form}
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save(commit=True)
            # if request.user.have_device:
            #     User.objects.update_user_device_nickname(
            #         request.user, form.cleaned_data["device_nickname"]
            #     )
        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    @property
    def base_context(self):
        return {
            "title": "Settings",
            "navname": "Settings",
            "action": reverse("accounts:profile"),
            "action_button_name": "Save",
            "step": ProfileStepsEnum.SETTINGS.value,
            "forget": True,
        }
