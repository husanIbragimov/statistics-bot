from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated

from data.config import ADMINS
from utils.db.models import GroupStatistics, Group

router = Router()
router.message.filter()

@router.channel_post()
async def bot_add_groups(message: ChatMemberUpdated, bot: Bot):
    try:
        await Group.get_or_create(
            id=message.chat.id,
            defaults={
                "title": message.chat.title,
                "group_type": message.chat.type,
                "username": message.chat.username or None,
                "date_joined": message.date,
            }
        )
        total = await GroupStatistics.filter(
            group_id=message.chat.id,
            date=message.date,
        ).first()
        await GroupStatistics.update_or_create(
            group_id=message.chat.id,
            date=message.date,
            defaults={
                "members": await bot.get_chat_member_count(message.chat.id),
                "total_posts": 1 if not total else (total.total_posts + 1),
                "total_comments": 0
            }
        )
    except Exception as e:
        print(f"Error in bot_add_groups: {e}")
        for admin in ADMINS:
            await bot.send_message(
                chat_id=admin,
                text=f"Error: {e}\n\nKanal: {message.chat.title}!"
            )
