from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers
from keyboards.base_keyboards import create_inline_kb



logger = setup_logging()




user_inline_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Список всех туров", callback_data='show_all_tours')],
        [InlineKeyboardButton(text="Информация об аккаунте", callback_data='show_me')],
        [InlineKeyboardButton(text="Ваши заказы", callback_data='show_user_orders')],
        [InlineKeyboardButton(text="О нас", callback_data='about_company')]

    ]
)

async def main_menu_post():
    '''возвращает фотку текст и клавиатуру для главного меню, видное юзеру'''


async def create_menu_content(session:AsyncSession, level:int, menu_name:str):
    '''метод для генерации меню с фоткой текстом и клавой по заданным характеристикам'''
    if level == 1:
        
    