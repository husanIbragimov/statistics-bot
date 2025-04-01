from loader import bot, dp

async def on_shutdown_notify():
    """Bot to‘xtatilganda bajariladigan funksiya"""
    await dp.storage.close() 
    await bot.session.close()
    print("✅ Bot to‘xtatildi.")
