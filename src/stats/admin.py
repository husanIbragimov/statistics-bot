import io
from datetime import date, timedelta

import pandas as pd
from django.contrib import admin
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.urls import path, reverse

from .models import Groups, GroupStatistics


class GroupStatsInline(admin.TabularInline):
    model = GroupStatistics
    extra = 0
    fields = ("members", "total_posts", "total_comments", "deleted_posts", "views", "date")
    readonly_fields = ("total_comments", "deleted_posts", "views")


@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "group_type", "username", "date_joined", "parent", "who_added")
    search_fields = ("title", "username")
    list_filter = ("group_type", "date_joined")
    list_select_related = ("who_added",)
    inlines = (GroupStatsInline,)
    change_list_template = "admin/groups_change_list.html"  # custom template


    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['monthly_report_url'] = reverse('admin:monthly-report')
        extra_context['generate_report_url'] = reverse('admin:generate-report')
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("generate-report/", self.admin_site.admin_view(self.generate_report), name="generate-report"),
            path("monthly-report/", self.admin_site.admin_view(self.monthly_report), name="monthly-report"),
        ]
        return custom_urls + urls

    def monthly_report(self, request):
        today = date.today()
        current_year = today.year

        stats = (
            GroupStatistics.objects.filter(
                date__year=current_year
            )
            .values("group__title", "group__username", "date")
            .annotate(
                members=Sum("members"),
                total_posts=Sum("total_posts")
            )
        )

        if not stats:
            return HttpResponse("Ma'lumot topilmadi.", status=404)

        df = pd.DataFrame(stats)
        df.rename(columns={
            'group__title': 'Guruh',
            'group__username': 'Username',
            'members': 'Members',
            'total_posts': 'Postlar',
            'date': 'Sana',
        }, inplace=True)
        df['Sana'] = pd.to_datetime(df['Sana'])
        df['Oy'] = df['Sana'].dt.to_period('M')

        # Oylik hisobot
        monthly_stats = (
            df.groupby(['Guruh', 'Username', 'Oy'])
            .agg({
                'Postlar': 'sum',
                'Members': ['first', 'last', 'count']
            })
            .reset_index()
        )
        monthly_stats.columns = ['Guruh', 'Username', 'Oy', 'Postlar', 'Aʼzolar_boshi', 'Aʼzolar_oxiri', 'Kun_soni']
        monthly_stats['Qo‘shilgan aʼzolar'] = (monthly_stats['Aʼzolar_oxiri'] - monthly_stats['Aʼzolar_boshi']).clip(
            lower=0)
        monthly_stats['Kunlik o‘rtacha'] = (monthly_stats['Qo‘shilgan aʼzolar'] / monthly_stats['Kun_soni']).round(2)

        final_df = monthly_stats[[
            'Guruh', 'Username', 'Oy', 'Postlar', 'Qo‘shilgan aʼzolar', 'Kunlik o‘rtacha'
        ]]

        # Excel faylga yozish
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_df.to_excel(writer, sheet_name='Oylik_hisobot', index=False)

        output.seek(0)
        filename = f"oylik_hisobot_{current_year}.xlsx"
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def get_last_two_weeks_range():
        today = date.today()
        # Haftaning boshiga (dushanba) boramiz
        weekday = today.weekday()  # 0 = dushanba
        this_monday = today - timedelta(days=weekday)

        # 2 hafta oldingi dushanbani topamiz
        start_date = this_monday - timedelta(weeks=2)
        end_date = this_monday + timedelta(days=6)  # Bu haftaning yakshanbasi

        return start_date, end_date

    def generate_report(self, request):

        # === 1. Aggregated Queryset ===
        stats = (
            GroupStatistics.objects.filter(
                date__range=self.get_last_two_weeks_range()
            )
            .values("group__title", "group__username", "date")
            .annotate(
                members=Sum("members"),
                total_posts=Sum("total_posts"),
                total_comments=Sum("total_comments"),
                deleted_posts=Sum("deleted_posts"),
                views=Sum("views"),
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
        }, inplace=True)
        df['Sana'] = pd.to_datetime(df['Sana'])

        # === 3. Formatlab chiqarish ===
        display_rows = []
        for guruh_nomi, guruh_df in df.groupby('Guruh'):
            display_rows.append({
                'Guruh': f"Guruh: {guruh_nomi}",
                'Username': '', 'Members': '', 'Postlar': '',
                'Izohlar': '', 'O‘chirilgan postlar': '', 'Ko‘rishlar': '', 'Sana': '',
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
        filename = f"hisobot_{date.today()}.xlsx"
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
