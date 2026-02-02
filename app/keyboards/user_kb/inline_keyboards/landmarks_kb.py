from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging




logger = setup_logging()



    
    
async def current_tour_landmarks_kb(tour_id:int, landmarks_lst:list)-> InlineKeyboardMarkup:
    '''принимает id тура и список связанных с ним landmarks по ним делает адаптивную клавиутару
    В callback указываю id достопримечательности и id Тура'''
    try:
        if not landmarks_lst:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Пока что нет информации', callback_data=f"show_tour_{tour_id}")]])
        all_lm_kb = InlineKeyboardBuilder()
        for lm in landmarks_lst:
            all_lm_kb.add(InlineKeyboardButton(text = f"{lm.name}", callback_data=f"show_landmark_{lm.id}|tour_{tour_id}"))
        all_lm_kb.row(InlineKeyboardButton(text='назад',callback_data=f"show_tour_{tour_id}"))
        return all_lm_kb.adjust(2).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех LM: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])

