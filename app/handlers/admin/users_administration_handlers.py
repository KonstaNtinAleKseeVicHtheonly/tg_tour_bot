from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#KB

from app.keyboards.admin_kb.inline_keyboards import all_users_kb, current_user_kb
from app.keyboards.base_keyboards import create_inline_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import AdminUsersMode
# системыне утилиты

from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database import db_managers
from app.database.all_models.models import User
from app.database.db_queries import _show_all_users_query, get_current_user_query
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
    

@admin_user_handler.callback_query(F.data=='show_all_users')
async def show_all_users(callback: CallbackQuery, session : AsyncSession):
    all_users = await _show_all_users_query(session)
    await callback.message.answer("Вот список всех юзеров", reply_markup = await all_users_kb(all_users) ) # выведет список всех пользователей


@admin_user_handler.callback_query(F.data.startswith('show_current_user'))
async def show_current_user(callback: CallbackQuery, session : AsyncSession):
    '''по Id юзера выводит развернутую инфу о нем и кнопки'''
    current_user_id = int(callback.data.split('_')[-1])
    user_db_manager = db_managers.UserManager()
    user_info = await user_db_manager.show_detailed_info_for_user(session, current_id=current_user_id)
    await callback.message.answer(user_info, reply_markup = current_user_kb(current_user_id) ) # выведет список всех пользователей



@admin_user_handler.callback_query(F.data.startswith("delete_user"))
async def delete_curent_user(callback: CallbackQuery, session : AsyncSession):
    current_user_id = int(callback.data.split('_')[-1])
    user_db_manager = db_managers.UserManager()
    delete_result = await user_db_manager.delete(session, id=current_user_id)# текущей юзер
    back_to_menu_kb = create_inline_kb([{'text':'Назад', 'callbac_data':'admin_interactive_menu'}])
    if not delete_result:
        await callback.message.answer(f"Ошибка при удалении юзера с id {current_user_id}, чекай логи", reply_markup=back_to_menu_kb)
    else:
        await session.commit()
        await callback.message.answer(f"Юзер с id {current_user_id} успешно удален из БД", reply_markup=back_to_menu_kb)
        




