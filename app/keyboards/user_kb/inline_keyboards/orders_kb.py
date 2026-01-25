from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_managers
from app.database.all_models.models import Order



logger = setup_logging()



def set_payment_type_kb():
    '''создает Inline клаву с типам оплаты'''
    payment_type_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'по карте', callback_data="order_payment_card"),
                                                             InlineKeyboardButton(text = 'Наличными', callback_data="order_payment_cash")],
                                                            [InlineKeyboardButton(text = 'переводом', callback_data="order_payment_transaction")]])
    return payment_type_kb
    

def successful_order_kb(tour_id:int , order_id:int):
    '''в случае успешного фомрирования заказа будет кнопка с подробная инфой о купленном туре
    , возврат к своим заказам и возврат в главное меню(или к турам)'''
    order_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Подробная инфаормация о туре', callback_data=f"detailed_info_tour_{tour_id}")],
                                                            [InlineKeyboardButton(text = 'Отменить заказ', callback_data=f"cancel_order_{order_id}")],
                                                            [InlineKeyboardButton(text = 'На главную', callback_data="user_main_menu")],
                                                            [InlineKeyboardButton(text = 'К заказам', callback_data="show_user_orders")]])
    return order_kb

def all_user_orders_kb(all_orders:list[Order]=None):
    '''из списка заказлов делает инлайн клавиатуру с инфой о них, возможностью отменить их
    если  они есть, либо возращает клаву с кнокой возвращения назад'''
    
    # try:
    if not all_orders: # значит что нет заказов у текущего юзера
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data="user_main_menu")]])
    all_orders_kb = InlineKeyboardBuilder()
    for order in all_orders:
        all_orders_kb.add(InlineKeyboardButton(text = f"Заказ {order.tour.name}", callback_data=f"current_order_info_{order.id}"))
    all_orders_kb.row(InlineKeyboardButton(text='назад',callback_data="user_main_menu"))
    return all_orders_kb.adjust(2).as_markup()

def current_order_kb(current_order:Order):
    if current_order.status == 'pending':# пока заказ не оплчаен его ещ можно отменить
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data="user_main_menu")],
                                                     [InlineKeyboardButton(text = 'Отменить', callback_data=f"cancel_order_{current_order.id}")]])
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data="user_main_menu")]])


# def current_order_kb(current_order:Order=None):
#     '''Выводит детальную инфу о заказе либо выводит кнопку вернуть к заказам'''
    
#     # try:
#     if not current_order: # значит что нет заказов у текущего юзера
#         return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'К заказам', callback_data="user_main_menu"),InlineKeyboardButton(text = 'Главное меню', callback_data="user_main_menu")]])
#     all_orders_kb = InlineKeyboardBuilder()
#     for order in all_orders:
#         all_orders_kb.add(InlineKeyboardButton(text = f"Заказ {order.tour.name}", callback_data=f"current_order_info_{order.id}"))
#     all_orders_kb.row(InlineKeyboardButton(text='назад',callback_data="user_main_menu"))
#     return all_orders_kb.adjust(2).as_markup()
    # except Exception as err:
    #     logger.error(f"Ошибка при формировании inline клавы всех заказов: {err}")
    #     return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'произошла ошибка, вернутся назад', callback_data="user_main_menu")]])
    
# сделать клаву для каждого отдельного заказа с возможностью его отмены

