from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Landmark
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging

logger = setup_logging()



class LandMarkManager(BaseManager):

        def __init__(self):
                super().__init__(Landmark)
                
        async def update_from_state(self,session: AsyncSession, state_data: dict):
                '''метод для обновления данных таблицы админом через FSM
                (уарпвление обновлением данных через админ режим в боте)'''
                try:
                        landmark_id = state_data['id']
                        param = state_data['param']
                        new_value = state_data.get('new_value')
                        
                        return await self.update(
                                session,
                                {'id': landmark_id},
                                {param: new_value}
                        )
                except Exception:
                        logger.error("Ошибка произошла при обновлении данных lanmdark через админ панель в боте !")
                        return False
