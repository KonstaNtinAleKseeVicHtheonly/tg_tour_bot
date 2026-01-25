from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers
from app.database.all_models.models import OrderStatus, Order



logger = setup_logging()





def get_order_manager():
    '''возвращает экз класса менеджера'''
    return db_managers.OrderManager()

async def get_current_order_query(session:AsyncSession, order_id:int)->Order:
    '''обращается  к менеджеру БД Order и возвращает  по id'''
    try: 
        order_db_manager = get_order_manager()
        current_order = await order_db_manager.get(session, id=order_id)
        return current_order
    except Exception as err:
        logger.error(f"Ошибка при запросе по order с id {order_id} : {err}")
        return None
        
async def show_order_detailed_info_query(session:AsyncSession, current_order_id:int, skip_fields:list[str])->str:
    '''по указанным китериям заказа найдет его через менедже и через метод менеджера
    выведет развернутую инфу'''
    try: 
        order_db_manager = get_order_manager()
        current_order_info = await order_db_manager.show_detailed_info_for_user(session, current_order_id, skip_fields)
        return current_order_info
    except Exception as err:
        logger.error(f"Ошибка при запросе по order с id {current_order_id} : {err}")
        return None
    
async def cancel_order_query(session:AsyncSession, order_criterion:int|Order):
    try: 
        order_db_manager = get_order_manager()
        current_order_cancel_result = await order_db_manager.cancel_order(session,order_criterion)
        return current_order_cancel_result
    except Exception as err:
        logger.error(f"Ошибка при запросе по order с критерием {order_criterion} : {err}")
        return None