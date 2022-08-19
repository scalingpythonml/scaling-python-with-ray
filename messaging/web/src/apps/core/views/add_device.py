from django import views
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.core.consts import OnboardingStepsEnum
from apps.core.forms import DeviceForm
from apps.core.models import Device


class AddDeviceView(views.View):
    template = "onboarding_wizard_form.html"
    form_class = DeviceForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template, {"form": form, **self.base_context}
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            device = Device.objects.get(
                serial_number=form.cleaned_data["serial_number"]
            )
            device.assign_to_user(request.user)
            device.set_nickname(form.cleaned_data["nickname"])
            device.save()
            return redirect(reverse("core:pick-plan"))
        return render(
            request, self.template, {"form": form, **self.base_context}
        )

    @property
    def base_context(self):
        return {
            "title": "Add device",
            "navname": "Please, add your device",
            "action": reverse("core:add-device"),
            "step": OnboardingStepsEnum.ADD_DEVICE.value,
        }
