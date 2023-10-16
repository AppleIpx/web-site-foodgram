from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        'id',
        'password',
        'username',
        'first_name',
        'last_name',
    )

    username = models.CharField(verbose_name='Логин', unique=True, max_length=128, blank=False)
    email = models.EmailField(verbose_name="Электронная почта", unique=True, blank=False)
    first_name = models.CharField(verbose_name="Имя", max_length=30, blank=False)
    last_name = models.CharField(verbose_name="Фамилия", max_length=30, blank=False)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        unique_together = (
            "user",
            "following",
        )
