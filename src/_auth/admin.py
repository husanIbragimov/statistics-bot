from django.contrib import admin
from .models import BotUser

@admin.register(BotUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "telegram_id", 'full_name')