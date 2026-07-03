import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from app.database import Base
from app.models import *  # noqa: F401,F403

config = context.config
target_metadata = Base.metadata


def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(target_metadata.create_all)

    asyncio.run(do_migrations())


run_migrations_online()
