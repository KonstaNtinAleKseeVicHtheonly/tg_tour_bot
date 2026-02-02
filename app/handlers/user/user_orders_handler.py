from aiogram import F, Router

from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram.enums import ChatAction
# фитры 
from app.filters.chat_group_filters import GroupFilter
from app.filters.admin_filters import AdminFilter
#KB
from app.keyboards.user_kb.inline_keyboards import set_payment_type_kb, successful_order_kb, all_user_orders_kb, current_order_kb, tg_star_payment_kb
from app.keyboards.base_keyboards import create_inline_kb
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.FSM.user_states.states import  NewOrder
from aiogram.filters import StateFilter, or_f
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from dotenv import load_dotenv
import os
# DB
from app.database import db_managers
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_queries import get_current_banner_query, get_current_tour_query, get_current_user_query, can_book_query, calculate_total_price_query, get_user_orders_query, get_current_order_query, show_order_detailed_info_query, cancel_order_query, update_order_query, create_new_order_query# слой абстракции для менеджера БД(маленькая связанность)
from app.database.all_models.models import OrderStatus
# оплата заказа и дейтсвия при транзакциях
from aiogram.types import LabeledPrice
from app.utils.managers.transaction_manager import OrderPaymentManager # общий класс для расчета при соверешинии операций и прочее

logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env





user_order_handler = Router()
user_order_handler.message.filter(GroupFilter(['private']))

