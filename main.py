from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
# from aiogram.types import BotCommandScopeAllPrivateChats
import asyncio
#конфигурации
from dotenv import load_dotenv
from project_logger.loger_configuration import setup_logging
import os
# системные утилиты
from app.utils.bot_commands import set_public_commands
#роутеры
from app.handlers.tg_group.user_group import tg_group_handler
# админа
from app.handlers.admin import admin_main_handler, admin_lm_handler, admin_tour_handler, admin_tour_lm_association_handler, admin_banner_handler, admin_user_handler, admin_orders_handler
# юзерские
from app.handlers.user import user_main_handler, user_lm_handler, user_tour_handler, user_order_handler
 
# database
load_dotenv() # что бы переменне подгрузились на момент подключения файла, должно быть над конфигурацией подключени к БД!!!
from app.database.db_configurations.db_engine import async_db_main, drop_db, async_session
#кэширование
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis
# MiddleWare
from app.middlewares.db_middleware import DBSession



load_dotenv()

logger = setup_logging()




async def on_startup(dispatcher:Dispatcher):
    '''Метод для создания подключения к Postgres при запуске бота'''
    logger.info('Подключение к СУБД Postgres')
    
    try:
        run_param = False
        if run_param:
            await drop_db()
        await async_db_main()
        logger.info("ПОдключение выполнено успешно")
    except Exception as err:
        logger.critical(f"Ошибка подключения к СУБД Postgres : {err}")
        return False
    

async def on_shutdown(dispatcher:Dispatcher):
    '''Метод для создания подключения к SQLite при запуске бота'''
    logger.info('Окончание работы бота')

    
    
    
async def main():
    # Кэширование через Redis
    redis_host = os.getenv('REDIS_HOST','redis')
    redis_port = os.getenv('REDIS_PORT','6379')
    redis_db = os.getenv('REDIS_DB')
    redis_client = await aioredis.from_url(f"redis://{redis_host}:{redis_port}/{redis_db}")

    dp = Dispatcher(storage=RedisStorage(redis_client)) # для каждого отдельного юзера в чате будет вестись своя FSM
    bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp.startup.register(on_startup) # действия при началае работы бота (подключение к БД и прочее)
    dp.shutdown.register(on_shutdown) # действия при прекращении работы бота
    # хэндлеры админа
    dp.include_routers(admin_main_handler, admin_lm_handler, admin_tour_handler,admin_tour_lm_association_handler, admin_banner_handler, admin_user_handler, admin_orders_handler)
    # хэндлеры юзера 
    dp.include_routers(user_main_handler, user_lm_handler, user_tour_handler, user_order_handler)

    dp.update.middleware(DBSession(session_pool=async_session)) # мидлварь на автоматическое создание сессии при работе с БД

    
    await bot.delete_webhook(drop_pending_updates=True)# сброс предыдущих апдейтов при перезапуске бота
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())  # раскоментировать один раз что бы удалить старые команды юзера(стали не нужные)
    await set_public_commands(bot)# встроенное меню для всех юзеров
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        logger.info("запуск основного цикла main")
        asyncio.run(main()) # отравка запроаса на сервре телеграма на наличеи новых сообщений, обнволений в нашем боте,если ответов нет то функция просто ожидает новых сообщений
    except KeyboardInterrupt:
        logger.warning("Работа бота была остановлена через скрипт и ctrl + C")
    except Exception as err:
        logger.critical(f"сработала ошибка {err} в теле основного цикла main")
