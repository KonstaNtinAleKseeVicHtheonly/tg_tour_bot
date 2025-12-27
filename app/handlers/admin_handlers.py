from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, Message
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#KB
from app.keyboards.reply_kb import admin_reply_kb, delete_reply_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.states import ChatMode
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
#утилиты
from app.utils.env_utils import _get_admins_id
#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_handler = Router()
admin_handler.message.filter(AdminFilter())





@admin_handler.message(Command('odmen'))
async def activate_admin_mode(message : Message):
    '''активирует режим дмин панели даваю юзеру доп полномочия, если id юзера состоит в admin_id конечно'''
    logger.warning(f"Юзер : {message.from_user.username} с id {message.from_user.id} активировал режим админ панели")
    await message.delete()
    await message.answer("Режим админа усешно активирован")
    await message.answer("Что хотите выбрать?" , reply_markup=admin_reply_kb)

@admin_handler.message(Command('show_admins'))
async def show_group_admins_id(message : Message, bot : Bot):
    '''показывает всех юзеров и ботов группы с полночиями creator или administrator'''
    admins_id_lst = await _get_admins_id()
    await message.answer(f"вот список с id всех админов : {'\n |'.join(admins_id_lst)}")



@admin_handler.message(F.text == "Я так, просто посмотреть зашел")
async def starring_at_product(message: Message):
    await message.answer("ОК, вот список товаров")


@admin_handler.message(F.text == "Изменить товар")
async def change_product(message: Message):
    await message.answer("ОК, вот список товаров")


@admin_handler.message(F.text == "Удалить товар")
async def delete_product(message: Message):
    await message.answer("Выберите товар(ы) для удаления")


@admin_handler.message(StateFilter(ChatMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
























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

