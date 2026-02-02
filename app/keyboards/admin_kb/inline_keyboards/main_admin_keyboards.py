from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging




logger = setup_logging()




admin_inline_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="меню", callback_data='admin_interactive_menu'),
            InlineKeyboardButton(text="show_me", callback_data='show_me'),
            InlineKeyboardButton(text="о нас", callback_data='about')
        ],
        [
            InlineKeyboardButton(text="Все админы", callback_data="show_admins")
        ] 
    ]
)

admin_inline_interaction_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Все пользователи', callback_data='show_all_users')],
        [InlineKeyboardButton(text='показать туры', callback_data='show_all_tours_admin')],
            [InlineKeyboardButton(text='показать достопримечательности', callback_data='show_all_lm_admin')],
            [InlineKeyboardButton(text='показать связи туров и landmarks', callback_data='show_all_associations')],
            [InlineKeyboardButton(text='показать все банеры', callback_data='show_all_banners')],  
        
            [InlineKeyboardButton(text='добавить тур', callback_data='create_tour')],
            [InlineKeyboardButton(text='добавить достопримечательности', callback_data='create_lm')],
            [InlineKeyboardButton(text='создать связь тура и landmark', callback_data='create_association')],
            [InlineKeyboardButton(text='создать новый  банер', callback_data='create_banner')],
            [InlineKeyboardButton(text='Посмотреть все заказы', callback_data='show_all_orders_admin')],
            [InlineKeyboardButton(text='проверить экспирацию', callback_data='check_orders_expiration')],
            
            [InlineKeyboardButton(text='назад', callback_data='admin_main_menu')]
    ]
)
