# from aiogram import Router, types, Bot
# from datetime import timedelta
# import pandas as pd
# from aiogram.types import FSInputFile
#
# from utils.db.models import Group, GroupStatistics
# from aiogram.filters import Command, CommandStart
# from filters import IsPrivateChat
#
# router = Router()
# router.message.filter(IsPrivateChat())
#
#
# @router.message(Command("report"))
# async def get_reports(message: types.Message, bot: Bot):
#     today = message.date.date()
#     last_2_months = today - timedelta(days=60)
#     file_name = f"hisobot-{last_2_months}_{today}.xlsx"
#     await message.answer("Iltimos, kuting, hisobot tayyorlanmoqda...")
#     group_stats = await (
#         GroupStatistics.filter(
#             date__gte=last_2_months,
#             date__lte=today,
#         )
#         .select_related("group")
#         .values(
#             'group__title',
#             'group__username',
#             # 'post_avg',
#             # 'comment_avg',
#             'members',
#             'total_posts',
#             'total_comments',
#             'deleted_posts',
#             'views'
#             'date',
#         ))
#     stat_df = pd.DataFrame(tuple(group_stats))
#     stat_df.to_excel(f"media/reports/{file_name}", index=False)
#     await message.answer_document(
#         FSInputFile(f"media/reports/{file_name}"),
#         filename=f"{file_name}",
#     )

import os
from aiogram import Router, types, Bot, F
from datetime import date, timedelta
import pandas as pd
from aiogram.types import FSInputFile

from data import config
from utils.db.models import GroupStatistics
from aiogram.filters import Command
from filters import IsPrivateChat, IsAdmin

router = Router()
router.message.filter(IsPrivateChat())


@router.message(Command("report"), IsAdmin())
async def get_reports(message: types.Message):
    await message.answer("Iltimos, kuting, hisobot tayyorlanmoqda...")
    # === 1. Sana oraliqlarini aniqlash ===
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    start_date = start_of_week - timedelta(weeks=4)

    # === 2. Hisobot faylini tayyorlash ===
    file_name = f"hisobot-{start_date}_{today}.xlsx"
    report_dir = "media/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, file_name)

    # === 3. Ma'lumotlarni olish (Query optimizatsiya) ===
    stats = await GroupStatistics.filter(
        date__range=(start_date, today)
    ).select_related("group").values(
        "group__title", "group__username", "members",
        "total_posts", "total_comments", "deleted_posts",
        "views", "date"
    )

    if not stats:
        return await message.answer("Ma'lumot topilmadi.")

    # === 4. DataFrame yaratish ===
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

    # === 5. Guruhlab chiqariladigan shaklni tayyorlash ===
    display_rows = []

    for guruh_nomi, guruh_df in df.groupby('Guruh'):
        # Guruh sarlavhasi
        display_rows.append({
            'Guruh': f"Guruh: {guruh_nomi}",
            'Username': '', 'Members': '', 'Postlar': '',
            'Izohlar': '', 'O‘chirilgan postlar': '', 'Ko‘rishlar': '', 'Sana': ''
        })

        # Sana bo‘yicha saralash
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

    # === 6. Haftalik o‘rtacha ko‘rsatkichlar ===
    weekly_avg = (
        df.groupby(['Guruh', 'Username'])[
            ['Postlar', 'Izohlar', 'O‘chirilgan postlar', 'Ko‘rishlar']
        ]
        .mean()
        .round()
        .reset_index()
    )

    # === 7. Excel faylga yozish ===
    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        formatted_df.to_excel(writer, sheet_name='Hisobot', index=False)
        weekly_avg.to_excel(writer, sheet_name='Haftalik', index=False)

    # === 8. Foydalanuvchiga yuborish ===
    await message.answer_document(FSInputFile(report_path), caption="✅ Hisobot tayyor!")
