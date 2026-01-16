from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from project_logger.loger_configuration import setup_logging

logger = setup_logging()

def create_inline_kb(buttons_data:list[dict], row_width=1):
    '''Создает клавиатуру по принимаемым на вход данным для кнопок в виде списка словаре'''
    adaptive_kb = InlineKeyboardBuilder()
    for current_button in buttons_data:
        current_button_text = current_button.get('text', None)
        current_button_callback = current_button.get('callback_data', None)
        if not current_button_text and not current_button_callback:
            logger.error("При создании клавы в словаре должны быть ключи 'text' и 'callback_data'")
            raise ValueError(f"введи валидные ключи а не {buttons_data}")
        adaptive_kb.add(InlineKeyboardButton(text=current_button_text, callback_data=current_button_callback))
        adaptive_kb.adjust(row_width) # натройка по количеству рядов
    return adaptive_kb.as_markup()

