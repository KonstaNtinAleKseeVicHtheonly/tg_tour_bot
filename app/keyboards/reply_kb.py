from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from project_logger.loger_configuration import setup_logging

logger = setup_logging()

reply_main_menu = ReplyKeyboardMarkup(keyboard=[
                                                [
                                                KeyboardButton(text='/menu'), 
                                                KeyboardButton(text='/show_me')
                                                ],
                                                [
                                                KeyboardButton(text='/about') 
                                                ]
                                                ], 
                                      resize_keyboard=True)

reply_request_kb = ReplyKeyboardMarkup(keyboard=[
                                                [
                                                KeyboardButton(text='номер телефона',request_contact=True), 
                                                KeyboardButton(text='местоположение', request_location=True),
                                                KeyboardButton(text='сделать опрос🤡', request_poll=KeyboardButtonPollType())
                                                ],
                                                ], 
                                      resize_keyboard=True)

delete_reply_kb = ReplyKeyboardRemove() # удаление предыдущей клавиатуры

admin_reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='изменить тур'), KeyboardButton(text='добавить тур'),KeyboardButton(text='удалить тур')],
        [KeyboardButton(text='изменить landmark'), KeyboardButton(text='добавить landmark'),KeyboardButton(text='удалить landmark')],
        [KeyboardButton(text='показать все туры'), KeyboardButton(text='все достопримечательности')]
    ],
    resize_keyboard=True
)