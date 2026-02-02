from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging


logger = setup_logging()




async def all_tours_kb(all_tours):
    '''по запросу из БД показывает в кнопках все достопримечательности'''
    try:
        if not all_tours:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что нет туров", callback_data="admin_interactive_menu")]])
        all_tours_kb = InlineKeyboardBuilder()
        for tour in all_tours:
            all_tours_kb.add(InlineKeyboardButton(text = f"{tour.name}", callback_data=f"show_tour_admin_{tour.id}"))
        all_tours_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
        return all_tours_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех туров: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])

    
    
def current_tour_kb(tour_id:int):
    '''из базы берет по Id нужную достопримеательность и формирует клаву на изменение, обновление тура'''
    current_tour_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'изменить', callback_data=f"change_tour_{tour_id}"),InlineKeyboardButton(text = 'удалить', callback_data=f"delete_tour_{tour_id}")],
                                          [InlineKeyboardButton(text = 'назад', callback_data="show_all_tours_admin")]])
    return current_tour_kb
    
