from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers
from app.database.all_models.models import Landmark



logger = setup_logging()




async def all_landmarks_kb(all_lm):
    '''по запросу из БД показывает в кнопках все достопримечательности'''
    try:
        if not all_lm:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что их нет", callback_data="admin_interactive_menu")]])
        all_lm_kb = InlineKeyboardBuilder()
        for lm in all_lm:
            all_lm_kb.add(InlineKeyboardButton(text = f"{lm.name}", callback_data=f"show_landmark_{lm.id}"))
        all_lm_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
        return all_lm_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех LM: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])

    
    
def current_landmark_kb(lm_id:int):
    '''берет по Id нужную достопримеательность и формирует клаву на изменение, обновление LM'''
    current_lm_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'изменить', callback_data=f"change_lm_{lm_id}"),InlineKeyboardButton(text = 'удалить', callback_data=f"delete_lm_{lm_id}")],
                                          [InlineKeyboardButton(text = 'назад', callback_data="show_all_lm")]])
    return current_lm_kb
    
