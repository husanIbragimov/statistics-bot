import logging
from loader import bot
from data.config import ADMIN_ID

async def on_startup_notify():
    bot_ = await bot.me()
    print(f"✅ Bot ishga tushdi | id: {bot_.id} | username: @{bot_.username} \n")
    
    for admin in ADMIN_ID:
        try:
            await bot.send_message(admin, "Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)