from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from tortoise import Tortoise
from data.config import BOT_TOKEN, DATABASE_CONFIG


bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode="HTML") 
)

dp = Dispatcher()

async def init_db():
    await Tortoise.init(config=DATABASE_CONFIG)
    await Tortoise.generate_schemas()
