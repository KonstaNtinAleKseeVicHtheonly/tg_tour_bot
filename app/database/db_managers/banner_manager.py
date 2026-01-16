from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Banner
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging

logger = setup_logging()



class BannerManager(BaseManager):
    '''менеджер для рабоыт с моделью банеров к постам в телеге'''

    def __init__(self):
            super().__init__(Banner)
            
