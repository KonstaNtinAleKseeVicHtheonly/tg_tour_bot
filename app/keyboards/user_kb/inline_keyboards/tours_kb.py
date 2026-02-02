from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging



logger = setup_logging()




async def all_tours_kb(all_tours):
    '''по запросу из БД показывает в кнопках все достопримечательности'''
    try:
        if not all_tours:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что нет туров, вернитесь назад", callback_data="user_main_menu")]])
        all_tours_kb = InlineKeyboardBuilder()
        for tour in all_tours:
            all_tours_kb.add(InlineKeyboardButton(text = f"{tour.name}", callback_data=f"show_tour_{tour.id}"))
        all_tours_kb.row(InlineKeyboardButton(text='назад',callback_data="user_main_menu"))
        return all_tours_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех туров: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="user_main_menu")]])

    
    
def current_tour_kb(tour_id:int):
    '''из базы берет по Id нужный тур и формирует клаву на показ инфы о нем'''
    current_tour_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'подробная информация о туре', callback_data=f"detailed_info_tour_{tour_id}"),
                                                             InlineKeyboardButton(text = 'достопримечательности тура', callback_data=f"tour_landmarks_{tour_id}")],
                                                            [InlineKeyboardButton(text = 'купить', callback_data=f"buy_tour_{tour_id}")],
                                          [InlineKeyboardButton(text = 'назад', callback_data="show_all_tours")]])
    return current_tour_kb
    
