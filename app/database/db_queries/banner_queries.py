from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers



logger = setup_logging()





def get_banner_manager():
    '''возвращает экз класса менеджера'''
    return db_managers.BannerManager()

async def get_current_banner_query(session:AsyncSession, banner_name:str='main_theme'):
    '''обращается  к менеджеру БД банера и возвращает банер по указанному имени'''
    try: 
        banner_db_manager = get_banner_manager()
        current_banner = await banner_db_manager.get(session, name=banner_name)
        return current_banner
    except Exception as err:
        logger.error(f"Ошибка при запросе по баннеру {banner_name} : {err}")
        return None
        
    
    