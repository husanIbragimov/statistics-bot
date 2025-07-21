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
        if self.title:
            return self.title
        return "Unnamed Group"




class GroupStatistics(models.Model):
    STATUS = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    members = models.IntegerField(default=0)
    total_posts = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    deleted_posts = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    status = models.CharField(max_length=8, choices=STATUS, default='daily')
    date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('Groups', models.DO_NOTHING, related_name='statistics', null=True)

    class Meta:
        managed = False
        db_table = 'group_statistics'
        constraints = [
            models.UniqueConstraint(fields=['group', 'date'], name='unique_group_date')
        ]

    def __str__(self):
        return f"{self.date}"
