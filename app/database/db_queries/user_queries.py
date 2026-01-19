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
        user_db_manager = get_user_manager()
        creating_result = await user_db_manager.create(session, user_info)
        return creating_result
    except Exception as err:
        logger.error(f"Ошибка при создании нового юзера с инфой из FSM : {user_info} : {err}")
        return None
        
async def get_current_user_query(session:AsyncSession, user_id:int):
    try: 
        user_db_manager = get_user_manager()
        current_user = await user_db_manager.get(session, id=user_id)
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