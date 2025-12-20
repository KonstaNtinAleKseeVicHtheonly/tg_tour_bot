from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests.user_requests import get_categories, get_cards_from_category
from project_logger.loger_configuration import setup_logging

logger = setup_logging()

reply_main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Каталог'),KeyboardButton(text='Контакты')]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

inline_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Каталог", callback_data='catalogue'),InlineKeyboardButton(text="Контакты", callback_data='contacts')],
    ],resize_keyboard=True, input_field_placeholder="Выберите пункт")

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена',callback_data='cancel')]])


# async def request_user_contact():
#     return ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='выбрать контакт', request_contact=True)]
# ], resize_keyboard=True, input_field_placeholder="Выберите свой номер из контактов или введие вручную")


# async def get_categories_kb():
#     '''создает клаву по всем категориям из ассортимента'''
#     try:
#         logger.info("Сохдание клавы по категориям товаров из БД")
#         all_categories = await get_categories()
#         if not all_categories:
#             logger.warning("Пока что нет категорий товаров")
#             return InlineKeyboardMarkup(inline_keyboard=[
#                     [InlineKeyboardButton(text='Нет категорий', callback_data='get_back')]])
#         else:
#             categories_kb = InlineKeyboardBuilder()
#             for category in all_categories:
#                 categories_kb.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
#             categories_kb.row(InlineKeyboardButton(text='Назад', callback_data='get_back'))
#             return categories_kb.adjust(3).as_markup() # преобразуем клаву в объект Markub для отображения в хэндлере 
#     except Exception as err:
#         logger.error(f"Ошибка при создании клавы по категориям: {err}")
        
# async def get_cards_kb(category_id:int):
#     '''Берет через метод данные о карточках текущей ктаегории по ее id и выводит карточки в виде inline клавы'''
#     try:
#             logger.info("Сохдание клавы по карточкам товаров из заданной категории товаров из БД")
#             cards_from_category = await get_cards_from_category(category_id)
#             if not cards_from_category:
#                 raise ValueError("Ошибка при запросе карточек товара для создания клавиатуры")
#             else:
#                 cards_kb = InlineKeyboardBuilder()
#                 for card in cards_from_category:
#                     cards_kb.add(InlineKeyboardButton(text=f"{card.name}|{card.price} RUB", callback_data=f"product_{card.id}"))
#                 cards_kb.row(InlineKeyboardButton(text='Назад', callback_data="catalogue"))
#                 return cards_kb.adjust(2).as_markup() # преобразуем клаву в объект Markub для отображения в хэндлере 
#     except Exception as err:
#         logger.error(f"Ошибка при создании клавы по категориям: {err}")
    
# async def product_kb(category_id:int, card_id:int):
#     '''генерирует клаву с возможностью купить либо вернуться назад для текущей карточки'''
#     logger.info(f"генерация клавы для покупки товара  с card_id : {card_id}")
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text='купить',callback_data=f"buy_{card_id}")],
#         [InlineKeyboardButton(text='Назад', callback_data=f"category_{category_id}")]
#         ])
    
# async def client_location():
#     '''клава с кнопкой запроса локации юзера'''
#     return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить геолокацию',  request_location=True)]],
#                                resize_keyboard= True, input_field_placeholder="Введите адрес или отпарвьте свою геолоакцию")