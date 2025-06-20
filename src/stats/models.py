from django.db import models

from _auth.models import BotUser


class Groups(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    group_type = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(unique=True, max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField()
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    who_added = models.ForeignKey(BotUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'groups'

    def __str__(self):
        return self.title




class GroupStatistics(models.Model):
    STATUS = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    members = models.IntegerField()
    total_posts = models.IntegerField()
    total_comments = models.IntegerField()
    deleted_posts = models.IntegerField()
    views = models.IntegerField()
    status = models.CharField(max_length=8, choices=STATUS, default='daily')
    date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    group = models.ForeignKey('Groups', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'group_statistics'

    def __str__(self):
        return f"{self.date}"
