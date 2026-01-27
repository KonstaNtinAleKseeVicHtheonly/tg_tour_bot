from aiogram import F, Router
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from aiogram.filters import CommandStart, Command
from app.filters.chat_group_filters import GroupFilter
from app.filters.admin_filters import AdminFilter
#KB
from app.keyboards.user_kb.inline_keyboards import user_inline_main_menu,  all_tours_kb, current_tour_kb, current_tour_landmarks_kb, set_payment_type_kb, successful_order_kb, all_user_orders_kb, current_order_kb
from app.keyboards.base_keyboards import create_inline_kb
from app.keyboards.user_kb.reply_keboards import request_user_contact
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.FSM.user_states.states import UserRegistration, NewOrder
from aiogram.filters import StateFilter, or_f
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from dotenv import load_dotenv

# DB
from app.database import db_managers
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_queries import get_current_banner_query, get_current_lm_query, get_all_tours_query, get_current_tour_query, get_tour_landmarks_query, get_tour_detailed_info_query, check_user_existance, _create_new_user_query, get_current_user_query, can_book_query, calculate_total_price_query# слой абстракции для менеджера БД(маленькая связанность)
from app.database.all_models.models import OrderStatus
logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env





user_tour_handler = Router()
user_tour_handler.message.filter(GroupFilter(['private']))


@user_tour_handler.callback_query(F.data=='show_all_tours')
async def show_all_tours(callback: CallbackQuery, session : AsyncSession):
    await callback.message.delete()
    all_tours = await get_all_tours_query(session)
    all_tours_banner = await get_current_banner_query(session, banner_name='tours_banner')
    tours_kb = await all_tours_kb(all_tours)
    if all_tours_banner:
        await callback.message.answer_photo(photo = all_tours_banner.image,caption = all_tours_banner.description, 
                                            reply_markup = tours_kb)
    else:
        await callback.message.answer("Вот список всех туров", reply_markup= tours_kb)
    
    
@user_tour_handler.callback_query(F.data.startswith('show_tour'))
async def get_current_tour_info(callback: CallbackQuery, session:AsyncSession):
    await callback.message.delete()
    current_tour_id =  int(callback.data.split('_')[-1])
    current_tour= await get_current_tour_query(session, current_tour_id) 
    if not current_tour:
        back_to_common_info = create_inline_kb([{'text':'Назад', 'callback_data':'show_all_tours'}])
        await callback.message.asnwer("по данному туру нет информации к сожалению", reply_markup = back_to_common_info)
    else:
        await callback.message.answer_photo(photo = current_tour.image_url,
                                                caption = f'''{current_tour.name}\n
                                                {current_tour.description}''',
                                                reply_markup = current_tour_kb(current_tour_id))
    
    
@user_tour_handler.callback_query(F.data.startswith("detailed_info_tour"))
async def show_tour_detailed_info(callback: CallbackQuery, session : AsyncSession):
    '''детальная инфа о туре'''
    await callback.message.delete()
    current_tour_id =  int(callback.data.split('_')[-1])
    back_to_common_info = create_inline_kb([{'text':'Назад', 'callback_data':f"show_tour_{current_tour_id}"}])
    current_tour= await get_current_tour_query(session=session, tour_id=current_tour_id) 
    if not current_tour:
        await callback.message.answer("Детальная информация по данной экскурсии пока что отсутствует",reply_markup=back_to_common_info)
    else:
        detailed_info = await get_tour_detailed_info_query(session, tour_id=current_tour_id, current_skip_fields=['description', 'id', 'updated_at', 'created_at', 'image_url'])
        await callback.message.answer(detailed_info, reply_markup=back_to_common_info)
        