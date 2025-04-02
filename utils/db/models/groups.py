from tortoise import fields
from tortoise.models import Model


class Group(Model):
    id = fields.BigIntField(pk=True)
    group_id = fields.CharField(max_length=16, unique=True, db_index=True)
    title = fields.CharField(max_length=100, null=True)
    group_type = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=100, null=True, unique=True)
    who_added = fields.ForeignKeyField("models.User", related_name="who_added", null=True)
    date_joined = fields.DatetimeField(auto_now_add=True)


class GroupStatistics(Model):
    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField("models.Group", related_name="statistics")
    members = fields.IntField(default=0)
    total_posts = fields.IntField(default=0)
    total_comments = fields.IntField(default=0)
    deleted_posts = fields.IntField(default=0)
    status = fields.CharField(max_length=8, null=True, default='daily')
    created_at = fields.DatetimeField(auto_now_add=True)
