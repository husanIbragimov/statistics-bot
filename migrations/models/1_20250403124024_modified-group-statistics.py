from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "group_statistics" ADD "date" DATE;
        ALTER TABLE "group_statistics" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;
        CREATE INDEX IF NOT EXISTS "idx_group_stati_date_920ebb" ON "group_statistics" ("date");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_group_stati_date_920ebb";
        ALTER TABLE "group_statistics" DROP COLUMN "date";
        ALTER TABLE "group_statistics" ALTER COLUMN "created_at" TYPE DATE USING "created_at"::DATE;"""
