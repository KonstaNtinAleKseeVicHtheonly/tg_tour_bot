from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers



logger = setup_logging()




admin_inline_main_menu = InlineKeyboardMarkup([
                                        # Первый ряд: две кнопки
                                        [
                                            InlineKeyboardButton("меню", callback_data='admin_menu'),
                                            InlineKeyboardButton("show_me", callback_data='show_me'),
                                            InlineKeyboardButton("о нас", callback_data='about')
                                        ],
                                        [
                                            InlineKeyboardButton("Все админы", callback_data="show_admins"),
                                        ]
                                    ])

admin_inline_interaction_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('показать туры', callback_data='show_all_tours'), InlineKeyboardButton('показать достопримечательности', callback_data='show_all_lm')],
        [InlineKeyboardButton(text='назад',callback_data='admin_menu')]],resize_keyboard=True)


async def all_landmarks_kb(session:AsyncSession):
    '''по запросу из БД показывает в кнопках все достопримечательности'''
    try:
        lm_db_manager = db_managers.LandMarkManager()
        all_lm = await lm_db_manager.get_all(session)
        if not all_lm:
            return InlineKeyboardMarkup([[InlineKeyboardButton("пока что их нет", callback_data="show_all_lm")]])
        all_lm_kb = InlineKeyboardBuilder()
        for lm in all_lm:
            all_lm_kb.add(InlineKeyboardButton(f"{lm.name}", callback_data=f"show_landmark_{lm.id}"))
        all_lm_kb.row(InlineKeyboardButton(text='назад',callback_data="show_all_lm"))
        return all_lm_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех LM: {err}")
        return False
    
async def current_landmark_db(session : AsyncSession, lm_id:int):
    '''из базы берет по Id нужную достопримеательность и формирует клаву на изменение, обновление LM'''
    current_lm_kb = InlineKeyboardMarkup([[InlineKeyboardButton('изменить', callback_data=f"change_lm_{lm_id}"),InlineKeyboardButton('удалить', callback_data=f"delete_lm_{lm_id}")],
                                          [InlineKeyboardButton('назад', callback_data="show_all_lm")]], resize_keyboard=True)
    
