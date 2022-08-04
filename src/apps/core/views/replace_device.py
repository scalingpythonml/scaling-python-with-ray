from django.shortcuts import render
from django.urls import reverse
from django.views import View

from apps.core.consts import ProfileStepsEnum
from apps.core.models import Device
from apps.core.views.add_device import DeviceForm


class ReplaceDeviceView(View):
    template = "accounts_form.html"
    form_class = DeviceForm

    def get(self, request):
        initial = {}
        if request.user.have_device:
            device = Device.objects.get(user=request.user)
            if device:
                initial = {
                    "serial_number": device.serial_number,
                    "nickname": device.nickname,
                }

        form = self.form_class(initial=initial)

        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    def post(self, request):
        form = self.form_class(request.POST)
        initial = {}
        if form.is_valid():
            if request.user.have_device:
                Device.objects.delete_user_device(request.user)
            new_user_device = Device.objects.get(
                serial_number=form.cleaned_data["serial_number"]
            )
            new_user_device.assign_to_user(request.user)
            new_user_device.set_nickname(form.cleaned_data["nickname"])
            new_user_device.save()
            initial = {
                "serial_number": new_user_device.serial_number,
                "nickname": new_user_device.nickname,
            }
        return render(
            request,
            self.template,
            {**self.base_context, "form": self.form_class(initial=initial)},
        )

    @property
    def base_context(self):
        return {
            "title": "Replace device",
            "navname": "Replace device",
            "action": reverse("core:replace-device"),
            "action_button_name": "Update",
            "step": ProfileStepsEnum.SETTINGS.value,
        }
