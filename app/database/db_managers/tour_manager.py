from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Tour, TourLandmarkAssociation
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging
from sqlalchemy.orm import selectinload, joinedload

logger = setup_logging()



class TourManager(BaseManager):
        '''менеджер для рабоыт с моделью Tour, содержит метод по отображению
        landmark текущих туров(через смежную таблицу many to many)'''
        
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
        
        async def update_from_state(self,session: AsyncSession, state_data: dict):
                '''метод для обновления данных таблицы админом через FSM
                (уарпвление обновлением данных через админ режим в боте)'''
                try:
                        tour_id = state_data['id']
                        param = state_data['param']
                        new_value = state_data.get('new_value')
                        
                        return await self.update(
                                session,
                                {'id': tour_id},
                                {param: new_value}
                        )
                except Exception:
                        logger.error("Ошибка произошла при обновлении данных тура через админ панель в боте !")
                        return False

        async def can_book(self,session: AsyncSession, tour_id: int, quantity: int) -> bool|tuple:
                """Проверка возможности бронирования по переданному количесту мест"""
                try:
                        logger.info(f"начало проверки возможности заброинрвоать {quantity} мест")
                        if quantity <= 0:
                                return False, "Количество мест должно быть положительным"
                        current_tour = await self.get(session, id=tour_id)
                        if not current_tour:
                                return current_tour # не найден тур с таким id
                        if quantity > current_tour.max_people:
                                logger.warning(f"Максимальное количество мест: {current_tour.max_people}")
                                return False, f"В данном туре всего: {current_tour.max_people} мест, введите меньше"
                        if quantity > (current_tour.max_people -current_tour.booked_seats):# количество доступных мест
                                logger.warning("указанное количество мест превышает доступные места")
                                return False, f"Осталось только {current_tour.max_people -current_tour.booked_seats} мест, введите меньшее количество"
                        return True
                except Exception as err:
                        logger.error(f"Ошибка при расчете мест для броинрования юезра:{err}")
                        return False, "Ошибка на стороне сервера, повторите бронирование позже"
        
        async def calculate_total_price(self,session: AsyncSession, tour_id: int,place_number:int) -> int:
                """Рассчитать общую стоимость исходя из заданного количества мест"""
                #!!! tour.price_per_persion - строковый вариант формата 200 byn !!!
                current_tour = await self.get(session, id=tour_id)
                if not current_tour:
                        return current_tour # не найден тур с таким id
                price_str = current_tour.price_per_person.split()[0] # цена в цифре без BYN
                logger.warning(f"Расчет цены при {place_number} купленных мест и {price_str} цены за место") 
                if price_str.isdigit():
                        price_value = int(price_str)
                else:
                        price_value = float(price_str)
                return price_value * place_number
