from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Landmark
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging

logger = setup_logging()



class LandMarkManager(BaseManager):

        def __init__(self):
                super().__init__(Landmark)
