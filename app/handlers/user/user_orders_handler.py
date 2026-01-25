from aiogram import F, Router

from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from app.filters.chat_group_filters import GroupFilter
from app.filters.admin_filters import AdminFilter
#KB
from app.keyboards.user_kb.inline_keyboards import set_payment_type_kb, successful_order_kb, all_user_orders_kb, current_order_kb
from app.keyboards.base_keyboards import create_inline_kb
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.FSM.user_states.states import  NewOrder
from aiogram.filters import StateFilter, or_f
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from dotenv import load_dotenv

# DB
from app.database import db_managers
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_queries import  get_current_tour_query, get_current_user_query, can_book_query, calculate_total_price_query, get_user_orders_query, get_current_order_query, show_order_detailed_info_query, cancel_order_query# слой абстракции для менеджера БД(маленькая связанность)
from app.database.all_models.models import OrderStatus
logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env



user_order_handler = Router()
# user_main_handler.message.filter(GroupFilter(['private']))

@user_order_handler.callback_query(F.data.startswith("buy_tour"))
async def buy_current_tour(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''при нажатии кнопку купить  тур активируется fsm режим покупки тура с указанием мест, типом платежа и прочее'''
    await callback.message.delete()
    current_tour_id = int(callback.data.split('_')[-1])
    await state.update_data(tour_id=current_tour_id)
    await state.set_state(NewOrder.select_place_quantity)
    await callback.message.answer("Укажите пожалуйста, сколько мест вы желаете приобрести")
    
@user_order_handler.message(lambda msg:msg.text.isdigit() and int(msg.text)>0 , StateFilter(NewOrder.select_place_quantity))
async def get_places_quantity(message: Message, state:FSMContext, session:AsyncSession):
    order_data = await state.get_data()
    current_tour_id = order_data.get('tour_id')
    user_booked_seats = int(message.text)# количество мест указанное зером для броинрования
    # current_tour = await get_current_tour_query(session, current_tour_id)
    booking_probability = await can_book_query(session,current_tour_id,user_booked_seats)# если tuple вернет, значит False и сообщение об оошибке иначе True
    if isinstance(booking_probability,tuple):# не получилось по указанной в tuple причине заказть user_booked_seats мест
        await message.answer(booking_probability[-1])
    else:
        total_price_for_user = await calculate_total_price_query(session, current_tour_id, user_booked_seats) # стоимость одного места в туер на указанное количество мест
        await state.update_data(total_price = total_price_for_user) # Общая стоимость
        await state.update_data(quantity = user_booked_seats)# количество мест
        await state.set_state(NewOrder.payment_type)
        await message.answer("отлично, теперь выберите форму оплаты заказа", reply_markup=set_payment_type_kb())
        
@user_order_handler.message(StateFilter(NewOrder.select_place_quantity))
async def wrong_places_quantity(message: Message):
    '''если вместо количества мест ввел ишляпу какую то'''
    await message.answer("Введите числовое значение мест, которые хотите забронировать")
        
        
@user_order_handler.callback_query(F.data == "order_payment_cash", StateFilter(NewOrder.payment_type))
async def set_order_with_cash(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''если юзер выбрал наличку в качестве оплаты'''
    logger.warning(f"tg_id юзера {callback.from_user.id}!!!")
    order_data = await state.get_data()
    tour_id = order_data.get('tour_id') # для формирования клавиатур
    await state.update_data(payment_type='cash')
    order_db_manager = db_managers.OrderManager()
    await state.set_state(NewOrder.waiting)
    current_user = await get_current_user_query(session, telegram_id = callback.from_user.id) # не callback.message.from_user !!!
    if not current_user:
        await callback.message.answer("Вас еще нет в базе, пожалуйста зарегестрируйтесь перед тем как делать заказ!")
        return
        # Нужно!!! сделать клавиатуру, возвращающую к этапу регистрации(заменить команду start, на высплывающую пи заходе в чат  инлайн кнопку start, и перенести юзера туда)
    await state.update_data(user_id=current_user.id)
    await state.update_data(payment_id = order_db_manager.set_order_payment_id()) # уникальный id заказа
    # берем уже обновленные данные
    order_data = await state.get_data()
    order_result = await order_db_manager.create(session, order_data) # создание заказа
    if order_result:
        current_tour = await get_current_tour_query(session, tour_id)
        current_tour.booked_seats = order_data['quantity']# изменение забронированных мест в туре
        await session.commit()
        final_kb = successful_order_kb(tour_id=tour_id, order_id=order_result.id)
        await callback.message.answer("Ваши места упешно забронированы в туре", 
                                      reply_markup= final_kb)# сделать потом подробную инфу о времени и месте встречи
        await state.clear()# не забывает очищать state
    else:
        await state.clear()# не забывает очищать state
        back_to_tour = create_inline_kb([{'text':'назад к туру', 'callback_data':f"show_tour_{tour_id}"}])
        await callback.message.answer("Произошла ошибка при формировании заказа, пожалуйста повторите еще раз", reply_markup = back_to_tour)
        
@user_order_handler.callback_query(F.data == "show_user_orders")
async def show_user_orders(callback: CallbackQuery, session:AsyncSession):
    await callback.message.delete()
    user_telegram_id = callback.from_user.id
    user_orders_result = await get_user_orders_query(session,telegram_id=user_telegram_id)
    if not user_orders_result: 
        await callback.message.answer("У вам пока нет заазов либо вы не зарегестрированы в системе", reply_markup= all_user_orders_kb())
    else:
        await callback.message.answer("Вот список твоих заказов", reply_markup=all_user_orders_kb(user_orders_result))
        
    
    
@user_order_handler.callback_query(F.data.startswith("current_order_info_"))
async def show_current_order(callback: CallbackQuery, session:AsyncSession):
    await callback.message.delete()
    current_order_id = int(callback.data.split('_')[-1])
    user_order = await get_current_order_query(session, current_order_id)
    back_to_orders_kb = create_inline_kb([{'text':'Вернуться к заказам','callback_data':'show_user_orders'},
                                          {'text':'Главное меню', 'callback_data':"user_main_menu"}],row_width=2)
    if not user_order: 
        await callback.message.answer("Нет инфы по данному заказу", reply_markup= back_to_orders_kb)
    else:
        if user_order.status == OrderStatus.CANCELLED:
            logger.warning("Не выыводим юзеру инфу об уже отмененном заказе")
            await callback.message.answer("Данный заказ был отменен, перезакажите его еще раз", show_alert=True, reply_markup=back_to_orders_kb)
            return
        current_order_info = await show_order_detailed_info_query(session,current_id=current_order_id, skip_fields=['id','user_id','tour_id','payment_id'])
        await callback.message.answer(current_order_info , reply_markup=current_order_kb(user_order))
        
    
@user_order_handler.callback_query(F.data.startswith("cancel_order"))
async def cancel_current_order(callback: CallbackQuery, session:AsyncSession):
    
    await callback.message.delete()
    current_order_id = int(callback.data.split('_')[-1])
    cancel_result = await cancel_order_query(session, current_order_id)
    back_to_orders_kb = create_inline_kb([{'text':'к заказам', 'callback_data':"show_user_orders"}])
    if cancel_result:
        await callback.message.answer("Ваш заказ успешно отменен", reply_markup= back_to_orders_kb)
        await session.commit() # сохраняем отмененный заказ
    else:
        await callback.message.answer("Произошла ошибка при отмене заказа, повторите позже", reply_markup=back_to_orders_kb) 
    
    
        