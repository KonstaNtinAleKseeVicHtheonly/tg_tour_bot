from typing import Callable, Dict, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker



class DBSession(BaseMiddleware):
    '''мидлварь передачи сессии в хэндлер для упрощенного взаимодействия в бд(что бы каждый
    раз не нужно было вручную подключаться к сессии)'''
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool # при любым взаимодействием с БД будет инициализироваться новая сессия
    
    async def __call__(self,handler:Callable[[TelegramObject, Dict[str,Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data : Dict[str, Any])->Any:
        async with self.session_pool() as session:
            data['session'] = session # передача сесии в хэндлер
            return await handler(event,data)