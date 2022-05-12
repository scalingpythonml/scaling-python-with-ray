from django import forms, views
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.core.models import Device


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
            "navname": "Add device",
            "action": reverse("core:add-device"),
            "step": 3,
        }
