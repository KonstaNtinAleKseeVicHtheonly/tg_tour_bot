from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, Message,ContentType
from decimal import Decimal
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter,and_f,or_f
#KB
from app.keyboards.reply_kb import admin_reply_kb, delete_reply_kb
from app.keyboards.admin_kb.inline_keyboards import all_landmarks_kb, current_landmark_kb, all_tours_kb, current_tour_kb, admin_inline_main_menu, admin_inline_interaction_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import AdminTourMode, ChatMode, AdminLandMarkMode
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

admin_handler = Router()
admin_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами


@admin_handler.message(Command('odmen'))
async def activate_admin_mode(message : Message):
    '''активирует режим дмин панели даваю юзеру доп полномочия, если id юзера состоит в admin_id конечно'''
    logger.warning(f"Юзер : {message.from_user.username} с id {message.from_user.id} активировал режим админ панели")
    await message.delete()
    await message.answer("Режим админа усешно активирован")
    await message.answer("Что хотите выбрать?" , reply_markup=admin_inline_main_menu)
    
@admin_handler.callback_query(F.data=='admin_main_menu')
async def admin_main_menu(callback: CallbackQuery):
    '''покажет главное меню админа'''
    await callback.message.answer("Что хотите посмотреть?", reply_markup = admin_inline_main_menu) # выведет список всех достопримечательностей

    
@admin_handler.callback_query(F.data=='admin_interactive_menu')
async def interaction_mode(callback: CallbackQuery):
    '''покажет кнопки с возможностью посмотреть все туры и достопримечательности (углубление в интерактивынй режим через колбэки)'''
    await callback.message.answer("Что хотите посмотреть?", reply_markup = admin_inline_interaction_kb) # выведет список всех достопримечательностей


@admin_handler.message(Command('cancel'), StateFilter('*'))
@admin_handler.message(F.text.lower()=='отмена', StateFilter('*'))
async def cancel_processes(message:Message, state:FSMContext):
    '''Команда отмены и выхода их всех FSM'''
    
    current_state = await state.set_state()

    if current_state is None:
        return
    await state.clear()
    await message.answer("Вы вышли из текущего режима", reply_markup=admin_reply_kb)
    
@admin_handler.message(or_f(
        StateFilter(AdminTourMode.waiting),
        StateFilter(AdminLandMarkMode.waiting)))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
@admin_handler.message(Command('show_admins'))
async def show_group_admins_id(message : Message, bot : Bot):
    '''показывает всех юзеров и ботов группы с полночиями creator или administrator'''
    admins_id_lst = await _get_admins_id()
    await message.answer(f"вот список с id всех админов : {'|'.join(admins_id_lst)}")
    
    
#___________________________________________________________
# Туры
@admin_handler.callback_query(F.data=='show_all_tours')
async def show_all_tours(callback: CallbackQuery, session : AsyncSession):
    await callback.message.answer("Вот список всех туров", reply_markup= await all_tours_kb(session)) # выведет список всех достопримечательностей


@admin_handler.callback_query(F.data.startswith('show_tour'))
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


    

@admin_handler.message(F.text.lower() == "добавить тур")
async def create_tour_mode(message: Message, state:FSMContext):
    await state.clear()
    await state.set_state(AdminTourMode.create_name)
    await message.answer("Активирован режим создания тура, пожалуйста введите название")

    
@admin_handler.message(F.text,F.text.len()>4, StateFilter(AdminTourMode.create_name))
async def set_tour_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text.lower())
    await state.set_state(AdminTourMode.create_description)
    await message.answer("Введите текстовое описание")
    
@admin_handler.message(StateFilter(AdminTourMode.create_name))
async def wrong_name(message: Message, state:FSMContext):
    await message.answer("Пожалуйста правильное описание тура")
    
    
@admin_handler.message(F.text, F.text.len()>7,StateFilter(AdminTourMode.create_description))
async def set_tour_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text.strip().capitalize())
    await state.set_state(AdminTourMode.create_price)
    await message.answer("Укажите цену в BYN")
    
