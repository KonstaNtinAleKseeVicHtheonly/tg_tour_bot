from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Tour, TourLandmarkAssociation
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging
from sqlalchemy.orm import selectinload, joinedload

logger = setup_logging()



class TourManager(BaseManager):

        
        def __init__(self):
                super().__init__(Tour)
                
        async def get_tour_landmarks(self,session: AsyncSession, tour_id: int) -> list:
                """
                Жадная загрузка: сразу возвращает список объектов Landmark для тура
                """
                logger.info(f"ПОлучение landmarks, связанных с туром по его id : {tour_id}")
                # Правильная жадная загрузка
                stmt = (
                        select(self.model)
                        .where(self.model.id == tour_id)
                        .options(
                        selectinload(self.model.landmark_associations)  # загружаем associations
                        .joinedload(TourLandmarkAssociation.landmark)  # для каждой association загружаем landmark
                        )
                ) # собрали с таблицы все связанные с данным туром по id объекты

                
                result = await session.execute(stmt)
                tour = result.scalar_one_or_none() # готовый объект с всеми landmark связанными с tour_id
                if not tour:
                        logger.warning(f"не найдено landmarks по туру с id : {tour_id}")
                        return []  # тур не найден
                logger.info(f"для тура с id : {tour_id} найдены lanmdarks")
                # Сразу собираем и возвращаем список landmarks
                return [assoc.landmark for assoc in tour.landmark_associations if assoc.landmark] # возврааем список landmarks связанных с данным туром
        
        # async def get_tour_landmark_ids(session: AsyncSession, tour_id: int) -> list[int]:
        #         """ID достопримечательностей тура одной строкой"""
        #         return (await session.execute(
        #                 select(TourLandmarkAssociation.landmark_id)
        #                 .where(TourLandmarkAssociation.tour_id == tour_id)
        #         )).scalars().all()