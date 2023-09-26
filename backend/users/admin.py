from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import User

# admin.site.register(CustomUser)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('username', 'email',)
