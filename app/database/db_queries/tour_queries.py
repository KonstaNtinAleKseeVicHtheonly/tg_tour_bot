from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers



logger = setup_logging()





def get_tour_manager():
    '''возвращает экз класса менеджера'''
    return db_managers.TourManager()

async def get_current_tour_query(session:AsyncSession, tour_id:int):
    '''обращается  к менеджеру БД банера и возвращает lm по id'''
    try: 
        tour_db_manager = get_tour_manager()
        current_tour = await tour_db_manager.get(session, id=tour_id)
        return current_tour
    except Exception as err:
        logger.error(f"Ошибка при запросе по тура с id {tour_id} : {err}")
        return None
        
async def get_all_tours_query(session:AsyncSession):
    try: 
        tours_db_manager = get_tour_manager()
        all_tours = await tours_db_manager.get_all(session)
        return all_tours
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ туров : {err}")
        return None
    
async def get_tour_landmarks_query(session:AsyncSession, tour_id:int):
    '''обращается к специальному методу менеджера который вывовдит все связанный с указанным туром(id)
     достопримечательности'''
    try: 
        tours_db_manager = get_tour_manager()
        tour_landmarks = await tours_db_manager.get_tour_landmarks(session, tour_id)
        return tour_landmarks
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ туров : {err}")
        return None
     
async def get_tour_detailed_info_query(session:AsyncSession, tour_id:int, current_skip_fields:list[str]):
    '''обращается к специальному методу менеджера который вывовдит все связанный с указанным туром(id)
     достопримечательности'''
    try: 
        tours_db_manager = get_tour_manager()
        tour_detailed_info = await tours_db_manager.show_detailed_info_for_user(session, current_id=tour_id, skip_fields=current_skip_fields)
        return tour_detailed_info
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ туров : {err}")
        return None
     
async def can_book_query(session:AsyncSession, tour_id:int, place_quantity:int):
    '''по указанному числу мест определяет можно ли заброинровать указаное количество'''
    try: 
        tour_db_manager = get_tour_manager()
        booking_probability = await tour_db_manager.can_book(session, tour_id, place_quantity)
        return booking_probability
    except Exception as err:
        logger.error(f"Ошибка при расчете возможности заброинровать {place_quantity} мест в туре : {err}")
        return None
    
    
async def calculate_total_price_query(session: AsyncSession, tour_id: int,place_number:int) -> int:
        """Рассчитать общую стоимость исходя из заданного количества мест"""
        try: 
            tour_db_manager = get_tour_manager()
            booking_probability = await tour_db_manager.calculate_total_price(session, tour_id, place_number)
            return booking_probability
        except Exception as err:
            logger.error(f"Ошибка при расчете общей стоимости забронированных мест для тура : {err}")
            return None
        