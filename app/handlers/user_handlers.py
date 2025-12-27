from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from aiogram.filters import CommandStart, Command
from app.filters.chat_group_filters import GroupFilter
#KB
from app.keyboards.reply_kb import reply_main_menu, delete_reply_kb, reply_request_kb
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, or_f
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from datetime import datetime
import asyncio
import uuid
import os
from dotenv import load_dotenv
# FSM
from aiogram.fsm.context import FSMContext
from app.FSM.states import ChatMode
# колбэки
from aiogram.types import CallbackQuery
# DB


logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env



user_handler = Router()
user_handler.message.filter(GroupFilter(['private']))



@user_handler.message(Command('start'))
async def initial_menu(message : Message, state:FSMContext):
    '''покажет всю инфу о юзере'''
    await state.clear()
    await message.answer(f"Привет {message.from_user.username}")
    await message.answer("<b>Запущен интерактивный режим</b>", reply_markup=reply_main_menu)
    
    
@user_handler.message(or_f(Command('menu'), F.text.lower().in_(['меню','menu','экскурси'])))
async def show_menu(message : Message, state:FSMContext):
    '''покажет всю инфу о юзере'''
    await state.clear()
    await message.answer("Лови актуальное меню")
    
@user_handler.message(Command('show_me'))
async def show_user_info(message : Message, state:FSMContext):
    '''покажет всю инфу о юзере'''
    await state.clear()
    await message.answer("Запущен интерактивный режим", reply_markup=reply_request_kb)

@user_handler.message(Command('about'))
async def common_info(message : Message, state:FSMContext):
    '''покажет всю инфу о юзере'''
    await message.answer("Мы являемся крупным представителем РБ", reply_markup=delete_reply_kb)
    
@user_handler.message(Command('payment'))
async def choose_payment(message : Message):
    '''покажет всю инфу о юзере'''
    await message.answer("Выберите вариант оплаты")
    
@user_handler.message(
    F.text.lower().contains("доставк") |
    F.text.lower().contains("варианты доставки") |
    F.text.lower().contains("способы доставки"))
@user_handler.message(Command('shipping'))
async def choose_shipping(message : Message):
    '''покажет всю инфу о юзере'''
    await message.answer("Выберите вариант доставки")

@user_handler.message(F.text)
async def unpredictable_message(message : Message):
    '''В случае непредвиденного поведения '''
    await message.answer(f"Непредвиденная текстовая команда : {message.text}")
        
 
@user_handler.message(F.photo)
async def unpredictable_img(message : Message):
    '''В случае непредвиденного поведения '''
    await message.answer("Ух ты какая клевая фотка")
        
 

    
#✅
    




# @user_handler.message(F.text)
# async def unpredictable_message(message : Message):
#     '''В случае непредвиденного поведения '''
#     await message.answer(f"Непредвиденная текстовая команда : {message.text}")
        
 
        
        
# @user_handler.message(F.text.isalpha(),F.text.len() > 3, StateFilter('reg_name'))
# async def set_user_name(message: Message, state:FSMContext):
#             await state.update_data(name=message.text.capitalize())
#             await state.set_state('reg_phone_number')    
#             await message.answer("Пожалуйста введите свой  корректный номер телефона", reply_markup = await request_user_contact())
            
# @user_handler.message(StateFilter('reg_name'))
# async def user_wrong_name(message: Message, state:FSMContext):  
#             await message.answer("Пожалуйста введите корректное имя !!!")
    
# @user_handler.message(F.contact, StateFilter('reg_phone_number'))
# async def set_user_phone_contact(message: Message, state:FSMContext):
   
#         await state.update_data(phone_number=message.contact.phone_number)
#         user_data = await state.get_data()
#         registration_result = await update_user(user_tg_id=message.from_user.id , user_data=user_data)
#         if not registration_result:
#             await state.clear()
#             await message("При регистрации произошла ошибка пожалуйста повторите процесс регистрации заново")
#         else:
#             await state.clear()
#             await message.answer("вы успешно зарегистрировались", reply_markup=inline_main_menu)
    
    
# @user_handler.message(F.text, StateFilter('reg_phone_number'))
# async def set_user_phone_text(message: Message, state:FSMContext):
#         if message.text.startswith('+'):
#             user_phone = message.text[1:]
#         else:
#             user_phone = message.text
#         if not user_phone.isdigit():
#             await message.answer("Пожалуйста введите корректный номер телефона")
#             return
#         await state.update_data(phone_number=message.text)
#         user_data = await state.get_data()
#         registration_result = await update_user(user_tg_id=message.from_user.id , user_data=user_data)
#         if not registration_result:
#             await state.clear()
#             await message("При регистрации произошла ошибка пожалуйста повторите процесс регистрации заново")
#         await state.clear()
#         await message.answer("вы успешно зарегистрировались", reply_markup=inline_main_menu)
        
# @user_handler.callback_query(F.data == 'catalogue')
# async def show_catalog(callback: CallbackQuery):
#     '''показывает каталог товарво при нажатии кнопки каталога'''
    
#     await callback.message.delete()
#     await callback.message.answer("Выберите категорию товаров",reply_markup= await get_categories_kb()) # метод создает inline клаву по категоиям из БД
    
# @user_handler.callback_query(F.data.startswith('category_'))
# async def get_category_products(callback: CallbackQuery):
#     '''показывает товары из выбранной категории'''
#     try:
#         category_id = int(callback.data.split('_')[-1])
#         await callback.message.edit_text(
#             "Выберите товар", 
#             reply_markup=await get_cards_kb(category_id)
#         )
#     except TelegramBadRequest:
#         # Если сообщение было с фото/медиа
#         await callback.message.edit_caption(
#             caption="Выберите товар",
#             reply_markup=await get_cards_kb(category_id)
#         )
    
    

