from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging




logger = setup_logging()




async def all_banners_kb(banners_lst:list):
    '''по запросу из БД показывает в кнопках все достопримечательности'''
    try:
        if not banners_lst:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что их нет", callback_data="admin_interactive_menu")]])
        all_banners_kb = InlineKeyboardBuilder()
        for banner in banners_lst:
            all_banners_kb.add(InlineKeyboardButton(text = f"{banner.name}", callback_data=f"show_banner_{banner.id}"))
        all_banners_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
        return all_banners_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех LM: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])

    
    
def current_banner_kb(banner_id:int):
    '''берет по Id нужный банер и формирует клаву на изменение, обновление LM'''
    current_banner_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'изменить', callback_data=f"change_banner_{banner_id}"),InlineKeyboardButton(text = 'удалить', callback_data=f"delete_banner_{banner_id}")],
                                          [InlineKeyboardButton(text = 'назад', callback_data="show_all_banners")]])
    return current_banner_kb
