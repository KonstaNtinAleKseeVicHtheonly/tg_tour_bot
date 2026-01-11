from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, Message,ContentType
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#KB

from app.keyboards.admin_kb.inline_keyboards import all_tours_kb, current_tour_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import AdminTourMode
# системыне утилиты
import asyncio
import os
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database import db_managers
from app.database.all_models.models import User,Landmark,Tour,TourLandmarkAssociation
from sqlalchemy.ext.asyncio import AsyncSession
#утилиты

#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_tour_handler = Router()
admin_tour_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами

    
#___________________________________________________________
# Туры


@admin_tour_handler.message(StateFilter(AdminTourMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
@admin_tour_handler.callback_query(F.data=='show_all_tours')
async def show_all_tours(callback: CallbackQuery, session : AsyncSession):
    tour_db_manager = db_managers.TourManager()
    all_tours = await tour_db_manager.get_all(session)
    await callback.message.answer("Вот список всех туров", reply_markup = await all_tours_kb(all_tours) ) # выведет список всех достопримечательностей


@admin_tour_handler.callback_query(F.data.startswith('show_tour'))
async def get_current_tour_info(callback: CallbackQuery, session:AsyncSession):
    current_tour_id =  int(callback.data.split('_')[-1])
    tour_db_manager = db_managers.TourManager()
    current_tour= await tour_db_manager.get(session=session, id=current_tour_id)
    if not current_tour:
        await callback.message.answer(f"данная lm с id : {current_tour_id} не найдена в базе")
        return
    await callback.message.answer_photo(photo = current_tour.image_url,
                                            caption = f'''{current_tour.name}\n
                                            {current_tour.description}''',
                                            reply_markup = current_tour_kb(current_tour_id))


    

@admin_tour_handler.callback_query(F.data=='create_tour')
async def create_tour_mode(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await state.set_state(AdminTourMode.create_name)
    await callback.message.answer("Активирован режим создания тура, пожалуйста введите название")

    
@admin_tour_handler.message(F.text,F.text.len()>4, StateFilter(AdminTourMode.create_name))
async def set_tour_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text.lower())
    await state.set_state(AdminTourMode.create_description)
    await message.answer("Введите текстовое описание")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.create_name))
async def wrong_name(message: Message, state:FSMContext):
    await message.answer("Пожалуйста правильное описание тура")
    
    
@admin_tour_handler.message(F.text, F.text.len()>7,StateFilter(AdminTourMode.create_description))
async def set_tour_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text.strip().capitalize())
    await state.set_state(AdminTourMode.create_price)
    await message.answer("Укажите цену в BYN")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.create_description))
async def wrong_description(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите валидное текстовое описание тура")
       
    
@admin_tour_handler.message(F.text,  StateFilter(AdminTourMode.create_price))
async def set_tour_price(message: Message, state:FSMContext):
    raw_tour_price = message.text.strip()
    await state.update_data(price_per_person = raw_tour_price)
    await state.set_state(AdminTourMode.create_photo)
    await message.answer("Отправьте фотографию тура")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.create_price))
async def wrong_price(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите цену на тур")
    
        
@admin_tour_handler.message(F.photo, StateFilter(AdminTourMode.create_photo))
async def set_tour_image(message: Message, state:FSMContext):
    img = message.photo[-1]
    img_id = img.file_id
    await state.update_data(image_url = img_id)
    await state.set_state(AdminTourMode.set_max_people)
    await message.answer("Введите максимально количество людей в данном туре")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.create_photo))
async def wrong_picture(message: Message, state:FSMContext):
    await message.answer("Пожалуйста отправьте фотографию")
    
    
@admin_tour_handler.message(F.text,F.text.isdigit(), StateFilter(AdminTourMode.set_max_people))
async def set_tour_max_people(message: Message, state:FSMContext):
    people_number = int(message.text)
    await state.update_data(max_people = people_number)
    await state.set_state(AdminTourMode.set_duration)
    await message.answer("Введите длительность тура, можно например: 3 часа 20 мин")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.set_max_people))
async def wrong_max_number(message: Message, state:FSMContext):
    await message.answer("Введите положительно число людей")
    
    
    
    
@admin_tour_handler.message(F.text, StateFilter(AdminTourMode.set_duration))
async def set_tour_duration(message: Message, state:FSMContext):
    tour_duration = message.text.strip()
    await state.update_data(duration = tour_duration)
    await state.set_state(AdminTourMode.set_category)
    await message.answer("Введите категорию тура: водный, пеший, автобус, машина")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.set_duration))
async def wrong_duration(message: Message, state:FSMContext):
    await message.answer("Укажите длительность текстом!!!")
    
@admin_tour_handler.message(F.text, StateFilter(AdminTourMode.set_category))
async def set_tour_category(message: Message, state:FSMContext):
    tour_category = message.text.strip()
    await state.update_data(category = tour_category)
    await state.set_state(AdminTourMode.set_meeting_point)
    await message.answer("Введите место встречи")
    
