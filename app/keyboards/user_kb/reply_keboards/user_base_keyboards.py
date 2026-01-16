from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from project_logger.loger_configuration import setup_logging



def request_user_contact():
    return ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='выбрать контакт', request_contact=True)]
], resize_keyboard=True, input_field_placeholder="Выберите свой номер из контактов или введие вручную")