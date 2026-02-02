from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import TourLandmarkAssociation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging
from sqlalchemy.orm import selectinload
logger = setup_logging()



class TourLMAssociationManager(BaseManager):
    
    
    
    def __init__(self):
                super().__init__(TourLandmarkAssociation)

    async def get_current_association(self, session: AsyncSession, tour_id: int, landmark_id: int):
        '''выводит ассоциацию по указанным id'''
        if not await self.exists(session, tour_id=tour_id, landmark_id=landmark_id):
            return None
        stm = select(self.model).options(selectinload(self.model.tour), selectinload(self.model.landmark)).where(self.model.tour_id==tour_id,self.model.landmark_id==landmark_id)
        current_association = await session.execute(stm)
        result = current_association.scalar_one_or_none() # объекты tour и landmark из текущей строки 
        return result
    
        
    async def show_ordered_associations_with_names(self, session:AsyncSession)->list:
        '''вернет список объектов (tour,ladnmark) по строкам из всех строк с табллицей ассоциацмй'''
        try:
            stm = select(self.model).options(selectinload(self.model.tour), selectinload(self.model.landmark)).order_by(self.model.tour_id, self.model.landmark_id)
            result = await session.execute(stm)
            associations = result.scalars().all()
            return associations if associations else []
        except Exception as err:
            logger.error(f"ошибка в {self.model.__name__} при поптыке вывести соритрованные объекты tour и lanmark : {err}")
            return []

