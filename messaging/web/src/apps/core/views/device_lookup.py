from django import views
from django.http import JsonResponse

from apps.core.forms import DeviceLookupForm
from apps.core.models import Device


class DeviceLookup(views.View):
    form_class = DeviceLookupForm

    def get(self, request):
        form = self.form_class(request.GET)
        try:
            if form.is_valid():
                device_id = form.cleaned_data["device_id"]
                user = Device.objects.get(serial_number=device_id).user
                username = user.username
                return JsonResponse(
                    {"status": "true", "email": f"{username}@spacebeaver.com"}
                )
            else:
                message = "Invalid form. Please set device_id"
                return JsonResponse(
                    {"status": "false", "message": message}, status=400
                )

        except:
            message = (
                "Device not configured, please setup and activate account."
            )
            return JsonResponse(
                {"status": "false", "message": message},
                status=402,  # 402 is payment required
            )
