from aiogram import Bot, Dispatcher
import asyncio
#конфигурации
from dotenv import load_dotenv
from project_logger.loger_configuration import setup_logging
import os
# системные утилиты
#роутеры
from app.handlers.user_handlers import user_handler
from app.handlers.admin_handlers import admin_handler
# database
from app.database.models import async_db_main
#кэширование
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis
#edis



load_dotenv()

logger = setup_logging()




async def on_startup(dispatcher:Dispatcher):
    '''Метод для создания подключения к SQLite при запуске бота'''
    logger.info('Подключение к СУБД SQLite')
    try:
        await async_db_main()
        logger.info("ПОдключение выполнено успешно")
    except Exception as err:
        logger.critical(f"Ошибка подключения к СУБД SQLite : {err}")
        return False
    

async def on_shutdown(dispatcher:Dispatcher):
    '''Метод для создания подключения к SQLite при запуске бота'''
    logger.info('Окончание работы бота')

    
    
    
async def main():
    

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    # # Кэширование через MemoryStorage
    # storage = MemoryStorage()
    # Кэширование через Redis
    redis_host = os.getenv('REDIS_HOST','redis')
    redis_port = os.getenv('REDIS_PORT','6379')
    redis_db = os.getenv('REDIS_DB')
    redis_client = await aioredis.from_url(f"redis://{redis_host}:{redis_port}/{redis_db}")
    dp = Dispatcher(storage=RedisStorage(redis_client))
    dp.include_routers(user_handler, admin_handler)
    dp.startup.register(on_startup) # подключение к БД
    dp.shutdown.register(on_shutdown)
    
    await bot.delete_webhook(drop_pending_updates=True)# сброс предыдущих апдейтов при перезапуске бота
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        logger.info("запуск основного цикла main")
        asyncio.run(main()) # отравка запроаса на сервре телеграма на наличеи новых сообщений, обнволений в нашем боте,если ответов нет то функция просто ожидает новых сообщений
        logger.info("окончание работы основного цикла main")
    except KeyboardInterrupt:
        logger.warning("Работа бота была остановлена через скрипт и ctrl + C")
    except Exception as err:
        logger.critical(f"сработала ошибка {err} в теле основного цикла main")
