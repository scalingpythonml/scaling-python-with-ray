from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Device


class DeviceOwnerRequestSerializer(serializers.Serializer):
    device_id = serializers.CharField()


class DeviceOwnerResponseSerializer(serializers.Serializer):
    twillion_number = serializers.CharField()
    email = serializers.CharField()


class DeviceOwnerApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceOwnerRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serial_number = serializer.validated_data["device_id"]
            device = get_object_or_404(
                Device.objects.all(), serial_number=serial_number
            )
            if not device.user:
                return Response({"message": "Device dont have user"})
            return Response(
                DeviceOwnerResponseSerializer(
                    {
                        "twillion_number": device.user.twillion_number,
                        "email": device.user.email,
                    }
                ).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
