from aiogram import Bot, Router, F
from aiogram.types import Message, ChatMemberUpdated

from data import config
from filters import IsChannel
from utils.db.models import User, Group, GroupStatistics

router = Router()
router.message.filter(IsChannel())

@router.message()
async def bot_add_groups(message: ChatMemberUpdated, bot: Bot):
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
        total = await GroupStatistics.get_or_none(
            group_id=message.chat.id,
            date=message.date,
            status="daily",
        )
        await GroupStatistics.update_or_create(
            group_id=message.chat.id,
            date=message.date,
            status="daily",
            defaults={
                "members": await bot.get_chat_member_count(message.chat.id),
                "total_posts": total.total_posts if total.total_posts == 0 else total.total_posts + 1,
                "total_comments": 0
            }
        )
    except Exception as e:
        print(f"Error in bot_add_groups: {e}")
        await bot.send_message(
            chat_id=config.ADMINS[0],
            text=f"Error in bot_add_groups: {e}\nBot {message.chat.title} dan o'chirildi!"
        )

@router.message(F.chat.type == "channel")
async def channel_post_handler(message: Message, bot: Bot):
    stats, _ = await GroupStatistics.get_or_create(
        group_id=message.chat.id,
        date=message.date,
        status="daily",
        defaults={
            "members": await bot.get_chat_member_count(message.chat.id),
        }
    )
    total_posts = stats.total_posts + 1
    await GroupStatistics.filter(
        date=message.date,
        group_id=message.chat.id,
        status="daily"
    ).update(
        members=await bot.get_chat_member_count(message.chat.id),
        total_posts=total_posts,
    )
