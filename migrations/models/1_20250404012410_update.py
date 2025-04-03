from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "channels" ADD "parent_id" BIGINT;
        ALTER TABLE "channels" ADD CONSTRAINT "fk_channels_channels_b71f3a1b" FOREIGN KEY ("parent_id") REFERENCES "channels" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "channels" DROP CONSTRAINT IF EXISTS "fk_channels_channels_b71f3a1b";
        ALTER TABLE "channels" DROP COLUMN "parent_id";"""
