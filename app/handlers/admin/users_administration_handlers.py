from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#KB

from app.keyboards.admin_kb.inline_keyboards import all_tours_kb, current_tour_kb
from app.keyboards.base_keyboards import create_inline_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import AdminUsersMode
# системыне утилиты
import asyncio
import os
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database import db_managers
from app.database.all_models.models import User
from app.database.db_queries import _show_all_users_query
from sqlalchemy.ext.asyncio import AsyncSession
#утилиты

#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_user_handler = Router()
admin_user_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами

    
#___________________________________________________________
# Туры


@admin_user_handler.message(StateFilter(AdminUsersMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
# Показ туров(чтение из базы)
@admin_user_handler.callback_query(F.data=='show_all_users')
async def show_all_users(callback: CallbackQuery, session : AsyncSession):
    all_users = await _show_all_users_query(session)
    await callback.message.answer("Вот список всех юзеров", reply_markup = await all_users_kb(all_users) ) # выведет список всех достопримечательностей


@admin_user_handler.callback_query(F.data.startswith('show_tour'))
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


    
# создание тура
@admin_user_handler.callback_query(F.data=='create_tour')
async def create_tour_mode(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await state.set_state(AdminTourMode.create_name)
    await callback.message.answer("Активирован режим создания тура, пожалуйста введите название")

    
@admin_user_handler.message(F.text,F.text.len()>4, StateFilter(AdminTourMode.create_name))
async def set_tour_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text.lower())
    await state.set_state(AdminTourMode.create_description)
    await message.answer("Введите текстовое описание")
    
@admin_user_handler.message(StateFilter(AdminTourMode.create_name))
async def wrong_name(message: Message, state:FSMContext):
    await message.answer("Пожалуйста правильное описание тура")
    
    
@admin_user_handler.message(F.text, F.text.len()>7,StateFilter(AdminTourMode.create_description))
async def set_tour_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text.strip().capitalize())
    await state.set_state(AdminTourMode.create_price)
    await message.answer("Укажите цену в BYN")
    
@admin_user_handler.message(StateFilter(AdminTourMode.create_description))
async def wrong_description(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите валидное текстовое описание тура")
       
    
@admin_user_handler.message(F.text,  StateFilter(AdminTourMode.create_price))
async def set_tour_price(message: Message, state:FSMContext):
    raw_tour_price = message.text.strip()
    await state.update_data(price_per_person = raw_tour_price)
    await state.set_state(AdminTourMode.create_photo)
    await message.answer("Отправьте фотографию тура")
    
@admin_user_handler.message(StateFilter(AdminTourMode.create_price))
async def wrong_price(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите цену на тур")
    
        
@admin_user_handler.message(F.photo, StateFilter(AdminTourMode.create_photo))
async def set_tour_image(message: Message, state:FSMContext):
    img = message.photo[-1]
    img_id = img.file_id
    await state.update_data(image_url = img_id)
    await state.set_state(AdminTourMode.set_max_people)
    await message.answer("Введите максимально количество людей в данном туре")
    
@admin_user_handler.message(StateFilter(AdminTourMode.create_photo))
async def wrong_picture(message: Message, state:FSMContext):
    await message.answer("Пожалуйста отправьте фотографию")
    
    
@admin_user_handler.message(F.text,F.text.isdigit(), StateFilter(AdminTourMode.set_max_people))
async def set_tour_max_people(message: Message, state:FSMContext):
    people_number = int(message.text)
    await state.update_data(max_people = people_number)
    await state.set_state(AdminTourMode.set_duration)
    await message.answer("Введите длительность тура, можно например: 3 часа 20 мин")
    
@admin_user_handler.message(StateFilter(AdminTourMode.set_max_people))
async def wrong_max_number(message: Message, state:FSMContext):
    await message.answer("Введите положительно число людей")
    
    
    
    
@admin_user_handler.message(F.text, StateFilter(AdminTourMode.set_duration))
async def set_tour_duration(message: Message, state:FSMContext):
    tour_duration = message.text.strip()
    await state.update_data(duration = tour_duration)
    await state.set_state(AdminTourMode.set_category)
    await message.answer("Введите категорию тура: водный, пеший, автобус, машина")
    
@admin_user_handler.message(StateFilter(AdminTourMode.set_duration))
async def wrong_duration(message: Message, state:FSMContext):
    await message.answer("Укажите длительность текстом!!!")
    
@admin_user_handler.message(F.text, StateFilter(AdminTourMode.set_category))
async def set_tour_category(message: Message, state:FSMContext):
    tour_category = message.text.strip()
    await state.update_data(category = tour_category)
    await state.set_state(AdminTourMode.set_meeting_point)
    await message.answer("Введите место встречи")
    
@admin_user_handler.message(StateFilter(AdminTourMode.set_category))
async def wrong_category(message: Message, state:FSMContext):
    await message.answer("Укажите длительность текстом!!!")
    

@admin_user_handler.message(F.text, StateFilter(AdminTourMode.set_meeting_point))
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
    
@admin_user_handler.message(StateFilter(AdminTourMode.set_meeting_point))
async def wrong_meeting_point(message: Message, state:FSMContext):
    await message.answer("Укажите место встречи текстом текстом!!!")

        
# изменение тура
@admin_user_handler.callback_query(F.data.startswith('change_tour'))
async def change_tour_mode(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''при нажатии на кнопку изменения определенной landmark'''
    await state.clear()
    tour_id = int(callback.data.split('_')[-1])
    await state.set_state(AdminTourMode.set_param_for_change)
    await state.update_data(id=tour_id)
    tour_db_manager = db_managers.TourManager()
    all_params = tour_db_manager.show_model_columns_lst()
    msg_text = ',\n'.join(tour_db_manager.show_model_columns_lst())
    await state.update_data(table_columns=all_params)  # сохраняем столбцы таблицы для проверок в дальнейших хэндлерах
    await callback.message.answer(f"Активирован режим изменения параметров тура, введите параметр для изменения:\n{msg_text}")
    
    
@admin_user_handler.message(F.text,  StateFilter(AdminTourMode.set_param_for_change))
async def set_param_to_change(message: Message, state:FSMContext):
    '''сообщение с именем параметра для изменения выбранного тура'''
    data = await state.get_data()
    table_columns =  data.get('table_columnds')# столбцы таблицы для проверки введеного админом столбца
    # небольшая проверка что бы параметры от админа соответс столбцам таблицы
    if message.text.lower().strip() not in table_columns:
        await message.answer(f"Пожалуйста введите имя параметра из списка {'\n'.join(table_columns)}")
        return
    await state.update_data(param=message.text.lower().strip())# имя параметра для изменения
    await message.answer("Отлично, теперь введите значение")
    await state.set_state(AdminTourMode.set_new_value)
    
@admin_user_handler.message(F.photo, StateFilter(AdminTourMode.set_new_value))
@admin_user_handler.message(F.text,StateFilter(AdminTourMode.set_new_value))
async def set_value_for_param(message: Message, state:FSMContext, session:AsyncSession):
    '''если фотку скинули то взять с нее ссылку, в остальных случаях берем текст сообщения'''
    try:
        # Определение нового значения
        new_value = message.photo[-1].file_id if message.photo else message.text # на случай если фото отправят
        await state.update_data(new_value=new_value)
        update_info = await state.get_data()
        # процесс обновления данных в БД
        tour_db_manager = db_managers.TourManager()
        result = await tour_db_manager.update_from_state(session, update_info)# берет все нобходимые данные из state и обновляет значеия в БД
        back_kb = create_inline_kb([{'text':'назад', 'callback_data':f"show_tour_{update_info['id']}"}])
        await state.clear()
        if result:
            await session.commit()
            await message.answer("обновление параметра прошло успешно",reply_markup=back_kb)
        else:
            await message.answer("ОШибка при обновлении параметра, чекай логи", reply_markup=back_kb)
    except Exception as err:
        logger.error(f"Ошибка в хэндлере при изменении ппрпметров landmark : {err}")
        await message.answer(f"Внутренняя лшибка в хэндлере :{err}", reply_markup=back_kb)
        
        
#процесс удаление тура
@admin_user_handler.callback_query(F.data.startswith('delete_tour'))
async def activate_deleting_mode(callback: CallbackQuery):
    '''админ выбрал удаление тура, нужно подтверждение дейтсвия(защита от дурака)'''
    tour_id = int(callback.data.split('_')[-1])
    yes_no_kb = create_inline_kb([{'text':'ДА,удалить','callback_data':f"confirm_deleting_tour_{tour_id}"},
                                  {'text':'Нет, отмена', 'callback_data':f"show_tour_{tour_id}"}])
    await callback.message.answer("Вы точно хотите удалить данный тур?", reply_markup=yes_no_kb)        
        

@admin_user_handler.callback_query(F.data.startswith('confirm_deleting_tour'))
async def delete_current_tour(callback: CallbackQuery, session : AsyncSession):
    '''Действие когда юзер подтвердил удаление тура'''
    current_tour_id = int(callback.data.split('_')[-1])
    tour_db_manager = db_managers.TourManager()
    delete_result = await tour_db_manager.delete(session, current_tour_id)
    if delete_result:
        await session.commit() 
        await callback.answer(f"Тур с id : {current_tour_id} удалена успешно", show_alert=True)
    else:
        await callback.message.answer(f"Ошибка при удалении тура с id : {current_tour_id}, чекай логи")
        

    
# @admin_user_handler.callback_query(F.data.startswith('tour_'), StateFilter(AdminTourMode.edit_select_product))
# async def get_tour_for_change(callback: CallbackQuery, state:FSMContext):
#     product_id = int(callback.data.split('_')[-1])
#     await state.update_data(id=product_id)
#     await state.set_state(AdminTourMode.edit_choose_field)
#     await callback.message.answer("Товар для изменения выбран, введите поля для изменения") # тут клава будет адаптированная под столбцы текущего тура
    
# @admin_user_handler.callback_query(F.data.startswith('edit_photo'), StateFilter(AdminTourMode.edit_choose_field))
# async def get_photo_for_change(callback: CallbackQuery, state:FSMContext):
#     img = callback.message.photo[-1]
#     img_id = img.file_id
#     await state.update_data(product_photo_id = img_id)
#     # процесс изменения полей
#     await callback.message.answer("выбранное поле успешно изменено, желаете изменить что то еще?") # тут клава будет адаптированная под столбцы текущего тура
    
    




