from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.all_models.models import User



logger = setup_logging()




async def all_users_kb(all_users:list[User]):
    '''по запросу из БД показывает в кнопках всех юзеров с воомжностью CRUD Операций'''
    try:
        if not all_users:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что нет юзеров", callback_data="admin_interactive_menu")]])
        all_users_kb = InlineKeyboardBuilder()
        for user in all_users:
            all_users_kb.add(InlineKeyboardButton(text = f"{user.username}", callback_data=f"show_current_user_{user.id}"))
        all_users_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
        return all_users_kb.adjust(2).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы вывода вех юзеров для админа: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])

    

    
def current_user_kb(user_id:int):
    '''по id текущего юзера и формирует клаву на удаление юзера, показ его заказов'''
    current_user_kb = InlineKeyboardMarkup(inline_keyboard=[
                                                             [InlineKeyboardButton(text = 'Заказы пользователя', callback_data=f"admin_user_orders_{user_id}")],
                                                             [InlineKeyboardButton(text = 'удалить', callback_data=f"delete_user_{user_id}")],
                                                            [InlineKeyboardButton(text = 'назад', callback_data="show_all_users")]
                                                            ])
    return current_user_kb
    