# @user_handler.callback_query(F.data.startswith('product_'))
# async def get_current_card_info(callback: CallbackQuery):
#     '''Показывает инфу о выбранно карточке товара'''
#     await callback.message.delete()
#     await callback.message.answer("Хороший выбор, вот инфа о выбранном товаре")
#     current_card_id = int(callback.data.split('_')[-1])
#     current_card_info = await get_card_info(current_card_id)
#     if not current_card_info:
#         await callback.message.answer("По данному товару нет подробной инфы повторите запрос позже")
#         return
#     # await callback.message.delete()
#     if current_card_info.card_image:# на случай если есть картинка картчоки товара
#         logger.info("Вывод ифны о товаре с фоткой")
#         await callback.message.answer_photo(photo=current_card_info.card_image,
#                                             caption=f'''{current_card_info.name}\n
#                                             {current_card_info.description}\n
#                                             {current_card_info.price} РУБ''',
#                                             reply_markup=await product_kb(current_card_info.category_id, current_card_id))                                                                                                                          
#     else:
#         logger.info("Вывод инфы о товаре без фотки")
#         await callback.message.answer(f'''{current_card_info.name}\n\n
#                                             {current_card_info.description}\n\n{current_card_info.price} РУБ''',
#                                             reply_markup= await product_kb(current_card_info.category_id, current_card_info.id))
    
# @user_handler.callback_query(F.data.startswith('buy_'))
# async def buy_product(callback:CallbackQuery, state:FSMContext):
#     '''метод при срабатыващий при покупке определенного товара (принимает buy_card_id)'''
#     logger.info(f"Инфа о callback при покупке товара : {callback.data}")
#     card_id = callback.data.split('_')[-1] # id Товара
#     card_info = await get_card_info(card_id)
#     if not card_info:
#         await callback.message.answer("Нет ифны о товаре")
#         return
#     #сохранение инфы о продукте в состоянме
#     await state.update_data(card_id = card_id)
#     await state.update_data(card_name=card_info.name)
#     await state.update_data(card_price=card_info.price)
#     await state.set_state('address_waiting')
#     await callback.message.answer("Введите ваш адрес доставки", reply_markup=await client_location())# клава с отправкой геолокации


# @user_handler.message(F.location, StateFilter('address_waiting'))
# async def get_user_address_location_var(message: Message, state:FSMContext):
#     '''случай если юзер отправил свою точную геолоакцию используя телеграм'''
#     if not message.location:
#         await message.answer("пожалуйста отправьте вашу текущую геолокацию")
#         return
#     product_data = await state.get_data()
#     location = await get_user_location(message)
#     user_data = await get_user_additional(message.from_user.id)
#     if not user_data:
#         await message.answer("Ошибка при выводе ваших данныех, повторите позже пожалуйста")
#         return
#     full_info = (f"Новый заказ \n"
#                 f"Пользователь {user_data.name}, @{message.from_user.username}, ID:{message.from_user.id}\n"
#                 f"Телефон {user_data.phone_number}\n"
#                 f"Адрес : {location}\n"
#                 f"ID товара : {product_data.get('card_id')}\n"
#                 f"Товар : {product_data.get('card_name')}\n"
#                 f"Цена : {product_data.get('card_price')}\n")
#     order_info = {'user_tg_id' : message.from_user.id,
#                   'address' : location,
#                   'card_id' : product_data.get('card_id')}
#     order_result = await create_order(order_info)
#     if not order_result:
#         await message.answer("Ошиька при создании заказа, потворите еще раз")
#         return    
#     await message.answer(f"Инфа о заказе : {full_info}")
#     await message.answer("Спасибо за покупку, ваш заказ находится в обработке")
    
# @user_handler.message(F.text, StateFilter('address_waiting'))
# async def get_user_address_text_var(message: Message, state:FSMContext):
#     '''случай есльи юзер решил вручную указать свой адрес'''
#     product_data = await state.get_data()
#     location = message.text
#     user_data = await get_user_additional(message.from_user.id)
#     if not user_data:
#         await message.answer("Ошибка при выводе ваших данныех, повторите позже пожалуйста")
#         return
#     order_info = {'user_tg_id' : message.from_user.id,
#                   'address' : location,
#                   'card_id' : product_data.get('card_id')}
#     order_result = await create_order(order_info) # создаст заказ и если все успешно то вернет его иначе вернет False
#     if not order_result:
#         await message.answer("Ошиька при создании заказа, потворите еще раз")
#         return
#     full_info = (f"Новый заказ order_id : {order_result.id}\n"
#                 f"Пользователь {user_data.name}, @{message.from_user.username}, ID:{message.from_user.id}\n"
#                 f"Телефон {user_data.phone_number}\n"
#                 f"Адрес : {location}\n"
#                 f"ID товара : {product_data.get('card_id')}\n"
#                 f"Товар : {product_data.get('card_name')}\n"
#                 f"Цена : {product_data.get('card_price')}\n")
#     await message.bot.send_message(int(os.getenv("GROUP_INFO_ID")) * -1, full_info) # Id группы должно быть со знаком -    
#     await message.answer(f"Спасибо за покупку, ваш заказ находится в обработке|\n id вашего заказа :{order_result.id}")
#     await state.clear()    
    

# @user_handler.callback_query(F.data== 'get_back')
# async def get_to_initial_state(callback: CallbackQuery):
#     '''Возвращается в самое начальное меню'''
#     await callback.message.edit_reply_markup(reply_markup=inline_main_menu)

