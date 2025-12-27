import os
from dotenv import load_dotenv
from project_logger.loger_configuration import setup_logging
from aiogram.types import Message

logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env


async def _get_admins_id()->list:
    '''асинхронно берет id всех админов из .env делает их числами и возвращает в списке'''
    ids = os.getenv('ADMIN_ID', '').strip()
    if not ids:
        logger.warning("В env нет инфы о id Админов")
        return []
    logger.info("инфа об id одминов успешно взята из env")
    return [admin_id.strip() for admin_id in ids.split(',')]
    
async def check_admin(message : Message)->bool:
    ''''Принимает сообщение и проверяет находится ли текущий юзер в списках амдинов и если находится то вернет True иначе False'''
    admins_id = await _get_admins_id()
    
    if str(message.from_user.id) in admins_id:
        return True
    return False