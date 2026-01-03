from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import User
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging

logger = setup_logging()



class UserManager(BaseManager):
    
        def __init__(self):
                super().__init__(User)
    
        
    # async def get_by_telegram_id(self, session: AsyncSession):
    #     user_check = await self.exists(session)
    #     if user_check:
    #         return user_check
    #     raise ValueError("Не найден данный юзер в Базе")

    # async def exists(self, session:AsyncSession, telegram_id:int)->bool|User:
    #     current_user = await session.scalars(select(self.model).where(self.model.telegram_id==telegram_id))
    #     result = current_user.first()
    #     if result is None:
    #         logger.warning(f"Данного юзера с tg_id : {telegram_id} не существует")
    #         return False
    #     logger.info(f"Юзер с tg_id {telegram_id} есть в БД")
    #     return result