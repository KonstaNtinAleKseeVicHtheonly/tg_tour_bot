from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter
#KB

from app.keyboards.admin_kb.inline_keyboards import all_orders_kb, user_current_order_kb
from app.keyboards.base_keyboards import create_inline_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import AdminOrderMode
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database import db_managers
from app.database.all_models.models import  OrderStatus
from app.database.db_queries import show_all_orders_query, get_current_order_query, update_order_query, get_current_user_query
from sqlalchemy.ext.asyncio import AsyncSession
#утилиты

#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_orders_handler = Router()
admin_orders_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами


@admin_orders_handler.message(StateFilter(AdminOrderMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
logger.info("Прошли в хэндлеры заказов админа")





@admin_orders_handler.callback_query(F.data=='check_orders_expiration')
async def check_orders_expiration(callback: CallbackQuery, session : AsyncSession):
    '''все заказаы берет со статусо CANCELLED и проверяеи на срок годности согласно expiration_limitm если такие есть,
    ту удаляем их'''
    order_db_manager = db_managers.OrderManager()
    all_cancelled_orders = await order_db_manager._find_info_by_params(session, status=OrderStatus.CANCELLED)
    process_result = await order_db_manager._delete_expired_orders(session,all_cancelled_orders, expiration_limit=5)
    if process_result is None:
        await callback.message.answer("Ошибка в процессе удаления просроченных товаров, чекай логи")
    else:
        if process_result[0]: # при успешной опреации вернется tuple(True,кол-во удлаенных заказов)
            await session.commit()
            await callback.message.answer(f"{process_result[-1]} заказа(ов) с истекшим сроком годности успешно удалены")
        else:# если не было просроченных заказов вернет tuple(False, 'не было просроченных заказов')
            await callback.message.answer(f"{process_result[-1]}")
            

@admin_orders_handler.callback_query(F.data=='show_all_orders_admin')
async def show_all_users(callback: CallbackQuery, session : AsyncSession):
    all_orders = await show_all_orders_query(session)
    if not all_orders:
        callback.message.answer("НЕт заказов в  бд чекни логи")
    else:
        await callback.message.answer("Вот список всех заказов", reply_markup = all_orders_kb(all_orders) ) # выведет список всех пользователей



@admin_orders_handler.callback_query(F.data.startswith("admin_user_orders"))
async def show_user_orders(callback: CallbackQuery, session : AsyncSession):
    '''выведет все заказы указанного юзера(по id юзера)'''
    current_user_id = int(callback.data.split('_')[-1])
    order_db_manager = db_managers.OrderManager()
    user_orders = await order_db_manager._find_info_by_params(session, user_id=current_user_id)
    if user_orders:
        await callback.message.answer(f"Вот заказы юзера с id {current_user_id}", reply_markup=all_orders_kb(user_orders))
    else:
        await callback.message.answer(f"У юзера с id {current_user_id} не найдено заказов, чекай логи")
    
    
    
@admin_orders_handler.callback_query(F.data.startswith("user_current_order"))
async def show_curent_users(callback: CallbackQuery, session : AsyncSession):
    current_order_id = int(callback.data.split('_')[-1])
    order_db_manager = db_managers.OrderManager()
    current_order = await order_db_manager.get(session, id=current_order_id)# текущей юзер
    if not current_order:
        await callback.message.answer(f"Заказ с id {current_order_id} не найден в базе")
    else:
        user_info_text = await order_db_manager.show_detailed_info_for_user(session, current_order_id) # развернутая текстовая инфа о заказе
        await callback.message.answer(user_info_text, reply_markup=user_current_order_kb(current_order))
    
@admin_orders_handler.callback_query(F.data.startswith("confirm_user_order"))
async def ask_to_confirm_curent_order(callback: CallbackQuery,  session : AsyncSession):
    '''Запрос подтверждение неоплаченного заказа с отправкой владельцу по его tg_ig id оплаты'''
    order_id = int(callback.data.split('_')[-1])
    confirm_kb = create_inline_kb([{'text':'ДА,подтвердить', 'callback_data':f"yes_confirm_order_{order_id}"},
                                   {'text':'Отмена', 'callback_data' : f'user_current_order_{order_id}'}])
    await callback.message.answer(f"Вы действительно хотите подвтердить неополаченный заказ с id {order_id}?", reply_markup=confirm_kb)

@admin_orders_handler.callback_query(F.data.startswith("yes_confirm_order"))
async def confirm_curent_order(callback: CallbackQuery, bot:Bot,  session : AsyncSession):
    '''в Случае согласия на подвтерждение неоплаченного заказа'''
    order_id = int(callback.data.split('_')[-1])
    current_order = await get_current_order_query(session, order_id)
    order_user_id = current_order.user_id
    current_user = await get_current_user_query(session, id=order_user_id)
    if not current_user:
        await callback.message.answer(f"Не смогли найти id владельца заказа {order_id}, проверьте базу данных")
        return
    logger.info(f"Нашли владельца заказа {order_id} в базе - user_id {current_user.id}, подтверждаем заказ и отправляем владельцу id транзакции")
    current_user_tg_id = current_user.telegram_id
    payment_id = current_order.payment_id
    current_order.status = OrderStatus.CONFIRMED
    await session.commit() # подвтерждаем сохранение
    back_to_orders_kb = create_inline_kb([{'text':'назад к заказам', 'callback_data':'show_all_orders_admin'}])
    await bot.send_message(chat_id=current_user_tg_id, text=f'''Ваш заказ был подвтержден.Вот ваш уникальный id оплаты : {payment_id}\n
                           Сохраните себе и покажите Гиду при отправке в путешествие в качестве подтвержения оплаты.Удачной поездки''')
    await callback.message.answer(f"Юзеру {current_user.username} был отправлен его id оплаты а статус заказа изменен на CONFIRMED", reply_markup=back_to_orders_kb)

@admin_orders_handler.callback_query(F.data.startswith("user_order_delete"))
async def delete_curent_order(callback: CallbackQuery, session : AsyncSession):
    '''удаление выбранного заказа по id'''
    current_order_id = int(callback.data.split('_')[-1])
    order_db_manager = db_managers.OrderManager()
    delete_result = await order_db_manager.delete(session, current_order_id)
    if delete_result:
        back_to_menu = create_inline_kb([{'text':'Назад', 'callback_data':'admin_interactive_menu'}])
        await session.commit()
        await callback.message.answer(f"Заказ с id {current_order_id} умпешно удален их базы данных",reply_markup=back_to_menu)
    else:
        current_order = await get_current_order_query(session,current_order_id )
        await callback.message.answer(f"Ошибка при удалении заказа с id {current_order_id}, чекая логи", reply_markup=user_current_order_kb(current_order))
        
@admin_orders_handler.callback_query(F.data.startswith("change_user_order_"))
async def change_curent_order(callback: CallbackQuery, state:FSMContext, session : AsyncSession):
    '''по id заказа меняем выбранные поля через FSM'''
    current_order_id = int(callback.data.split('_')[-1])
    await state.update_data(order_id = current_order_id)
    await state.set_state(AdminOrderMode.edit_choose_field)
    order_db_manager = db_managers.OrderManager()
    table_columns_lst = order_db_manager.show_model_columns_lst()
    await callback.message.answer(f"Укажите поле для изменения из текущих:\n{'\n'.join(table_columns_lst)}")
    
@admin_orders_handler.message(F.text.isalpha(), StateFilter(AdminOrderMode.edit_choose_field))
async def check_field_validation_and_complete(message:Message, state:FSMContext):
    order_db_manager = db_managers.OrderManager()
    table_columns_lst = order_db_manager.show_model_columns_lst()
    if  F.text not in table_columns_lst:
        await message.answer(f"ВВеди поля из указанного списка:{'\n'.join(table_columns_lst)}")
    else:
        await state.update_data(changing_field=message.text)
        await state.set_state(AdminOrderMode.edit_new_value)
        await message.answer("Отлично, теперь введите н=значение на которое нужно поменять указанный столбец")
        
@admin_orders_handler.message(StateFilter(AdminOrderMode.edit_choose_field))
async def wrong_field_validation_and_complete(message:Message):
    await message.answer("Введиет поле из указанного списка!!!")
    
@admin_orders_handler.message(StateFilter(AdminOrderMode.edit_new_value))
async def choose_new_value(message:Message, state:FSMContext, session:AsyncSession):
    '''под выбранный столбец вводим новое значение'''
    new_value = message.text
    data_for_update = await state.get_data() # получаем инфу что бы найти заказ и изменить его
    changing_field = data_for_update.get('changing_field')
    order_id = data_for_update.get('order_id')
    update_result = await update_order_query(session,data_to_find_object={'id':order_id},
                                             data_to_update_object={changing_field:new_value})
    current_order = await get_current_order_query(session, order_id)
    if update_result:
        await session.commit()
        await message.answer(f"поле {changing_field} успешно изменено на {new_value}",reply_markup=user_current_order_kb(current_order))
    else:
        await message.answer("ПРоизошла ошибка при изменении параметров, чекйа логи", reply_markup=user_current_order_kb(current_order)) 
        
        
