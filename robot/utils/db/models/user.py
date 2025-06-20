from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, db_index=True)
    username = fields.CharField(max_length=64, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    # status = fields.BooleanField(default=False)
    age = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"
        ordering = ["-id"]
