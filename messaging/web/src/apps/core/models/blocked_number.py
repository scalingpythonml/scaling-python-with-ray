from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class BlockedNumberManager(models.Manager):
    def get_user_blocked_numbers(self, user: User):
        return self.filter(user__id=user.id)

    def add_user_blocked_number(self, number: str, user: User):
        number, created = self.get_or_create(number=number)
        number.user.add(user)
        number.save()

    def delete_user_blocked_number(self, number_id: int, user: User):
        number = self.get(id=number_id)
        number.user.remove(user)
        number.save()


class BlockedNumber(models.Model):
    number = models.CharField(max_length=20, unique=True)
    user = models.ManyToManyField(User, related_name="blocked_numbers")

    object = BlockedNumberManager()

    def __str__(self):
        return self.number
