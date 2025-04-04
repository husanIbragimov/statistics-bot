from typing import Union
from datetime import date
from aiogram import Bot, Router, F
from data import config
from aiogram.types import Message, ChatMember, ChatMemberUpdated

from filters import IsChannel
from utils.db.models import User, Group, GroupStatistics


router = Router()
# router.message.filter(IsChannel())


@router.my_chat_member()
async def add_bot_group(message: Message, bot: Bot):
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
        group_id=message.chat.id,
        defaults={
            'title': message.chat.title,
            'username': message.chat.username if message.chat.username else None,
            'who_added_id': message.from_user.id,
            'group_type': message.chat.type,
        }
    )
    await GroupStatistics.update_or_create(
        group_id=str(message.chat.id),
        date=message.date,
        status="daily",
        defaults={
            "members": await bot.get_chat_member_count(message.chat.id),
            "total_posts": 0,
            "total_comments": 0
        }
    )

@router.channel_post()
async def channel_post_handler(message: Message, bot: Bot):


    stats, _ = await GroupStatistics.get_or_create(
        group_id=str(message.chat.id),
        status="daily",
    )
    print(message)
    total_posts = stats.total_posts + 1
    await GroupStatistics.update_or_create(
        group_id=str(message.chat.id),
        date=message.date,
        status="daily",
        defaults={
            "members": await bot.get_chat_member_count(message.chat.id, request_timeout=5),
            "total_posts": total_posts,
        }
    )


@router.message()
async def message_post_handler(message: Message, bot: Bot):
    print(message)
    print(message.sender_chat.id)
    print(message.chat.id)
    obj, _ = await GroupStatistics.get_or_create(
        group_id=str(message.chat.id),
        date=message.date,
        status="daily",
        defaults={
            "members": await bot.get_chat_member_count(message.chat.id, request_timeout=5),
            "total_comments": 1,
            "total_posts": 1
        }
    )
    obj.total_comments += 1
    await obj.save()