@admin_handler.message(StateFilter(AdminTourMode.create_description))
async def wrong_description(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите валидное текстовое описание тура")
       
    
@admin_handler.message(F.text,  StateFilter(AdminTourMode.create_price))
async def set_tour_price(message: Message, state:FSMContext):
    raw_tour_price = message.text.strip()
    await state.update_data(price_per_person = raw_tour_price)
    await state.set_state(AdminTourMode.create_photo)
    await message.answer("Отправьте фотографию тура")
    
@admin_handler.message(StateFilter(AdminTourMode.create_price))
async def wrong_price(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите цену на тур")
    
        
@admin_handler.message(F.photo, StateFilter(AdminTourMode.create_photo))
async def set_tour_image(message: Message, state:FSMContext):
    img = message.photo[-1]
    img_id = img.file_id
    await state.update_data(image_url = img_id)
    await state.set_state(AdminTourMode.set_max_people)
    await message.answer("Введите максимально количество людей в данном туре")
    
@admin_handler.message(StateFilter(AdminTourMode.create_photo))
async def wrong_picture(message: Message, state:FSMContext):
    await message.answer("Пожалуйста отправьте фотографию")
    
    
@admin_handler.message(F.text,F.text.isdigit(), StateFilter(AdminTourMode.set_max_people))
async def set_tour_max_people(message: Message, state:FSMContext):
    people_number = int(message.text)
    await state.update_data(max_people = people_number)
    await state.set_state(AdminTourMode.set_duration)
    await message.answer("Введите длительность тура, можно например: 3 часа 20 мин")
    
@admin_handler.message(StateFilter(AdminTourMode.set_max_people))
async def wrong_max_number(message: Message, state:FSMContext):
    await message.answer("Введите положительно число людей")
    
    
    
    
@admin_handler.message(F.text, StateFilter(AdminTourMode.set_duration))
async def set_tour_duration(message: Message, state:FSMContext):
    tour_duration = message.text.strip()
    await state.update_data(duration = tour_duration)
    await state.set_state(AdminTourMode.set_category)
    await message.answer("Введите категорию тура: водный, пеший, автобус, машина")
    
@admin_handler.message(StateFilter(AdminTourMode.set_duration))
async def wrong_duration(message: Message, state:FSMContext):
    await message.answer("Укажите длительность текстом!!!")
    
@admin_handler.message(F.text, StateFilter(AdminTourMode.set_category))
async def set_tour_category(message: Message, state:FSMContext):
    tour_category = message.text.strip()
    await state.update_data(category = tour_category)
    await state.set_state(AdminTourMode.set_meeting_point)
    await message.answer("Введите место встречи")
    
@admin_handler.message(StateFilter(AdminTourMode.set_category))
async def wrong_category(message: Message, state:FSMContext):
    await message.answer("Укажите длительность текстом!!!")
    

@admin_handler.message(F.text, StateFilter(AdminTourMode.set_meeting_point))
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
    
@admin_handler.message(StateFilter(AdminTourMode.set_meeting_point))
async def wrong_meeting_point(message: Message, state:FSMContext):
    await message.answer("Укажите место встречи текстом текстом!!!")

@admin_handler.message(F.text.lower() == "показать все туры")
async def show_all_tours(message: Message, session:AsyncSession):
        tour_db_manager = db_managers.TourManager()
        all_tours = await tour_db_manager.get_all(session)
        if not all_tours:
            await message.answer("⭕ В базе нет туров")
            return
        final_text = "📋 Список всех туров:\n\n"
        for tour in all_tours:
            tour_info = (
                f"🏷 ID: {tour.id}\n"
                f"🏰 Название: {tour.name}\n"
                f"💰 Цена: {tour.price_per_person}₽\n"
                f"👥 Мест: {tour.max_people}\n"
                f"➖➖➖➖➖➖➖➖➖\n"
            )
            # Если добавление превысит лимит
            if len(final_text) + len(tour_info) > 4000:
                # Отправляем накопленное
                await message.answer(final_text)
                # Начинаем новое сообщение с заголовком
                final_text = "📋 Список всех туров (продолжение):\n\n" + tour_info
            else:
                # Добавляем к текущему сообщению
                final_text += tour_info
        # Отправляем остаток
        if final_text:
            await message.answer(final_text)

    

@admin_handler.message(F.text == "изменить тур")
async def change_tour_mode(message: Message, state:FSMContext):
    await message.answer("Активирован режим изменения текущего тура, выберите тур который хотите изменить")
    await state.update_data(AdminTourMode.edit_select_product)
    #добавить адаптивную клаву которая идет в бд и вытаскивает все туры их имена в текст inline кнопок а их id в callback кнопок

@admin_handler.callback_query(F.data.startswith('tour_'), StateFilter(AdminTourMode.edit_select_product))
async def get_tour_for_change(callback: CallbackQuery, state:FSMContext):
    product_id = int(callback.data.split('_')[-1])
    await state.update_data(id=product_id)
    await state.set_state(AdminTourMode.edit_choose_field)
    await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
@admin_handler.callback_query(F.data.startswith('edit_photo'), StateFilter(AdminTourMode.edit_choose_field))
async def get_photo_for_change(callback: CallbackQuery, state:FSMContext):
    img = callback.message.photo[-1]
    img_id = img.file_id
    await state.update_data(product_photo_id = img_id)
    # процесс изменения полей
    await callback.message.answer("выбранное поле успешно изменено, желаете изменить что то еще?") # тут клава будет адаптированная под столбцы текущего тура
    
    

@admin_handler.callback_query(F.data.startswith('edit_'), StateFilter(AdminTourMode.edit_choose_field))
async def get_field_for_change(callback: CallbackQuery, state:FSMContext):
    await state.update_data()
    # процесс изменения поля вставить
    await state.clear()
    await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
    
#_______________________________________________________________________________________
#LANDMARKS(достопримечательности)
    
    
@admin_handler.callback_query(F.data=='show_all_lm')
async def show_all_landmarks(callback: CallbackQuery, session : AsyncSession):
    await callback.message.answer("Вот список всех достопримечательностей", reply_markup= await all_landmarks_kb(session)) # выведет список всех достопримечательностей


@admin_handler.callback_query(F.data.startswith('show_landmark'))
async def show_current_landmark(callback: CallbackQuery, session:AsyncSession):
    logger.warning(f"принят callback о LM : {callback.data}")
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


        
@admin_handler.message(F.text.lower() == "добавить landmark")
async def create_landmark_mode(message: Message, state:FSMContext):
    await state.clear()
    await state.set_state(AdminLandMarkMode.create_name)
    await message.answer("Активирован режим создания достопримечательности, пожалуйста введите название")
    
@admin_handler.message(StateFilter(AdminLandMarkMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")

    
@admin_handler.message(F.text,F.text.len()>4, StateFilter(AdminLandMarkMode.create_name))
async def set_landmark_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text.lower())
    await state.set_state(AdminLandMarkMode.create_description)
    await message.answer("Введите текстовое описание")
    
@admin_handler.message(StateFilter(AdminLandMarkMode.create_name))
async def wrong_name(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите еткстовое название достопримечательности")
    
    
@admin_handler.message(F.text, F.text.len()>7,StateFilter(AdminLandMarkMode.create_description))
async def set_landmark_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text.capitalize())
    await state.set_state(AdminLandMarkMode.create_url)
    await message.answer("Укажите ссылку на достопримечательност из инета")
    
@admin_handler.message(StateFilter(AdminTourMode.create_description))
async def wrong_description(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите валидное текстовое описание товара")
       
    
@admin_handler.message(F.text.isdigit(), StateFilter(AdminLandMarkMode.create_url))
async def set_landmark_url(message: Message, state:FSMContext):
    await state.update_data(url = message.text.strip())
    await state.set_state(AdminLandMarkMode.create_photo)
    await message.answer("Отправьте фотографию")
    
@admin_handler.message(StateFilter(AdminLandMarkMode.create_url))
async def wrong_url(message: Message, state:FSMContext):
    await message.answer("Пожалуйста ссылку на достопримечательность из инета")
    
        
@admin_handler.message(F.photo, StateFilter(AdminLandMarkMode.create_photo))
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


    
@admin_handler.message(StateFilter(AdminLandMarkMode.create_photo))
async def wrong_picture(message: Message, state:FSMContext):
    await message.answer("Пожалуйста отправьте фотографию")
    

@admin_handler.message(F.text.lower() == "все достопримечательности")
async def show_all_landmarks(message: Message, session:AsyncSession):
        lm_db_manager = db_managers.LandMarkManager()
        all_lm = await lm_db_manager.get_all(session)
        if not all_lm:
            await message.answer("⭕ В базе нет достопримечательностей")
            return
        final_text = "📋 Список всех туров:\n\n"
        for lm in all_lm:
            lm_info = (
                f"🏷 ID: {lm.id}\n"
                f"🏰 Название: {lm.name}\n"
                f"💰 Ссылка: {lm.url}\n"
                f"➖➖➖➖➖➖➖➖➖\n"
            )
            # Если добавление превысит лимит
            if len(final_text) + len(lm_info) > 4000:
                # Отправляем накоплеlm
                await message.answer(final_text)
                # Начинаем новое сообщение с заголовком
                final_text = "📋 Список всех туров (продолжение):\n\n" + lm_info
            else:
                # Добавляем к текущему сообщению
                final_text += lm_info
        # Отправляем остаток
        if final_text:
            await message.answer(final_text)





@admin_handler.message(F.text == "изменить landmark")
async def change_tour_mode(message: Message, state:FSMContext):
    await message.answer("Активирован режим изменения текущего тура, выберите тур который хотите изменить")
    await state.update_data(AdminTourMode.edit_select_product)
    #добавить адаптивную клаву которая идет в бд и вытаскивает все туры их имена в текст inline кнопок а их id в callback кнопок

@admin_handler.callback_query(F.data.startswith('tour_'), StateFilter(AdminTourMode.edit_select_product))
async def get_tour_for_change(callback: CallbackQuery, state:FSMContext):
    product_id = int(callback.data.split('_')[-1])
    await state.update_data(id=product_id)
    await state.set_state(AdminTourMode.edit_choose_field)
    await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
@admin_handler.callback_query(F.data.startswith('edit_photo'), StateFilter(AdminTourMode.edit_choose_field))
async def get_photo_for_change(callback: CallbackQuery, state:FSMContext):
    img = callback.message.photo[-1]
    img_id = img.file_id
    await state.update_data(product_photo_id = img_id)
    # процесс изменения полей
    await callback.message.answer("выбранное поле успешно изменено, желаете изменить что то еще?") # тут клава будет адаптированная под столбцы текущего тура
    
    

@admin_handler.callback_query(F.data.startswith('edit_'), StateFilter(AdminTourMode.edit_choose_field))
async def get_field_for_change(callback: CallbackQuery, state:FSMContext):
    await state.update_data()
    # процесс изменения поля вставить
    await state.clear()
    await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
    
    

@admin_handler.message(F.text == "удалить landmark")
async def delete_tour(message: Message):
    await message.answer("Выберите товар(ы) для удаления")








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

