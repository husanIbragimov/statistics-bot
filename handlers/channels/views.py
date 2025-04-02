from typing import Union
from aiohttp import ClientSession
from aiogram import Bot, Router, F
from data import config
from aiogram.types import Message, ChatMember, ChatMemberUpdated
from pydantic.v1.class_validators import all_kwargs

from filters import IsChannel
from utils.db.models import User, Group, GroupStatistics


router = Router()
# router.message.filter(IsChannel())


@router.my_chat_member()
async def add_bot_group(message: Message, bot: Bot):
    user, added = await User.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            'username': message.from_user.username if message.from_user.username else None,
            'full_name': message.from_user.full_name,
        }
    )

    group, created = await Group.get_or_create(
        group_id=message.chat.id,
        defaults={
            'title': message.chat.title,
            'username': message.chat.username if message.chat.username else None,
            'who_added_id': user.id,
            'group_type': message.chat.type,
        }
    )
    group_statistics = await GroupStatistics.create(
        group_id=group.id,
        members=await bot.get_chat_member_count(message.chat.id, request_timeout=5),
        total_posts=bot.get_chat(message.chat.id),

    )
    await bot.send_message(
        chat_id=config.ADMINS,
        text=f"Bot added to group: {message.chat.title}\n"
             f"Group ID: {message.chat.id}\n"
             f"Members: {group_statistics.members}\n"
    )


@router.channel_post()
async def channel_post_handler(channel_post: Message):
    group, created = await Group.get_or_create(
        group_id=channel_post.chat.id
    )
    get = await GroupStatistics.get_or_none(
        group_id=group.id
    )
    await GroupStatistics.update_or_create(
        group_id=group.id,
        defaults={
            'total_posts': get.total_posts + 1
        }
    )



