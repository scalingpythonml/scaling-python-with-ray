from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class DeviceManager(models.Manager):
    def can_register_device(self, serial_number: str):
        try:
            device = self.get(serial_number=serial_number)
            return not device.used and device.user is None
        except self.model.DoesNotExist:
            return False


class Device(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device",
    )

    objects = DeviceManager()

    def __str__(self):
        return f"Device: {self.serial_number}"

    def assign_to_user(self, user: User):
        if self.is_used:
            raise ValueError(f"Device: {self.serial_number} already used")
        if user.device:
            raise ValueError(f"User: {user} already have device")
        self.user = user
        self.save()

    def set_nickname(self, nickname: str):
        self.nickname = nickname
        self.save()

    @property
    def is_used(self):
        return self.used or self.user
