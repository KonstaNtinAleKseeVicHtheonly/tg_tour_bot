from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, Message,ContentType
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#KB
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.admin_kb.inline_keyboards import all_associations_kb_with_names, show_current_association, show_all_tours_for_association, show_all_lm_for_association, bound_tour_kb,  bound_lm_kb
from app.keyboards.base_keyboards import create_inline_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import Admin_LM_Tour_Bound_Mode
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

admin_tour_lm_association_handler = Router()
admin_tour_lm_association_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами



@admin_tour_lm_association_handler.message(StateFilter(Admin_LM_Tour_Bound_Mode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
@admin_tour_lm_association_handler.callback_query(F.data=='show_all_associations')
async def show_all_tour_lm_bounds(callback: CallbackQuery, session : AsyncSession):
    lm_tour_db = db_managers.TourLMAssociationManager()
    all_bounds = await lm_tour_db.show_ordered_associations_with_names(session) # выведет все ассоциации отсортированные 
    await callback.message.answer("Вот список всех связей", reply_markup = all_associations_kb_with_names(all_bounds)) # выведет список всех достопримечательностей


@admin_tour_lm_association_handler.callback_query(F.data=='create_association')
async def start_association_creating(callback: CallbackQuery, session:AsyncSession):
    await callback.message.answer("Активирован режим создания связи между туром и достопримечательностью")
    tour_db_manager = db_managers.TourManager()
    all_tours = await tour_db_manager.get_all(session)
    await callback.message.answer("Пожалуйста выберите тур с которым хотите сделать связь", reply_markup=await show_all_tours_for_association(all_tours))
    
    
@admin_tour_lm_association_handler.callback_query(F.data.startswith('add_bound_tour'))
async def set_lm_for_bound(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    tour_id = int(callback.data.split('_')[-1])
    await state.update_data(tour_id=tour_id)
    lm_db_manager = db_managers.LandMarkManager()
    all_lm = await lm_db_manager.get_all(session)
    await callback.message.answer("Теперь выберите достопримечательность", reply_markup=await show_all_lm_for_association(all_lm))
    
@admin_tour_lm_association_handler.callback_query(F.data.startswith('add_bound_lm'))
async def create_new_bound(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''по собранным id у tour и lm создает связь если ее не было дэ этого'''
    lm_id = int(callback.data.split('_')[-1])
    await state.update_data(landmark_id = lm_id)
    associations_db_manager = db_managers.TourLMAssociationManager()
    bound_info = await state.get_data()
    back_to_menu = create_inline_kb([{'text':'назад к меню','callback_data':'admin_interactive_menu'}])
    # InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад к меню', callback_data='admin_interactive_menu')]])
    create_bound = await associations_db_manager.create(session, bound_info)
    if create_bound:
        await session.commit()
        await callback.message.answer("связь создана успешно", reply_markup= back_to_menu)
    else:
        await callback.message.answer("Скорее всего таакая сыязь уже есть чека логи", reply_markup=back_to_menu)
    await state.clear()
    
    
@admin_tour_lm_association_handler.message(StateFilter(Admin_LM_Tour_Bound_Mode.set_tour_id))
async def invalid_tour_id(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введи целочисленный id тура из бд")
    
@admin_tour_lm_association_handler.callback_query(F.data.startswith('current_bound'))
async def get_current_tour_lm_bound(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''покажет текущую строку из таблицы many to many'''
    current_tour_id, current_lm_id = [int(elem) for elem in callback.data.split('_')[-2:]] # из колбэка вычленяем id Тура и landmark
    # передача значений id объектов что бы потом можно было вернуться в меню с данной парой в дальнейшем(формировать правильный callback)
    await state.set_state(Admin_LM_Tour_Bound_Mode.current_bound) # в течение взаимодействия бд прокидываем инфу о tour и landmark
    await state.update_data(current_bound_tour_id=current_tour_id)
    await state.update_data(current_bound_lm_id=current_lm_id)
    bound_db_manager = db_managers.TourLMAssociationManager()
    current_bound = await bound_db_manager.get_current_association(session, tour_id=current_tour_id, landmark_id=current_lm_id)
    await callback.message.answer("Вот пара для изменения",reply_markup = show_current_association(current_bound))
    
    
@admin_tour_lm_association_handler.callback_query(F.data.startswith('show_bound_tour'), StateFilter(Admin_LM_Tour_Bound_Mode.current_bound))
async def get_current_tour_bound(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''Выбран тур из текущей связи(пара тур - Lanmdark), отобразить возмохность изменения'''
    current_tour_id =  int(callback.data.split('_')[-1])
    tour_db_manager = db_managers.TourManager()
    current_tour= await tour_db_manager.get(session, id=current_tour_id)
    current_association_data = await state.get_data()
    general_lm_id = current_association_data['current_bound_lm_id']
    if not current_tour:
        back_kb = create_inline_kb([{'text':'назад', 'callback_data':f"current_bound_{current_tour_id}_{general_lm_id}"}])
        await callback.message.answer("ошибка отображения", reply_markup=back_kb)
        return
    await callback.message.answer_photo(photo = current_tour.image_url,
                                            caption = f'''ID:{current_tour.id}{current_tour.name}\n
                                            {current_tour.description}''',
                                            reply_markup = bound_tour_kb(current_tour_id, current_association_data['current_bound_lm_id']))
    
@admin_tour_lm_association_handler.callback_query(F.data.startswith('show_bound_landmark'), StateFilter(Admin_LM_Tour_Bound_Mode.current_bound))
async def get_current_lm_bound(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''Выбран lm из текущей связи(пара тур - Lanmdark), отобразить возмохность изменения'''
    tour_db_manager = db_managers.LandMarkManager()
    current_lm_id =  int(callback.data.split('_')[-1])
    current_lm = await tour_db_manager.get(session, id=current_lm_id)
    current_association_data = await state.get_data()
    general_tour_id = current_association_data['current_bound_tour_id']
    if not current_lm:
        back_kb = create_inline_kb([{'text':'назад', 'callback_data':f"current_bound_{general_tour_id}_{current_lm_id}"}])
        await callback.message.answer("ошибка отображения", reply_markup=back_kb)
        return
    await callback.message.answer_photo(photo = current_lm.image_url,
                                            caption = f'''ID:{current_lm.id}{current_lm.name}\n
                                            {current_lm.description}''',
                                            reply_markup = bound_lm_kb(general_tour_id, current_lm_id ))
    
    
    
@admin_tour_lm_association_handler.callback_query(F.data=='change_bound_tour', StateFilter(Admin_LM_Tour_Bound_Mode.current_bound))
async def change_current_lm_bound(callback: CallbackQuery,state:FSMContext, session:AsyncSession):
    '''из выбранной пары tour-lm выбран tour'''
    await state.set_state(Admin_LM_Tour_Bound_Mode.change_tour_bound)
    tour_db_manager = db_managers.TourManager()
    # в строке покажу все туры и их id, что бы можно было сразу прописать новый тур прочитва из списка
    all_tours = await tour_db_manager.get_all(session)
    tours_text_description = "Список туров:\n"
    for tour in all_tours:
        current_tour_description = f"ID тура: {tour.id}| НАзвание тура{tour.name}\n"
        # Если добавление превысит лимит, отправим накопившиеся и по новой начнем набирать
        if len(current_tour_description) + len(tours_text_description) > 4000:
            await callback.message.answer(tours_text_description)
            tours_text_description = "Список туров(продолжение):\n" + current_tour_description
        else:
            tours_text_description += current_tour_description
    if tours_text_description:
        await callback.message.answer(tours_text_description)
        await callback.message.answer("Введите id тура на который хотите поменяь предыдущий")
    
    
@admin_tour_lm_association_handler.callback_query(F.data=='change_bound_lm', StateFilter(Admin_LM_Tour_Bound_Mode.current_bound))
async def change_current_tour_bound(callback: CallbackQuery,state:FSMContext, session:AsyncSession):
    '''из выбранной пары tour-lm выбран lm'''
    await state.set_state(Admin_LM_Tour_Bound_Mode.change_lm_bound)
    lm_db_manager = db_managers.LandMarkManager()
    # в строке покажу все достопримечательносит и их id, что бы можно было сразу прописать новый тур прочитва из списка
    all_lm = await lm_db_manager.get_all(session)
    landmarks_text_description = "Список landmarks:\n"
    for lm in all_lm:
        current_lm_description = f"ID lm: {lm.id}| НАзвание lm{lm.name}\n"
        # Если добавление превысит лимит, отправим накопившиеся и по новой начнем набирать
        if len(current_lm_description) + len(landmarks_text_description) > 4000:
            await callback.message.answer(landmarks_text_description)
            landmarks_text_description = "Список landmarks(продолжение):\n" + current_lm_description
        else:
            landmarks_text_description += current_lm_description
    if landmarks_text_description:
        await callback.message.answer(landmarks_text_description)
        await callback.message.answer("Введите id достопримечательности на который хотите поменяь предыдущий")
    
    
@admin_tour_lm_association_handler.message(F.text, F.text.isdigit(),StateFilter(Admin_LM_Tour_Bound_Mode.change_lm_bound))
async def get_new_lm_bound_id(message:Message, state:FSMContext, session:AsyncSession):
    '''получаем от юзера id нового lanmdark для пары'''
    logger.info("поймал id landmark для обновления")
    lm_changing_info = await state.get_data()
    new_lm_id = int(message.text)
    # берем из FSM инфу о старом landmark и общем tour
    general_tour_id = lm_changing_info.get('current_bound_tour_id')
    old_lm_id = lm_changing_info.get('current_bound_lm_id')
    bound_db_manager = db_managers.TourLMAssociationManager()
    updating_result = await bound_db_manager.update(
        session,
        data_to_find_object={'tour_id':general_tour_id,'landmark_id':old_lm_id},
        data_to_update_object={'landmark_id':new_lm_id})
    if updating_result:
        await session.commit()
        updating_result_kb = create_inline_kb([{'text':'перейти к обновленной паре','callback_data':f"current_bound_{general_tour_id}_{new_lm_id}"}])# вернет к обновленной паре тура и lm
        await message.answer("пара успешно обновлена", reply_markup=updating_result_kb)
    else: # вернет к старой паре тура и lm
        failed_result = create_inline_kb([{'text':'назад','callback_data':f"current_bound_{general_tour_id}_{old_lm_id}"}])
        await message.answer("Ошибка при изменении пары, чекай логи", reply_markup=failed_result)


@admin_tour_lm_association_handler.message(F.text, F.text.isdigit(),StateFilter(Admin_LM_Tour_Bound_Mode.change_tour_bound))
async def get_new_tour_bound_id(message:Message, state:FSMContext, session:AsyncSession):
    logger.info("поймал id тура для обновления")
    tour_changing_info = await state.get_data()
    new_tour_id = int(message.text)
    # берем из FSM инфу о старом туре и общем landmark 
    old_tour_id = tour_changing_info.get('current_bound_tour_id')
    general_lm_id = tour_changing_info.get('current_bound_lm_id')
    bound_db_manager = db_managers.TourLMAssociationManager()
    updating_result = await bound_db_manager.update(
        session,
        data_to_find_object={'tour_id':old_tour_id,'landmark_id':general_lm_id},
        data_to_update_object={'tour_id':new_tour_id})
    if updating_result:
        await session.commit()
        updating_result_kb = create_inline_kb([{'text':'перейти к обновленной паре','callback_data':f"current_bound_{new_tour_id}_{general_lm_id}"}])# вернет к обновленной паре тура и lm
        await message.answer("пара успешно обновлена", reply_markup=updating_result_kb)

    else: # вернет к старой паре тура и lm
        failed_result = create_inline_kb([{'text':'назад','callback_data':f"current_bound_{old_tour_id}_{general_lm_id}"}])
        await message.answer("Ошибка при изменении пары, чекай логи", reply_markup=failed_result)
        
    
    
    
@admin_tour_lm_association_handler.message(StateFilter(Admin_LM_Tour_Bound_Mode.change_tour_bound))
async def wrong_new_tour_bound(message:Message, session:AsyncSession):
    await message.answer("Введи числовой id тура который хочишь добавить в пару!!!")
    
@admin_tour_lm_association_handler.message(StateFilter(Admin_LM_Tour_Bound_Mode.change_lm_bound))
async def wrong_new_lm_bound(message:Message, session:AsyncSession):
    await message.answer("Введи числовой id достопримечательности который хочишь добавить в пару!!!")