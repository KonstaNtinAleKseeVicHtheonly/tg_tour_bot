from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from project_logger.loger_configuration import setup_logging
from app.database.all_models.models import Order, OrderStatus



logger = setup_logging()



def set_payment_type_kb():
    '''создает Inline клаву с типам оплаты'''
    payment_type_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'по карте', callback_data="order_payment_card"),
                                                            InlineKeyboardButton(text = 'Наличными', callback_data="order_payment_cash"),
                                                            InlineKeyboardButton(text = 'переводом', callback_data="order_payment_transfering")],
                                                            [InlineKeyboardButton(text = 'Внутренней валютой tg_stars', callback_data="order_payment_tgstars")]
                                                            ])
    return payment_type_kb
    

def tg_star_payment_kb(tour_id:int):
    '''клава с подтверждением покупки заказа через tg_starts'''
    payment_type_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Оплатить', pay=True),
                                                            InlineKeyboardButton(text = 'Отмена', callback_data=f"show_tour_{tour_id}")]
                                                            ])
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
        if order.status == OrderStatus.CANCELLED:
            all_orders_kb.add(InlineKeyboardButton(text = f"Отмененный {order.tour.name}", callback_data=f"current_order_info_{order.id}"))
        elif order.status == OrderStatus.PENDING:
            all_orders_kb.add(InlineKeyboardButton(text = f"Неподтвержденный {order.tour.name}", callback_data=f"current_order_info_{order.id}"))
        elif order.status == OrderStatus.COMPLETED:
            all_orders_kb.add(InlineKeyboardButton(text = f"Завершенный {order.tour.name}", callback_data=f"current_order_info_{order.id}"))
        elif order.status == OrderStatus.CONFIRMED:
            all_orders_kb.add(InlineKeyboardButton(text = f"Оплаченный {order.tour.name}", callback_data=f"current_order_info_{order.id}"))   
    all_orders_kb.row(InlineKeyboardButton(text='назад',callback_data="user_main_menu"))
    return all_orders_kb.adjust(2).as_markup()

def current_order_kb(current_order:Order):
    if current_order.status == 'pending':# пока заказ не оплчаен его ещ можно отменить
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data="user_main_menu")],
                                                     [InlineKeyboardButton(text = 'Отменить', callback_data=f"cancel_order_{current_order.id}")],
                                                     [InlineKeyboardButton(text = 'Изменить количество мест', callback_data=f"change_order_places_{current_order.id}")],
                                                     ])
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data="user_main_menu")]])

