from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, Message,ContentType
from decimal import Decimal
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter,and_f,or_f
#KB
from app.keyboards.admin_kb.inline_keyboards import all_landmarks_kb, current_landmark_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import  ChatMode, AdminLandMarkMode
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
from app.utils.env_utils import _get_admins_id
#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_lm_handler = Router()
admin_lm_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами

    
#_______________________________________________________________________________________
#LANDMARKS(достопримечательности)
    
    
@admin_lm_handler.message(StateFilter(AdminLandMarkMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")

    
@admin_lm_handler.callback_query(F.data=='show_all_lm')
async def show_all_landmarks(callback: CallbackQuery, session : AsyncSession):
    lm_db_manager = db_managers.LandMarkManager()
    all_lm = await lm_db_manager.get_all(session)   
    await callback.message.answer("Вот список всех достопримечательностей", reply_markup= await all_landmarks_kb(all_lm)) # выведет список всех достопримечательностей


@admin_lm_handler.callback_query(F.data.startswith('show_landmark'))
async def show_current_landmark(callback: CallbackQuery, session:AsyncSession):
    current_lm_id =  int(callback.data.split('_')[-1])
    lm_db_manager = db_managers.LandMarkManager()
    current_landmark = await lm_db_manager.get(session=session, id=current_lm_id)
    if not current_landmark:
        await callback.message.answer(f"данная lm с id : {current_landmark} не найдена в базе")
        return
    await callback.message.answer_photo(photo = current_landmark.image_url,
                                            caption = f'''{current_landmark.name}\n
                                            {current_landmark.description}''',
                                            reply_markup = current_landmark_kb(current_lm_id))


        
@admin_lm_handler.callback_query(F.data == 'create_lm')
async def create_landmark_mode(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await state.set_state(AdminLandMarkMode.create_name)
    await callback.message.answer("Активирован режим создания достопримечательности, пожалуйста введите название")
    
    
@admin_lm_handler.message(F.text,F.text.len()>4, StateFilter(AdminLandMarkMode.create_name))
async def set_landmark_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text.lower())
    await state.set_state(AdminLandMarkMode.create_description)
    await message.answer("Введите текстовое описание")
    
@admin_lm_handler.message(StateFilter(AdminLandMarkMode.create_name))
async def wrong_name(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите еткстовое название достопримечательности")
    
    
@admin_lm_handler.message(F.text, F.text.len()>7,StateFilter(AdminLandMarkMode.create_description))
async def set_landmark_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text.capitalize())
    await state.set_state(AdminLandMarkMode.create_url)
    await message.answer("Укажите ссылку на достопримечательност из инета")
    
@admin_lm_handler.message(StateFilter(AdminLandMarkMode.create_description))
async def wrong_description(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите валидное текстовое описание товара")
       
    
@admin_lm_handler.message(F.text,F.text.contains("http"),  StateFilter(AdminLandMarkMode.create_url))
async def set_landmark_url(message: Message, state:FSMContext):
    await state.update_data(url = message.text.strip())
    await state.set_state(AdminLandMarkMode.create_photo)
    await message.answer("Отправьте фотографию")
    
@admin_lm_handler.message(StateFilter(AdminLandMarkMode.create_url))
async def wrong_url(message: Message, state:FSMContext):
    await message.answer("Пожалуйста ссылку на достопримечательность из инета")
    
        
@admin_lm_handler.message(F.photo, StateFilter(AdminLandMarkMode.create_photo))
async def set_landmark_image(message: Message, state:FSMContext, session: AsyncSession):
    try:
        img = message.photo[-1]
        img_id = img.file_id
        await state.update_data(image_url = img_id)
        # сбор всей инфы и сохранение в БД
        landmark_info = await state.get_data()
        logger.info("Данные о достопримечательности успешно собраны")
        lm_db_manager = db_managers.LandMarkManager()
        logger.info(f"Приступаю к записи LM в таблицу с параметрами : {landmark_info}")
        await state.set_state(AdminLandMarkMode.waiting)
        creation_result = await lm_db_manager.create(session, landmark_info)
        if creation_result:
                await message.answer("LM успешно добавлена в БД")
                await session.commit() # нужно именно в хэндлере указать, Т.к в менеджере flush используем для вохможности отката
        else:
            await message.answer("ошибка при создании записив БД, чекни логи")
        await state.clear()
    except Exception as err:
        logger.error(f"Произошла какая то шляпа в хэндлере на запись строки в Landmark:{err}")
        await session.rollback()
        await state.clear()
        await message.answer(f'Произошла непредвиденная ошибка : {err}, чекни логи')


    
@admin_lm_handler.message(StateFilter(AdminLandMarkMode.create_photo))
async def wrong_picture(message: Message, state:FSMContext):
    await message.answer("Пожалуйста отправьте фотографию")
    
@admin_lm_handler.callback_query(F.data.startswith('delete_lm'))
async def delete_current_landmark(callback: CallbackQuery, session : AsyncSession):
    current_lm_id = int(callback.data.split('_')[-1])
    lm_db_manager = db_managers.LandMarkManager()
    delete_result = await lm_db_manager.delete(session, current_lm_id)
    if delete_result:
        await session.commit() 
        await callback.message.answer(f"Достопримечательность с id : {current_lm_id} удалена успешно")
    else:
        await callback.message.answer(f"Ошибка при удалении достопримечательности с id : {current_lm_id}, чекаай логи")
    




@admin_lm_handler.message(F.text == "изменить landmark")
async def change_tour_mode(message: Message, state:FSMContext):
    await message.answer("Активирован режим изменения текущего тура, выберите тур который хотите изменить")
    await state.update_data(AdminLandMarkMode.edit_select_product)
    #добавить адаптивную клаву которая идет в бд и вытаскивает все туры их имена в текст inline кнопок а их id в callback кнопок

# @admin_lm_handler.callback_query(F.data.startswith('tour_'), StateFilter(AdminLandMarkMode.edit_select_lm))
# async def get_tour_for_change(callback: CallbackQuery, state:FSMContext):
#     product_id = int(callback.data.split('_')[-1])
#     await state.update_data(id=product_id)
#     await state.set_state(AdminLandMarkMode.edit_choose_field)
#     await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
# @admin_lm_handler.callback_query(F.data.startswith('edit_photo'), StateFilter(AdminLandMarkMode.edit_choose_field))
# async def get_photo_for_change(callback: CallbackQuery, state:FSMContext):
#     img = callback.message.photo[-1]
#     img_id = img.file_id
#     await state.update_data(product_photo_id = img_id)
#     # процесс изменения полей
#     await callback.message.answer("выбранное поле успешно изменено, желаете изменить что то еще?") # тут клава будет адаптированная под столбцы текущего тура
    
    

# @admin_lm_handler.callback_query(F.data.startswith('edit_'), StateFilter(AdminLandMarkMode.edit_choose_field))
# async def get_field_for_change(callback: CallbackQuery, state:FSMContext):
#     await state.update_data()
#     # процесс изменения поля вставить
#     await state.clear()
#     await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
    





