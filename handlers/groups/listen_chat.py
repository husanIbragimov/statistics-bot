from aiogram import Bot, Router
from aiogram.types import Message
from telethon import TelegramClient

from filters import IsGroup
from utils.db.models import Group, GroupStatistics


router = Router()
router.message.filter(IsGroup())

@router.message()
async def message_post_handler(message: Message, bot: Bot):
    group, _ = await Group.get_or_create(
        id=message.chat.id,
        defaults={
            'title': message.chat.title,
            'username': message.chat.username,
            'who_added_id': message.from_user.id,
            'group_type': message.chat.type,
        }
    )
    if message.sender_chat:
        if message.chat.id != message.sender_chat.id:
            group.parent_id = message.sender_chat.id
            await group.save()
    obj, _ = await GroupStatistics.get_or_create(
        group_id=group.parent_id,
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
