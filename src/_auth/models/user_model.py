from django.db import models


class BotUser(models.Model):
    username = models.CharField(max_length=150, null=False, blank=False)
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return f"{self.full_name}"
