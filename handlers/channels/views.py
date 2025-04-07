from typing import Union
from datetime import date
from aiogram import Bot, Router, F
from data import config
from aiogram.types import Message, ChatMember, ChatMemberUpdated

from filters import IsChannel
from utils.db.models import User, Group, GroupStatistics


router = Router()
router.message.filter(IsChannel())

@router.my_chat_member()
async def bot_add_groups(message: Message, bot: Bot):
    try:
        await User.get_or_create(
            id=message.from_user.id,
            telegram_id=message.from_user.id,
            defaults={
                'username': message.from_user.username if message.from_user.username else None,
                'full_name': message.from_user.full_name,
            }
        )

        await Group.get_or_create(
            id=message.chat.id,
            defaults={
                'title': message.chat.title,
                'username': message.chat.username if message.chat.username else None,
                'who_added_id': message.from_user.id,
                'group_type': message.chat.type,
            }
        )
        await GroupStatistics.get_or_create(
            group_id=message.chat.id,
            date=message.date,
            status="daily",
            defaults={
                "members": await bot.get_chat_member_count(message.chat.id),
                "total_posts": 0,
                "total_comments": 0
            }
        )
    except Exception as e:
        print(f"Error in bot_add_groups: {e}")
        await bot.send_message(
            chat_id=config.ADMINS[0],
            text=f"Error in bot_add_groups: {e}\nBot {message.chat.title} dan o'chirildi!"
        )

@router.channel_post()
async def channel_post_handler(message: Message, bot: Bot):
    stats, _ = await GroupStatistics.update_or_create(
        group_id=message.chat.id,
        date=message.date,
        status="daily",
        defaults={
            "members": await bot.get_chat_member_count(message.chat.id, request_timeout=5),
        }
    )
    total_posts = stats.total_posts + 1
    await GroupStatistics.update_or_create(
        group_id=message.chat.id,
        date=message.date,
        status="daily",
        defaults={
            "members": await bot.get_chat_member_count(message.chat.id, request_timeout=5),
            "total_posts": total_posts,
        }
    )
