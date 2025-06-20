import io
from datetime import date, timedelta

import pandas as pd
from django.contrib import admin
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.urls import path

from .models import Groups, GroupStatistics


class GroupStatsInline(admin.TabularInline):
    model = GroupStatistics
    extra = 0
    fields = ("members", "total_posts", "date", "total_comments", "deleted_posts", "views")
    readonly_fields = ("total_comments", "deleted_posts", "views")


@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "group_type", "username", "date_joined", "parent", "who_added")
    search_fields = ("title", "username")
    list_filter = ("group_type", "date_joined")
    list_select_related = ("who_added",)
    inlines = (GroupStatsInline,)

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

        # === 1. Aggregated Queryset ===
        stats = (
            GroupStatistics.objects.filter(
                date__gte=start_date,
                date__lte=today
            )
            .values("group__title", "group__username", "date")
            .annotate(
                members=Sum("members"),
                total_posts=Sum("total_posts"),
                total_comments=Sum("total_comments"),
                deleted_posts=Sum("deleted_posts"),
                views=Sum("views"),
                records_count=Count("id")
            )
        )

        if not stats:
            return HttpResponse("Ma'lumot topilmadi.", status=404)

        # === 2. DataFrame yasash ===
        df = pd.DataFrame(stats)
        df.rename(columns={
            'group__title': 'Guruh',
            'group__username': 'Username',
            'members': 'Members',
            'total_posts': 'Postlar',
            'total_comments': 'Izohlar',
            'deleted_posts': 'O‘chirilgan postlar',
            'views': 'Ko‘rishlar',
            'date': 'Sana',
            'records_count': 'Takroriy yozuvlar'
        }, inplace=True)
        df['Sana'] = pd.to_datetime(df['Sana'])

        # === 3. Formatlab chiqarish ===
        display_rows = []
        for guruh_nomi, guruh_df in df.groupby('Guruh'):
            display_rows.append({
                'Guruh': f"Guruh: {guruh_nomi}",
                'Username': '', 'Members': '', 'Postlar': '',
                'Izohlar': '', 'O‘chirilgan postlar': '', 'Ko‘rishlar': '', 'Sana': '', 'Takroriy yozuvlar': ''
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
                    'Sana': row['Sana'].strftime('%Y-%m-%d'),
                    'Takroriy yozuvlar': int(row['Takroriy yozuvlar']),
                })

        formatted_df = pd.DataFrame(display_rows)

        # === 4. Haftalik o‘rtacha ko‘rsatkichlar ===
        weekly_avg = (
            df.groupby(['Guruh', 'Username'])[
                ['Postlar', 'Izohlar', 'O‘chirilgan postlar', 'Ko‘rishlar']
            ]
            .mean()
            .round()
            .reset_index()
        )

        # === 5. Excelga yozish ===
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            formatted_df.to_excel(writer, sheet_name='Hisobot', index=False)
            weekly_avg.to_excel(writer, sheet_name='Haftalik', index=False)

        output.seek(0)
        filename = f"hisobot_{start_date}_{today}.xlsx"
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
