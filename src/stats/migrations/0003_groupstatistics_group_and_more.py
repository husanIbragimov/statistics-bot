# Generated by Django 5.2 on 2025-07-21 04:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_alter_groupstatistics_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupstatistics',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='statistics', to='stats.groups'),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='deleted_posts',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='members',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='status',
            field=models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily', max_length=8),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='total_comments',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='total_posts',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='groupstatistics',
            name='views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddConstraint(
            model_name='groupstatistics',
            constraint=models.UniqueConstraint(fields=('group', 'date'), name='unique_group_date'),
        ),
    ]
