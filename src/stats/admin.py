from django.contrib import admin

from .models import GroupStatistics, Groups


class GroupStatsStackedInline(admin.StackedInline):
    model = GroupStatistics
    extra = 0
    readonly_fields = ('created_at', 'total_comments', 'deleted_posts')


@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "group_type", "username", "date_joined", "parent", "who_added")
    search_fields = ("title", "username")
    list_filter = ("group_type", "date_joined")
    list_select_related = ("who_added",)
    inlines = [GroupStatsStackedInline]

