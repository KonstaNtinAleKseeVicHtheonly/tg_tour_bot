from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import TourLandmarkAssociation
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging

logger = setup_logging()



class TourLMAssociationManager(BaseManager):
    
    
    
    def __init__(self):
                super().__init__(TourLandmarkAssociation)

    async def get_association(self, session: AsyncSession, tour_id: int, landmark_id: int):
        
        stm = select(TourLandmarkAssociation).where(TourLandmarkAssociation.tour_id==tour_id,
                                                                            TourLandmarkAssociation.landmark_id==landmark_id)
        association = await session.execute(stm)
        result = association.scalar_one_or_none()
        return result