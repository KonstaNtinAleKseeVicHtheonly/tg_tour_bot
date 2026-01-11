from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from aiogram.filters import CommandStart, Command
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from datetime import datetime
import asyncio
import uuid
import os
from dotenv import load_dotenv
#KB
from app.keyboards.reply_kb import admin_reply_kb
# from app.keyboards.base_keyboards import reply_main_menu, inline_main_menu, request_user_contact, get_categories_kb, get_cards_kb, product_kb, client_location
# FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import AdminTourMode
# колбэки
from aiogram.types import CallbackQuery
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




# @tg_group_handler.message(Command('odmen'))
# async def activate_admin_mode(message : Message, bot : Bot):
#     '''активирует режим дмин панели даваю юзеру доп полномочия, если id юзера состоит в admin_id конечно'''
#     is_admin = await check_admin(message)
#     if not is_admin:
#         await message.answer("Вы не обладаете полномочиями для данной команды")
#         return
#     logger.warning(f"Юзер : {message.from_user.username} с id {message.from_user.id} активировал режим админ панели")
#     await message.delete()
#     await message.answer("Режим админа усешно активирован")
#     await message.answer("Что хотите выбрать?" , reply_markup=admin_reply_kb)

# @tg_group_handler.message(Command('show_admins'))
# async def show_group_admins(message : Message, bot : Bot):
#     '''показывает всех юзеров и ботов группы с полночиями creator или administrator'''
#     is_admin = await check_admin(message)
#     if is_admin:
#         admins_id_lst = await _get_admins_id()
#         await message.answer(f"вот список с id всех админов : {'\n |'.join(admins_id_lst)}")
#     else:
#         await message.answer("Вы не обладаете полномочиями для данной команды")


@tg_group_handler.edited_message()# на случай если отредактируют старые сообщения и запишут плохие слова
@tg_group_handler.message(F.text)
async def censorship(message : Message):
    '''проверка сообщений юзер на запрещенные слова'''
    if await check_banned_words(message):
        await message.delete()
        await message.answer(f"Ненормативаня лексика запрещена в данной групе.\n {message.from_user.username} пожалуйста соблюдайте порядок в чате")