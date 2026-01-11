from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers



logger = setup_logging()




user_inline_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Список всех туров", callback_data='show_all_tours')],
        [InlineKeyboardButton(text="Информация об аккаунте", callback_data='show_me')],
        [InlineKeyboardButton(text="Ваши заказы", callback_data='show_user_orders')],
        [InlineKeyboardButton(text="О нас", callback_data='about_company')]

    ]
)

# user_inline_interaction_kb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(text='показать туры', callback_data='show_all_tours'), 
#             InlineKeyboardButton(text='показать достопримечательности', callback_data='show_all_lm')
#         ],
#         [
#             InlineKeyboardButton(text='назад', callback_data='admin_main_menu')
#         ]
#     ]
# )
