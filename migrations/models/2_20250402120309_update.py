from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "group" ALTER COLUMN "group_id" TYPE VARCHAR(16) USING "group_id"::VARCHAR(16);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "group" ALTER COLUMN "group_id" TYPE BIGINT USING "group_id"::BIGINT;"""
