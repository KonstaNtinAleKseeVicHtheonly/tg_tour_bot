from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers
from app.database.all_models.models import TourLandmarkAssociation


logger = setup_logging()




    
    
def all_associations_kb_with_names(tour_lm_bounds_lst:list) -> InlineKeyboardMarkup:
    """Клавиатура с названиями туров и достопримечательностей"""
    if not tour_lm_bounds_lst: # если пустой список значит ошибка пи выводе связей либо их попросту нет
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='нет данных о связях,вернитесь назад', callback_data="admin_interactive_menu")]])
    builder = InlineKeyboardBuilder()
    
    for bound in tour_lm_bounds_lst:
        # Получаем названия
        builder.add(InlineKeyboardButton(text=f"Пара:{bound.tour.name}|{bound.landmark.name}", callback_data=f"current_bound_{bound.tour.id}_{bound.landmark.id}"))
    builder.row(InlineKeyboardButton(text='назад', callback_data="admin_interactive_menu"))
    
    builder.adjust(1)  # вертикальный список
    return builder.as_markup()


def show_current_association(current_association:TourLandmarkAssociation):
    '''Формирует по паре тура и lm из ассоциативной таблицы клавиатура взаимодействия с каждым из них 
    (через прокидывание callback-ов в соотв хэндлеры админа landmarks_h и tour_h)'''
    current_association_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=current_association.tour.name, callback_data=f"show_bound_tour_{current_association.tour.id}"),
                                                                    InlineKeyboardButton(text=current_association.landmark.name, callback_data=f"show_bound_landmark_{current_association.landmark.id}")],
                                                                   [InlineKeyboardButton(text="назад", callback_data="show_all_associations")]
                                                                   ])
    return current_association_kb




async def show_all_tours_for_association(all_tours_lst:list)-> InlineKeyboardMarkup:
    '''адаптиваня клавиатура  показывающая клаву с турами для их выбора в связь'''
    try:
        if not all_tours_lst:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что нет туров, вернитесь назад", callback_data="admin_interactive_menu")]])
        all_tours_kb = InlineKeyboardBuilder()
        for tour in all_tours_lst:
            all_tours_kb.add(InlineKeyboardButton(text = f"ID:{tour.id}{tour.name}", callback_data=f"add_bound_tour_{tour.id}"))
        all_tours_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
        return all_tours_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех туров: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])
    
async def show_all_lm_for_association(all_lm_lst:list)-> InlineKeyboardMarkup:
    '''адаптиваня клавиатура  показывающая клаву с достопримечательностями для их выбора в связь'''
    try:
        if not all_lm_lst:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="пока что нет тдостопримечательностей, вернитесь назад", callback_data="admin_interactive_menu")]])
        all_lm_kb = InlineKeyboardBuilder()
        for lm in all_lm_lst:
            all_lm_kb.add(InlineKeyboardButton(text = f"{lm.name}", callback_data=f"add_bound_lm_{lm.id}"))
        all_lm_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
        return all_lm_kb.adjust(4).as_markup()
    except Exception as err:
        logger.error(f"Ошибка при формировании inline клавы всех достопримечательностей: {err}")
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="admin_interactive_menu")]])
    

def bound_tour_kb(bound_tour_id:int, bound_lm_id:int):
    '''формирует клаву для отображения и изменения тура из выбранной связи в ассоциативной таблице'''
    return  InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Изменить данный объект в связке', callback_data="change_bound_tour")],
                                                  [InlineKeyboardButton(text='Назад', callback_data=f"current_bound_{bound_tour_id}_{bound_lm_id}")]])
    
    
def bound_lm_kb(bound_tour_id:int, bound_lm_id:int):
    '''формирует клаву для отображения и изменения landmark из выбранной связи в ассоциативной таблице'''
    return  InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Изменить данный объект в связке', callback_data="change_bound_lm")],
                                                  [InlineKeyboardButton(text='Назад', callback_data=f"current_bound_{bound_tour_id}_{bound_lm_id}")]])
    