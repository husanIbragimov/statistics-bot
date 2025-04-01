import asyncio
from tortoise import Tortoise

from data.config import DATABASE_CONFIG

async def apply_migrations():
    await Tortoise.init(
        db_url=DATABASE_CONFIG["connections"]["default"],
        modules={"models": DATABASE_CONFIG["apps"]["models"]["models"]}  
    )
    await Tortoise.generate_schemas()
    print("✅ Migrations applied successfully!")

asyncio.run(apply_migrations())
