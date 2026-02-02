from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
#
from dotenv import load_dotenv
import os
#логгер
from project_logger.loger_configuration import setup_logging
from app.database.all_models.models import Base
from sqlalchemy import text


load_dotenv()






engine = create_async_engine(os.getenv('DB_URL_Postgre'))

logger = setup_logging()

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def async_db_main():
    logger.info("ЗАпуск асинхронного движка для Postgres")
    async with engine.begin() as conn:
         # Проверяем текущую схему
        schema_result = await conn.execute(text("SELECT current_schema()"))
        current_schema = schema_result.scalar()
        logger.warning(f"Текущая схема БД: {current_schema}")
        await conn.run_sync(Base.metadata.create_all)# создание всех наследюущих от Base моделей
        
async def drop_db():
    logger.warning("Запуск процесса удаления БД")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)