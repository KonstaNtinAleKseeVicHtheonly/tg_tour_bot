from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
# фитры 
from aiogram.filters import CommandObject, Command, CommandObject, StateFilter,and_f,or_f
#KB
from app.keyboards.admin_kb.inline_keyboards import admin_inline_main_menu, admin_inline_interaction_kb
#FSM
from aiogram.fsm.context import FSMContext
# системыне утилиты
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter

#утилиты
from app.utils.env_utils import _get_admins_id
#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_main_handler = Router()
admin_main_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами


@admin_main_handler.message(Command('odmen'))
async def activate_admin_mode(message : Message, state:FSMContext):
    '''активирует режим дмин панели даваю юзеру доп полномочия, если id юзера состоит в admin_id конечно'''
    logger.warning(f"Юзер : {message.from_user.username} с id {message.from_user.id} активировал режим админ панели")
    await state.clear() # на всякий случай сбросим состояние
    await message.delete()
    await message.answer("Режим админа усешно активирован")
    await message.answer("Что хотите выбрать?" , reply_markup=admin_inline_main_menu)
    
@admin_main_handler.callback_query(F.data=='admin_main_menu')
async def admin_main_menu(callback: CallbackQuery):
    '''покажет главное меню админа'''
    await callback.message.answer("Что хотите посмотреть?", reply_markup = admin_inline_main_menu) # выведет список всех достопримечательностей

    
@admin_main_handler.callback_query(F.data=='admin_interactive_menu')
async def interaction_mode(callback: CallbackQuery):
    '''покажет кнопки с возможностью посмотреть все туры и достопримечательности (углубление в интерактивынй режим через колбэки)'''
    await callback.message.answer("Что хотите посмотреть?", reply_markup = admin_inline_interaction_kb) # выведет список всех достопримечательностей

@admin_main_handler.message(Command('cancel'))
@admin_main_handler.message(Command('cancel'), StateFilter('*'))
@admin_main_handler.message(F.text.lower()=='отмена', StateFilter('*'))
async def cancel_processes(message:Message, state:FSMContext):
    '''Команда отмены и выхода их всех FSM'''
    
    current_state = await state.set_state() # есть ли текущее FSM состояние
    if current_state is not  None:
        await state.clear()
        
    await message.delete()
    await message.answer("Вы вышли из текущего режима")
        
    
@admin_main_handler.message(Command('show_admins'))
async def show_group_admins_id(message : Message, bot : Bot):
    '''показывает всех юзеров и ботов группы с полночиями creator или administrator'''
    admins_id_lst = await _get_admins_id()
    await message.answer(f"вот список с id всех админов : {'|'.join(admins_id_lst)}")
    
    