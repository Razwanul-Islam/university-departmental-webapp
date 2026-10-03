from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import User


class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "email", "name", "user_type", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        (
            "Personal info",
            {
                "fields": [
                    "name",
                    "user_type",
                ]
            },
        ),
        (
            "Permissions",
            {
                "fields": [
                    "is_admin",
                ]
            },
        ),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "user_type", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []


admin.site.register(User, UserModelAdmin)
