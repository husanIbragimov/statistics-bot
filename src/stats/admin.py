from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.http import HttpResponse
from datetime import date, timedelta
import pandas as pd
import io

from .models import Groups, GroupStatistics



@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "group_type", "username", "date_joined", "parent", "who_added")
    search_fields = ("title", "username")
    list_filter = ("group_type", "date_joined")
    list_select_related = ("who_added",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("generate-report/", self.admin_site.admin_view(self.generate_report), name="generate-report"),
        ]
        return custom_urls + urls

    def generate_report(self, request):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week - timedelta(weeks=4)

        stats = GroupStatistics.objects.filter(
            date__gte=start_date,
            date__lte=today
        ).select_related("group").values(
            "group__title", "group__username", "members",
            "total_posts", "total_comments", "deleted_posts",
            "views", "date"
        )

        if not stats.exists():
            return redirect("/admin/stats/groups/")

        df = pd.DataFrame(stats)
        df.rename(columns={
            'group__title': 'Guruh',
            'group__username': 'Username',
            'members': 'Members',
            'total_posts': 'Postlar',
            'total_comments': 'Izohlar',
            'deleted_posts': 'O‘chirilgan postlar',
            'views': 'Ko‘rishlar',
            'date': 'Sana'
        }, inplace=True)
        df['Sana'] = pd.to_datetime(df['Sana'])

        display_rows = []
        for guruh_nomi, guruh_df in df.groupby('Guruh'):
            display_rows.append({
                'Guruh': f"Guruh: {guruh_nomi}",
                'Username': '', 'Members': '', 'Postlar': '',
                'Izohlar': '', 'O‘chirilgan postlar': '', 'Ko‘rishlar': '', 'Sana': ''
            })
            guruh_df = guruh_df.sort_values(by='Sana', ascending=False)
            for _, row in guruh_df.iterrows():
                display_rows.append({
                    'Guruh': '',
                    'Username': row['Username'],
                    'Members': row['Members'],
                    'Postlar': row['Postlar'],
                    'Izohlar': row['Izohlar'],
                    'O‘chirilgan postlar': row['O‘chirilgan postlar'],
                    'Ko‘rishlar': row['Ko‘rishlar'],
                    'Sana': row['Sana'].strftime('%Y-%m-%d')
                })

        formatted_df = pd.DataFrame(display_rows)

        weekly_avg = (
            df.groupby(['Guruh', 'Username'])[
                ['Postlar', 'Izohlar', 'O‘chirilgan postlar', 'Ko‘rishlar']
            ]
            .mean()
            .round()
            .reset_index()
        )

        # Excel faylni xotirada yaratamiz
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            formatted_df.to_excel(writer, sheet_name='Hisobot', index=False)
            weekly_avg.to_excel(writer, sheet_name='Haftalik', index=False)

        output.seek(0)
        filename = f"hisobot_{start_date}_{today}.xlsx"

        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
