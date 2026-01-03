from logging.config import fileConfig


from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
import os
import asyncio
from dotenv import load_dotenv
from alembic import context
from sqlalchemy.engine import Connection
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
#DB
from app.database.all_models.models import Base, User, Order, Tour, Landmark,TourLandmarkAssociation


load_dotenv()


DB_URL = os.getenv("DB_URL_Postgre")  # что бы alembic.ini автоматически брад из .env ссылку на БД
if not DB_URL:
    raise ValueError("DB_URL_POSTGRE environment variable is not set")



config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    
# Получаем URL из переменной окружения

config.set_main_option('sqlalchemy.url', DB_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
        
# 🔽 ЭТУ ФУНКЦИЮ НУЖНО ОПРЕДЕЛИТЬ!
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_server_default=True) # учитываем значение по умолчанию
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()
    


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
