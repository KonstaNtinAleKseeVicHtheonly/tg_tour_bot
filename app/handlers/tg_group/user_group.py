from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from aiogram.filters import CommandStart, Command
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from dotenv import load_dotenv
#KB
from app.keyboards.reply_kb import admin_reply_kb

# FSM
from app.FSM.admin_states.states import AdminTourMode
# DB
#фильтры
from app.filters.chat_group_filters import GroupFilter

#утилиты
from app.utils.censcorship_tools import check_banned_words
from app.utils.env_utils import check_admin, _get_admins_id
load_dotenv()
logger = setup_logging()


tg_group_handler = Router()
tg_group_handler.message.filter(GroupFilter(['group','supergroup']))# проверка что сообщения поступают только в группа а не в сам бот





@tg_group_handler.edited_message()# на случай если отредактируют старые сообщения и запишут плохие слова
@tg_group_handler.message(F.text)
async def censorship(message : Message):
    '''проверка сообщений юзер на запрещенные слова'''
    if await check_banned_words(message):
        await message.delete()
        await message.answer(f"Ненормативаня лексика запрещена в данной групе.\n {message.from_user.username} пожалуйста соблюдайте порядок в чате")