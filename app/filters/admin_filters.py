
from aiogram.types import Message
import os
from dotenv import load_dotenv
from aiogram.filters import Filter
from app.utils.env_utils import check_admin

load_dotenv()




class AdminFilter(Filter):
    '''фильтр для админов, что бы в хэндлеры админов попадали запросы 
    только от юзеров которые являются админами(список с их ID в .env)'''
    async def __call__(self, message:Message)->bool:
        result = await check_admin(message) # если админ то True иначе False
        return result
    
# async def check_admin(message:Message)->bool:
#     '''проверка юзера на админа по его id'''
#     return message.from_user.id == int(os.getenv('ADMIN_ID'))