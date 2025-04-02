from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "group" ADD "group_id" BIGINT NOT NULL UNIQUE;
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_group_group_i_72dd4a" ON "group" ("group_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_group_group_i_72dd4a";
        ALTER TABLE "group" DROP COLUMN "group_id";"""
