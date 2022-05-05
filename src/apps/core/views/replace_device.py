from django.shortcuts import render
from django.urls import reverse
from django.views import View

from apps.core.models import Device
from apps.core.views.add_device import DeviceForm


class ReplaceDeviceView(View):
    template = "accounts_form.html"
    form_class = DeviceForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            if request.user.have_device:
                Device.objects.delete_user_device(request.user)
            new_user_device = Device.objects.get(
                serial_number=form.cleaned_data["serial_number"]
            )
            new_user_device.assign_to_user(request.user)
            new_user_device.set_nickname(form.cleaned_data["nickname"])
            new_user_device.save()
        return render(
            request,
            self.template,
            {**self.base_context, "form": self.form_class()},
        )

    @property
    def base_context(self):
        return {
            "title": "Replace device",
            "navname": "Replace device",
            "action": reverse("core:replace-device"),
            "action_button_name": "Update",
        }