@user_order_handler.callback_query(F.data.startswith("buy_tour"))
async def buy_current_tour(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''при нажатии кнопку купить  тур активируется fsm режим покупки тура с указанием мест, типом платежа и прочее'''
    await callback.message.delete()
    current_tour_id = int(callback.data.split('_')[-1])
    current_tour = await get_current_tour_query(session, current_tour_id)
    await state.update_data(tour_id=current_tour_id)
    await state.set_state(NewOrder.select_place_quantity)
    await callback.message.answer(f"Укажите пожалуйста, сколько мест вы желаете приобрести.\n Всего доступно {current_tour.max_people - current_tour.booked_seats}")
    
@user_order_handler.message(lambda msg:msg.text and msg.text.isdigit() and int(msg.text)>0 , StateFilter(NewOrder.select_place_quantity))
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
        
        
# варианты оплаты

@user_order_handler.callback_query(F.data.startswith("order_payment"), StateFilter(NewOrder.payment_type))
async def set_order_with_cash(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''юезр выбирает варианты оплаты'''
    await callback.message.delete()
    current_payment_type = callback.data.split('_')[-1]
    transaction_manager = OrderPaymentManager()
    order_data = await state.get_data()
    tour_id = order_data.get('tour_id')
    current_user = await get_current_user_query(session, telegram_id = callback.from_user.id) # не callback.message.from_user !!!
    if not current_user:
        await callback.message.answer("Вас еще нет в базе, пожалуйста зарегестрируйтесь перед тем как делать заказ!")
        return
    await state.update_data(user_id = current_user.id)# сохрним id юзера для дальнейшеей передачи при фомрировании заказа
    await state.update_data(payment_type=current_payment_type)# сохранем тип платежа для определяни дальнейше логики заверешняи оплаты
    if current_payment_type == 'tgstars': # если оплата через внутреннюю валюту tg 
        stars_price = transaction_manager.calculate_tg_star_price(order_data.get('total_price')) # по цене в рублях за тур у заказчика расчитываем цену в звездах
        await callback.message.answer_invoice(
            title='Оплатить телеграм звездами',
            description='Внутрення валюта телеграм',
            prices = stars_price, # расчитать формулу и сделать методв order_db_manager
            provider_token='',
            payload='by stars',
            currency='XTR',
            reply_markup=tg_star_payment_kb(tour_id))
    elif current_payment_type == 'card':# если юзер выбрал при оплате через master_pay
        rub_price = transaction_manager.calculate_rub_price(order_data.get('total_price')) # по цене в рублях за тур у заказчика расчитываем цену в звездах
        await callback.message.answer_invoice(
            title='Оплатить банковской картой',
            description='Оплата через pay систему',
            payload='order_payload',# служебная инфа передается для проведения платежа
            provider_token=os.getenv("PAY_MASTER_TOKEN"),
            currency='RUB',  
            prices = rub_price,# расчитать формулу и сделать методв order_db_manager
            start_parameter='pay_order', # параметр для идентификации платежа юзером
            reply_markup=tg_star_payment_kb(tour_id)) 
    else: # у налички и перевода по карте сразу логика бронирования
        order_db_manager = db_managers.OrderManager()
        await state.set_state(NewOrder.waiting)
        await state.update_data(payment_id = order_db_manager.set_order_payment_id()) # уникальный id заказа
        # берем уже обновленные данные
        order_data = await state.get_data()
        order_result = await order_db_manager.create(session, order_data) # создание заказа, если все норм то вернет созданный заказ
        if order_result:
            await transaction_manager._accomplish_successful_transaction(session, order_result, order_data) # В БД меняем общее количество мест в туре, статус заказа о юзера
            await session.commit()
            final_kb = successful_order_kb(tour_id=tour_id, order_id=order_result.id)
            purchase_banner = await get_current_banner_query(session, banner_name="purchase_banner")
            await state.clear()# не забывает очищать state
            if current_payment_type == 'cash':
                await callback.message.answer_photo(photo = purchase_banner.image,caption = "Ваш заказ забронирован, оплатите при встрече с Гидом", 
                                                reply_markup = final_kb)
            elif current_payment_type == 'transfering':
                await callback.message.answer_photo(photo = purchase_banner.image,caption = "При успешном переводе денежных средств вам отправится идентификационный id, который нужно показать при встрече", 
                                                reply_markup = final_kb)
        else: # ошибка при фомрировании заказа
            await state.clear()# не забывает очищать state
            back_to_tour = create_inline_kb([{'text':'назад к туру', 'callback_data':f"show_tour_{tour_id}"}])
            await callback.message.answer("Произошла ошибка при формировании заказа, пожалуйста повторите еще раз", reply_markup = back_to_tour)
         
        
@user_order_handler.pre_checkout_query()
async def pre_checkout_process(pre_checkout_query:PreCheckoutQuery, state:FSMContext):
    '''проверка платежа на успешность'''
    await pre_checkout_query.answer(ok=True)
    

@user_order_handler.message(F.successful_payment)
async def successful_payment_process(message:Message,state:FSMContext, session:AsyncSession):
    '''действия при успешной оплате юзера тура через tg_stars'''
    await message.delete()
    order_data = await state.get_data()
    transaction_manager = OrderPaymentManager()
    current_payment_id = message.successful_payment.telegram_payment_charge_id # уникальный id транзакции
    order_data = await state.get_data()
    tour_id = order_data.get('tour_id') # для формирования клавиатур
    await state.set_state(NewOrder.waiting)
    current_user = await get_current_user_query(session, telegram_id = message.from_user.id) # не callback.message.from_user !!!
    if not current_user:
        await message.answer("Вас еще нет в базе, пожалуйста зарегестрируйтесь перед тем как делать заказ!")
        return
    await state.update_data(user_id=current_user.id)
    await state.update_data(payment_id = current_payment_id) # уникальный id заказа
    await state.update_data(status=OrderStatus.CONFIRMED) # тестовая установка статуса, потом убрать
    # берем уже обновленные данные
    order_data = await state.get_data()
    order_result = await create_new_order_query(session, order_data) # создание заказа, если все норм то вернет созданный заказ
    if order_result:
        await transaction_manager._accomplish_successful_transaction(session, order_result, order_data) # при создании заказа все необходимые изменения в БД
        await session.commit()
        final_kb = successful_order_kb(tour_id=tour_id, order_id=order_result.id)
        purchase_banner = await get_current_banner_query(session, banner_name="purchase_banner")
        await message.answer_photo(photo = purchase_banner.image,caption = "Ваш заказ успешно оплачен, о месте и начале тура ознакомьтесь в информации о туре", 
                                            reply_markup = final_kb)
        await message.answer(f"Пожалуйста при начале экскурсии не забудьте предьявить свой номер транзакции для подтверждения оплаты:\n{current_payment_id}")
        await state.clear()# не забывает очищать state
    else: # ошибка при фомрировании заказа
        await state.clear()# не забывает очищать state
        back_to_tour = create_inline_kb([{'text':'назад к туру', 'callback_data':f"show_tour_{tour_id}"}])
        await message.answer("Произошла ошибка при формировании заказа, пожалуйста повторите еще раз", reply_markup = back_to_tour)

    

    
@user_order_handler.callback_query(F.data == "show_user_orders")
async def show_user_orders(callback: CallbackQuery, session:AsyncSession):
    '''покажет юзеру все его теущее заказаы'''
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
        current_order_info = await show_order_detailed_info_query(session,current_order_id=current_order_id, skip_fields=['id','user_id','tour_id'])
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
    
    
@user_order_handler.callback_query(F.data.startswith("change_order_places"))
async def change_current_order_places(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    current_order_id = int(callback.data.split('_')[-1])
    current_order = await get_current_order_query(session,current_order_id)
    # обработка случаем когда заказ выолнен или отменен
    if current_order:
        if current_order.status != OrderStatus.PENDING:# только количестов мест в неоплаченном заказе можно изменить!!!
            await callback.message.answer("К сожалению можно изменить только неоплаченный заказ")
        else:
            await state.set_state(NewOrder.change_places)
            # изменение мест в текущем заказе и его туре
            current_tour = await get_current_tour_query(session, current_order.tour_id)#ищем тур по заказу
            current_tour.booked_seats -= current_order.quantity # меняем количество занятых мест в туре
            current_order.quantity = 1 # по умолчанию не может быть < 1
            await session.commit()
            # await session.refresh(current_order)
            # await session.refresh(current_tour)
            await state.update_data(order_id=current_order_id)# сохраним id тура и заказа в state для последующего изменения
            await state.update_data(tour_id=current_tour.id)
            await callback.message.answer("Введите новое количество мест для тура")
    else:
        await callback.message.answer("По данному заказу отсутсвует информация")
        
        
@user_order_handler.message(lambda msg:msg.text and msg.text.isdigit() and int(msg.text)>0, StateFilter(NewOrder.change_places))
async def complete_places_changing(message: Message, state:FSMContext, session:AsyncSession):
    '''если юзер указал числовое значение'''
    order_data = await state.get_data()
    current_order_id = order_data.get('order_id')
    current_tour_id = order_data.get('tour_id')
    current_order = await get_current_order_query(session,order_id=current_order_id)
    current_tour = await get_current_tour_query(session, tour_id=current_tour_id)
    new_place_quantity = int(message.text)  # новое количество мест от юзера 
    # проверка сможет ли юзер столько мест занять
    #(-1 т.к по умолчанию уже одно стояло при обнулении старых мест заказа)
    booking_probability = await can_book_query(session,current_order.tour_id,new_place_quantity-1)# если tuple вернет, значит False и сообщение об оошибке иначе True
    if isinstance(booking_probability,tuple):# не получилось по указанной в tuple причине заказть user_booked_seats мест
        await message.answer(booking_probability[-1])
    else:
        # расчет новой цены в зависимости от указанных мест
        new_total_price_for_user = await calculate_total_price_query(session, current_order.tour_id, new_place_quantity) # стоимость одного места в туер на указанное количество мест
        updated_result = await update_order_query(session, {'id':current_order.id}, {'quantity':new_place_quantity,'total_price':new_total_price_for_user})# обновление имеющихся даных
        await state.clear()
        if updated_result:
            current_tour.booked_seats += new_place_quantity # в туре поменяю общее количество мест
            await session.commit()
            await message.answer(f'Количество мест успешно изменено на {new_place_quantity}', reply_markup=successful_order_kb(current_tour_id, current_order_id))
        else:
            await session.rollback()
            await message.answer('Ошибка при изменении мест в заказе повторите позже')

@user_order_handler.message(StateFilter(NewOrder.change_places))
async def wrong_places_changing(message: Message):
    '''если вместо количества мест ввел ишляпу какую то'''
    await message.answer("Введите числовое значение мест, которые хотите забронировать")
        