from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers



logger = setup_logging()





def get_lm_manager():
    '''возвращает экз класса менеджера'''
    return db_managers.LandMarkManager()

async def get_current_lm_query(session:AsyncSession, lm_id:int):
    '''обращается  к менеджеру БД банера и возвращает lm по id'''
    try: 
        lm_db_manager = get_lm_manager()
        current_lm = await lm_db_manager.get(session, id=lm_id)
        return current_lm
    except Exception as err:
        logger.error(f"Ошибка при запросе по lm с id {lm_id} : {err}")
        return None
        
async def get_all_lm_query(session:AsyncSession):
    try: 
        lm_db_manager = get_lm_manager()
        all_lm = await lm_db_manager.get_all(session)
        return all_lm
    except Exception as err:
        logger.error(f"Ошибка при запросе по выводу ВСЕХ lm : {err}")
        return None
    
    
    