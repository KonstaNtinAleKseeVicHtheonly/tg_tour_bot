from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, Message
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.states import NewsLetter
from aiogram.filters import StateFilter
# системыне утилиты
import asyncio
import os
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database.requests.user_requests import get_current_category
from app.database.requests.admin_requests import create_product, create_category
#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_handler = Router()
admin_handler.message.filter(AdminFilter())



























# @admin_handler.message(Command('create_product'))
# async def create_new_product(message: Message, state:FSMContext):
#     '''активирует динмаичный FSM для добавления товара (вместо id категории указывается имя категории)'''
#     await state.set_state('product_name')
#     await message.answer("активирован режим создания продукта, введите название продукта")
    
# @admin_handler.message(F.text, StateFilter('product_name'))
# async def write_product_name(message: Message, state:FSMContext):
#     await state.update_data(name=message.text.lower())
#     await state.set_state('product_description')
#     await message.answer("ВВедите описание товара")
    
# @admin_handler.message(F.text, StateFilter('product_description'))
# async def write_product_description(message: Message, state:FSMContext):
#     await state.update_data(description=message.text)
#     await state.set_state('product_price')
#     await message.answer("ВВедите цену товара")

# @admin_handler.message(F.text, StateFilter('product_price'))
# async def write_product_price(message: Message, state:FSMContext):
#     await state.update_data(price=message.text)
#     await state.set_state('product_image')
#     await message.answer("Отправьте фотографию товара")
    
# @admin_handler.message(F.photo, StateFilter('product_image'))
# async def write_product_image(message: Message, state:FSMContext):
#     img = message.photo[-1]
#     img_id = img.file_id
#     await state.update_data(card_image=img_id)
#     await state.set_state('product_category')
#     await message.answer("Отправьте категорию товара")
    
    
# @admin_handler.message(F.text=='skip', StateFilter('product_image'))
# async def skip_image(message: Message, state:FSMContext):
#     await message.answer("пропущено добавление картинки товара")
#     await state.set_state('product_category')
#     await message.answer("Отправьте категорию товара")

# @admin_handler.message(F.text, StateFilter('product_category'))
# async def write_product_category(message: Message, state:FSMContext):
#     product_category = await get_current_category(message.text.lower())
#     if not product_category:
#         await message.answer("Пожалуйста введите уже существующую категорию товара")
#         return
#     await state.update_data(category_id = product_category.id)
#     new_product_data = await state.get_data()
#     logger.info("данные для создания товара успешно созданы, приступаю к записи его в БД")
#     result = await create_product(new_product_data)
#     await state.clear()
#     if not result:
#         await message.answer("Ошибка при создании ногов товара")
#         return
#     message_text = "✅ Продукт успешно создан!\n:"
#     for key, value in new_product_data.items():
#         message_text += f"{key}: {value}\n"
#     await message.answer(message_text)

# @admin_handler.message(Command('create_category'))
# async def create_new_category(message: Message, state:FSMContext):
#     '''активирует динмаичный FSM для добавления категории'''
#     await state.set_state('category_name')
#     await message.answer("активирован режим создания категории, введите название продукта")
    
# @admin_handler.message(F.text, StateFilter('category_name'))
# async def write_category_name(message: Message, state:FSMContext):
#     await state.update_data(name=message.text.lower())
#     await state.set_state('category_img')
#     await message.answer("Отправьте фотографию для категории")
    
# @admin_handler.message(F.photo, StateFilter('category_img'))
# async def write_category_img(message: Message, state:FSMContext):
#     img = message.photo[-1]
#     img_id = img.file_unique_id
#     await state.update_data(category_image=img_id)
#     category_data = await state.get_data()
#     result = await create_category(category_data)
#     await state.clear()
#     if not result:
#         await message.answer("Ошибка при создании категории, чекай логи")
#         return
#     message_text = "✅ Категория успешно создана!\n:"
#     for key, value in category_data.items():
#         message_text += f"{key}: {value}\n"
#     await message.answer(message_text)
    
    
    
# @admin_handler.message(F.text=='skip', StateFilter('category_img'))
# async def skip_category_img(message: Message, state:FSMContext):
#     await message.answer("Пропущено добавление фотографии категории")
#     category_data = await state.get_data()
#     result = await create_category(category_data)
#     await state.clear()
#     if not result:
#         await message.answer("Ошибка при создании категории, чекай логи")
#         return
#     message_text = "✅ Категория успешно создана!\n:"
#     for key, value in category_data.items():
#         message_text += f"{key}: {value}\n"
#     await message.answer(message_text)
    
    
    
# @admin_handler.message(Command('cancel'))
# async def cancel_processes(message:Message, state:FSMContext):
#     '''Команда отмены и выхода их всех FSM'''
#     await state.clear()
#     await message.answer("Вы вышли из текущего режима")

