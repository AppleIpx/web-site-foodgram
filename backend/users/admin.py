from django.contrib import admin
from django.contrib.admin import register
from . import models

admin.site.register(models.Follow)


@register(models.User)
class CustomUserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', )
    search_fields = ('username', 'email',)
