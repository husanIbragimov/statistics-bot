from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "telegram_id" BIGINT NOT NULL UNIQUE,
    "username" VARCHAR(64),
    "full_name" VARCHAR(255),
    "age" INT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_users_telegra_ab91e9" ON "users" ("telegram_id");
CREATE TABLE IF NOT EXISTS "group" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100),
    "group_type" VARCHAR(255),
    "username" VARCHAR(100) UNIQUE,
    "date_joined" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "who_added_id" BIGINT REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "groupstatistics" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "members" INT NOT NULL DEFAULT 0,
    "total_posts" INT NOT NULL DEFAULT 0,
    "total_comments" INT NOT NULL DEFAULT 0,
    "deleted_posts" INT NOT NULL DEFAULT 0,
    "status" VARCHAR(8) DEFAULT 'daily',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "group_id" BIGINT NOT NULL REFERENCES "group" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
