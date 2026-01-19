'''Прост создал заготовки для текста постов и банеров в отдельном файле'''
from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Еда', 'Напитки']

description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Добро пожаловать в компанию БелТур",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",

        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Туры:',
    'cart': 'В корзине ничего нет!'
}