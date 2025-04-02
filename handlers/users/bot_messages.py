from aiogram import Router
from aiogram.types import Message
from aiogram import F
from keyboards import reply, builders, inline, fabrics
from data.subloader import get_json
from filters import IsPrivateChat


router = Router()
router.message.filter(IsPrivateChat())


@router.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)
