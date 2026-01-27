from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers



logger = setup_logging()





def get_user_manager():
    '''возвращает экз класса менеджера'''
    return db_managers.UserManager()

async def _create_new_user_query(session:AsyncSession, user_info:dict[str:str]):
    '''после FSM в хэндлере user_handlers собиракет отправленную инфу юзером и через менеджер БД создает в базе 
    нового юзера с переданными в хэндлере параметрами'''
    '''обращается  к менеджеру БД банера и возвращает lm по id'''
    try: 
        logger.info(f"Начало регистрации юзера с данными:{user_info}")
        user_db_manager = get_user_manager()
        creating_result = await user_db_manager.create(session, user_info)
        return creating_result
    except Exception as err:
        logger.error(f"Ошибка при создании нового юзера с инфой из FSM : {user_info} : {err}")
        return None
        
async def get_current_user_query(session:AsyncSession, **params):
    try: 
        logger.warning(f"quey запрос на вывод юзера с параметрами {params}")
        user_db_manager = get_user_manager()
        current_user = await user_db_manager.get(session, **params)
        return current_user
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ туров : {err}")
        return None
    
async def check_user_existance(session : AsyncSession, user_tg_id:int)->bool:
    '''по тг id юзера через менеджера (метод exist) узнает существует ли юзер'''
    try: 
        user_db_manager = get_user_manager()
        user_exists = await user_db_manager.exists(session, telegram_id = user_tg_id)
        return user_exists
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ туров : {err}")
        return None
    
async def get_user_orders_query(session:AsyncSession, **user_params):
    '''по указанным параметрам показывает все заказа юзра'''
    try: 
        user_db_manager = get_user_manager()
        all_orders = await user_db_manager.show_user_orders(session, **user_params)
        return all_orders
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ заказов юзера : {err}")
        return None
    
    
async def _show_all_users_query(session:AsyncSession):
    '''query для админа. по указанным параметрам показывает все заказа юзра'''
    try: 
        user_db_manager = get_user_manager()
        all_users = await user_db_manager.get_all(session)
        return all_users
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ юзеров : {err}")
        return None
    
    
    