@admin_tour_handler.message(StateFilter(AdminTourMode.set_category))
async def wrong_category(message: Message, state:FSMContext):
    await message.answer("Укажите длительность текстом!!!")
    

@admin_tour_handler.message(F.text, StateFilter(AdminTourMode.set_meeting_point))
async def set_meeting_point(message: Message, state:FSMContext, session: AsyncSession):
    try:
        tour_meeting_point = message.text.capitalize().strip()
        await state.update_data(meeting_point = tour_meeting_point)
        #сбор инфы и запись в БД
        tour_info = await state.get_data()
        logger.info('ЗАкончен сбор инфы о новом туре, приступаю к записи в БД')
        
        await state.set_state(AdminTourMode.waiting)
        tour_db_manager = db_managers.TourManager()
        result = await tour_db_manager.create(session, tour_info)
        if result:
            await message.answer("Новый тур успешно создан")
            await session.commit()
        else:
            await message.answer("Ошибка при создании тура, чекай логи, проблема в менеджере Бд")
        await state.clear()
    except Exception as err:
        logger.error(f"Произошла какая то шляпа в хэндлере на запись строки в Tour:{err}")
        await session.rollback()
        await state.clear()
        await message.answer(f'Произошла непредвиденная ошибка : {err}, чекни логи')
    
@admin_tour_handler.message(StateFilter(AdminTourMode.set_meeting_point))
async def wrong_meeting_point(message: Message, state:FSMContext):
    await message.answer("Укажите место встречи текстом текстом!!!")

# @admin_tour_handler.message(F.text.lower() == "показать все туры")
# async def show_all_tours(message: Message, session:AsyncSession):
#         tour_db_manager = db_managers.TourManager()
#         all_tours = await tour_db_manager.get_all(session)
#         if not all_tours:
#             await message.answer("⭕ В базе нет туров")
#             return
#         final_text = "📋 Список всех туров:\n\n"
#         for tour in all_tours:
#             tour_info = (
#                 f"🏷 ID: {tour.id}\n"
#                 f"🏰 Название: {tour.name}\n"
#                 f"💰 Цена: {tour.price_per_person}₽\n"
#                 f"👥 Мест: {tour.max_people}\n"
#                 f"➖➖➖➖➖➖➖➖➖\n"
#             )
#             # Если добавление превысит лимит
#             if len(final_text) + len(tour_info) > 4000:
#                 # Отправляем накопленное
#                 await message.answer(final_text)
#                 # Начинаем новое сообщение с заголовком
#                 final_text = "📋 Список всех туров (продолжение):\n\n" + tour_info
#             else:
#                 # Добавляем к текущему сообщению
#                 final_text += tour_info
#         # Отправляем остаток
#         if final_text:
#             await message.answer(final_text)


@admin_tour_handler.callback_query(F.data.startswith('delete_tour'))
async def delete_current_landmark(callback: CallbackQuery, session : AsyncSession):
    current_tour_id = int(callback.data.split('_')[-1])
    tour_db_manager = db_managers.TourManager()
    delete_result = await tour_db_manager.delete(session, current_tour_id)
    if delete_result:
        await session.commit() 
        await callback.message.answer(f"Тур с id : {current_tour_id} удалена успешно")
    else:
        await callback.message.answer(f"Ошибка при удалении тура с id : {current_tour_id}, чекай логи")

@admin_tour_handler.message(F.text == "изменить тур")
async def change_tour_mode(message: Message, state:FSMContext):
    await message.answer("Активирован режим изменения текущего тура, выберите тур который хотите изменить")
    await state.update_data(AdminTourMode.edit_select_product)
    #добавить адаптивную клаву которая идет в бд и вытаскивает все туры их имена в текст inline кнопок а их id в callback кнопок

@admin_tour_handler.callback_query(F.data.startswith('tour_'), StateFilter(AdminTourMode.edit_select_product))
async def get_tour_for_change(callback: CallbackQuery, state:FSMContext):
    product_id = int(callback.data.split('_')[-1])
    await state.update_data(id=product_id)
    await state.set_state(AdminTourMode.edit_choose_field)
    await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
@admin_tour_handler.callback_query(F.data.startswith('edit_photo'), StateFilter(AdminTourMode.edit_choose_field))
async def get_photo_for_change(callback: CallbackQuery, state:FSMContext):
    img = callback.message.photo[-1]
    img_id = img.file_id
    await state.update_data(product_photo_id = img_id)
    # процесс изменения полей
    await callback.message.answer("выбранное поле успешно изменено, желаете изменить что то еще?") # тут клава будет адаптированная под столбцы текущего тура
    
    

@admin_tour_handler.callback_query(F.data.startswith('edit_'), StateFilter(AdminTourMode.edit_choose_field))
async def get_field_for_change(callback: CallbackQuery, state:FSMContext):
    await state.update_data()
    # процесс изменения поля вставить
    await state.clear()
    await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
    



