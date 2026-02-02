from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from app.database.all_models.models import Order, OrderStatus



logger = setup_logging()




def all_orders_kb(all_orders:list[Order]):
    '''по запросу из БД показывает в кнопках все заказы юзера'''
    # try:
    if not all_orders: # значит что нет заказов у текущего юзера
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data="show_all_orders_admin")]])
    all_orders_kb = InlineKeyboardBuilder()
    for order in all_orders:
        if order.status == OrderStatus.CANCELLED:
            all_orders_kb.add(InlineKeyboardButton(text = f"Отмененный заказ {order.id}", callback_data=f"user_current_order_{order.id}"))
        elif order.status == OrderStatus.COMPLETED:
            all_orders_kb.add(InlineKeyboardButton(text = f"Завершенный заказ {order.id}", callback_data=f"user_current_order_{order.id}"))
            OrderStatus
        elif order.status == OrderStatus.PENDING:
            all_orders_kb.add(InlineKeyboardButton(text = f"Неоплаченный заказ {order.id}", callback_data=f"user_current_order_{order.id}"))
        elif order.status == OrderStatus.CONFIRMED:
            all_orders_kb.add(InlineKeyboardButton(text = f"Оплаченный заказ {order.id}", callback_data=f"user_current_order_{order.id}")) 
    all_orders_kb.row(InlineKeyboardButton(text='назад',callback_data="admin_interactive_menu"))
    return all_orders_kb.adjust(2).as_markup()


# def user_orders_kb(user_orders:list[Order]):
#     '''клаву создает для'''

    
def user_current_order_kb(order_obj:int):
    '''Формирует клаву вависимости от заказа с возможностью потдвердить неполаченные'''
    if order_obj.status == OrderStatus.PENDING: # с возможностью подвердить неоплаченный заказ для админа
        current_user_kb = InlineKeyboardMarkup(inline_keyboard=[
                                                                [InlineKeyboardButton(text = 'удалить', callback_data=f"user_order_delete_{order_obj.id}")],
                                                                [InlineKeyboardButton(text = 'изменить', callback_data=f"change_user_order_{order_obj.id}")],
                                                                [InlineKeyboardButton(text = 'Подтвердить', callback_data=f"confirm_user_order_{order_obj.id}")],
                                                                [InlineKeyboardButton(text = 'назад', callback_data="show_all_orders_admin")]
                                                                
                                                                ])
    else:
        current_user_kb = InlineKeyboardMarkup(inline_keyboard=[
                                                                [InlineKeyboardButton(text = 'удалить', callback_data=f"user_order_delete_{order_obj.id}")],
                                                                [InlineKeyboardButton(text = 'изменить', callback_data=f"change_user_order_{order_obj.id}")],
                                                                [InlineKeyboardButton(text = 'назад', callback_data="show_all_orders_admin")]
                                                                ])
    return current_user_kb
    
