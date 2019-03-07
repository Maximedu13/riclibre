from django.contrib import admin

from account_manager.models import CustomUser


# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    admin class for CustomUser model.
    """
    search_fields = ("email", "username", "first_name", "last_name")
