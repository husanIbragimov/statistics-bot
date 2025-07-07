from aiogram import Bot, Router
from aiogram.enums import ParseMode
from aiogram.types import Message

from data.config import ADMINS
from utils.db.models import Group

router = Router()
router.message.filter()


@router.my_chat_member()
async def join_channel(message: Message, bot: Bot):
    text = f"""
👥 Yangi guruh qo'shildi: {message.chat.title}
🆔 Guruh ID: `{message.chat.id}`
👤 Qo'shgan foydalanuvchi: [{message.from_user.full_name}]({message.from_user.url})
    """

    for admin in ADMINS:
        await bot.send_message(
            chat_id=admin,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )

    group, _ = await Group.get_or_create(
        id=message.chat.id,
        defaults={
            'title': message.chat.title,
            'username': message.chat.username,
            'who_added_id': None,
            'group_type': message.chat.type,
        }
    )
