from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from aiogram.filters import CommandStart, Command
from app.filters.chat_group_filters import GroupFilter
from app.filters.admin_filters import AdminFilter
#KB
from app.keyboards.user_kb.inline_keyboards import user_inline_main_menu,  all_tours_kb, current_tour_kb, current_tour_landmarks_kb
from app.keyboards.base_keyboards import create_inline_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
from aiogram.fsm.state import State
# колбэки
from aiogram.types import CallbackQuery
# DB
from app.database import db_managers
from sqlalchemy.ext.asyncio import AsyncSession
logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env



user_handler = Router()
# user_handler.message.filter(GroupFilter(['private']))



@user_handler.message(Command('start'))
async def initial_menu(message : Message, state:FSMContext, session: AsyncSession):
    '''покажет всю инфу о юзере'''
    await state.clear()
    user_db_manager = db_managers.UserManager()
    if not await user_db_manager.exists(session, telegram_id=int(message.from_user.id)):
        logger.warning('Новый юзер, регистрация в базе')
        await message.answer("Я смортю ты тут новенький, сейчас зарегистрируем тебя")
        new_user_info = {'telegram_id' : int(message.from_user.id),
                            'username' : message.from_user.username,
                            'first_name' : message.from_user.first_name,
                            'last_name' : message.from_user.last_name,
                            'phone_number' : 'no_info'}
        await user_db_manager.create(session, new_user_info )
    else:
        await message.answer(f"Привет {message.from_user.username}, чего изволите?", reply_markup=user_inline_main_menu)
    
    
@user_handler.callback_query(F.data=='user_main_menu')
async def back_to_initial_menu(callback: CallbackQuery):
    '''что бы в  можно было возвращаться к изначальному меню'''
    await callback.message.answer("Вот список всех туров", reply_markup= user_inline_main_menu)
    
@user_handler.callback_query(F.data=='about_company')
async def show_about_company(callback: CallbackQuery):
    '''Инфа о компании(мб контакты владельца сделать через отдельную клаву)'''
    company_info = '''
                    Мы создаём маршруты, где история оживает. Не просто экскурсии, а погружение в атмосферу Беларуси — от средневековых замков до современных арт-пространств.
                    Наш подход:
                    📍 Локации с характером — выбираем места, где чувствуется дух страны
                    🕐 Продуманный тайминг — максимум впечатлений без усталости
                    👥 Небольшие группы — персональное внимание каждому гостю
                    🎯 Глубина вместо галочек — лучше узнать 5 мест, чем мельком увидеть 15
                        Каждый тур — это история, которую вы увозите с собой.'''
    additional_kb = create_inline_kb([{'text':'Связаться с нами', 'callback_data':'boss_contacts'},
                                      {'text' : 'Вернуться назад','callback_data':'user_main_menu'}
                                      ])
    await callback.message.answer(company_info, reply_markup= additional_kb) 
    
@user_handler.callback_query(F.data=='boss_contacts')
async def show_info_about_boss(callback: CallbackQuery):
    '''что бы в  можно было возвращаться к изначальному меню'''
    # мб прокинуть через модель User вместо хардкода
    boss_info = '''Владелец:Константин Алексеевич|\n
                    Номер телефона : 88005553535|\n
                    электронная почта : ept.13@inbox.ru|'''
    back_to_menu = create_inline_kb([{'text':'Вернуться назад','callback_data':'user_main_menu'}])
    await callback.message.answer(boss_info, reply_markup= back_to_menu)
    
     
    
    
@user_handler.callback_query(F.data=='show_all_tours')
async def show_all_tours(callback: CallbackQuery, session : AsyncSession):
    tour_db_manager = db_managers.TourManager()
    all_tours = await tour_db_manager.get_all(session)
    await callback.message.answer("Вот список всех туров", reply_markup= await all_tours_kb(all_tours)) # выведет список всех туров
    
    
@user_handler.callback_query(F.data.startswith('show_tour'))
async def get_current_tour_info(callback: CallbackQuery, session:AsyncSession):
    current_tour_id =  int(callback.data.split('_')[-1])
    tour_db_manager = db_managers.TourManager()
    current_tour= await tour_db_manager.get(session=session, id=current_tour_id)
    if not current_tour:
        back_to_common_info = create_inline_kb([{'text':'Назад', 'callback_data':'show_all_tours'}])
        await callback.message.answer("по данному туру нет информации к сожалению", reply_markup = back_to_common_info)
    else:
        await callback.message.answer_photo(photo = current_tour.image_url,
                                                caption = f'''{current_tour.name}\n
                                                {current_tour.description}''',
                                                reply_markup = current_tour_kb(current_tour_id))
        
    
    
#мб переделать под FSM что бы не было лишних запросов в БД
@user_handler.callback_query(F.data.startswith("detailed_info_tour"))
async def show_tour_detailed_info(callback: CallbackQuery, session : AsyncSession):
    '''детальная инфа о туре'''
    current_tour_id =  int(callback.data.split('_')[-1])
    back_to_common_info = create_inline_kb([{'text':'Назад', 'callback_data':f"show_tour_{current_tour_id}"}])
    tour_db_manager = db_managers.TourManager()
    current_tour= await tour_db_manager.get(session=session, id=current_tour_id)
    if not current_tour:
        await callback.message.answer("Детальная информация по данной экскурсии пока что отсутствует",reply_markup=back_to_common_info)
    else:
        detailed_info_2 = await tour_db_manager.show_detailed_info_for_user(session, current_id=current_tour_id, skip_fields=['description', 'id', 'updated_at', 'created_at', 'image_url'])
        # detailed_info = f"""Подробная информация о туре {current_tour.name}:\n 
        #                     Длительность : {current_tour.duration}\n
        #                     Максимальное количество людей : {current_tour.max_people}\n
        #                     Осталось мест : {current_tour.booked_seats}\n
        #                     Время отправки : {current_tour.meeting_time}\n
        #                     Место отправки : {current_tour.meeting_point}\n
        #                     Цена за человека : {current_tour.price_per_person}
        #                     """
        await callback.message.answer(detailed_info_2, reply_markup=back_to_common_info)
        
@user_handler.callback_query(F.data.startswith("tour_landmarks"))
async def show_tour_landmarks(callback: CallbackQuery, session : AsyncSession):
    '''покажет все связанные с Туром достопримечательности'''
    tour_id = int(callback.data.split('_')[-1])
    tour_lm_db_manager = db_managers.TourManager()
    tour_landmarks = await tour_lm_db_manager.get_tour_landmarks(session, tour_id) # берем все landmarks связанные с данным туром по его id

    await callback.message.answer("Список достопримечательностей по текущему туру:", reply_markup= await current_tour_landmarks_kb(tour_id, tour_landmarks)) # тут же передаем lanmarks для создания адаптивной клавиатуры
        
        
        
        
@user_handler.callback_query(F.data.startswith("show_landmark"))
async def show_landmark_info(callback: CallbackQuery, session : AsyncSession):
    #в колбэке у нас id данной landmark и общей для данных landmarks тура, пришлось изъебнуться немного
    landmarks_tour_id = int(callback.data.split('|')[-1].split('_')[-1]) #тур общий для данных достопримечательностей
    current_lm_id =  int(callback.data.split('|')[0].split('_')[-1]) # id выбранной Достопримечательности
    lm_db_manager = db_managers.LandMarkManager()
    current_landmark = await lm_db_manager.get(session=session, id=current_lm_id)
    back_to_common_info = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data=f"show_tour_{landmarks_tour_id}")]])
    if not current_landmark:
        await callback.message.answer(f"данная lm с id : {current_landmark} не найдена в базе", reply_markup=back_to_common_info)
    else:
        await callback.message.answer_photo(photo = current_landmark.image_url,
                                                caption = f'''{current_landmark.name}\n
                                                {current_landmark.description}''',
                                                reply_markup = back_to_common_info)
        
        
    
 
    
# @user_handler.message(or_f(Command('menu'), F.text.lower().in_(['меню','menu','экскурси'])))
# async def show_menu(message : Message, state:FSMContext):
#     '''покажет всю инфу о юзере'''
#     await state.clear()
#     await message.answer("Лови актуальное меню")
    
# @user_handler.message(Command('show_me'))
# async def show_user_info(message : Message, state:FSMContext):
#     '''покажет всю инфу о юзере'''
#     await state.clear()
#     await message.answer("Запущен интерактивный режим", reply_markup=reply_request_kb)

# @user_handler.message(Command('about'))
# async def common_info(message : Message, state:FSMContext):
#     '''покажет всю инфу о юзере'''
#     await message.answer("Мы являемся крупным представителем РБ", reply_markup=delete_reply_kb)
    
# @user_handler.message(Command('payment'))
# async def choose_payment(message : Message):
#     '''покажет всю инфу о юзере'''
#     await message.answer("Выберите вариант оплаты")
    
# @user_handler.message(
#     F.text.lower().contains("доставк") |
#     F.text.lower().contains("варианты доставки") |
#     F.text.lower().contains("способы доставки"))
# @user_handler.message(Command('shipping'))
# async def choose_shipping(message : Message):
#     '''покажет всю инфу о юзере'''
#     await message.answer("Выберите вариант доставки")

# @user_handler.message(F.text)
# async def unpredictable_message(message : Message):
#     '''В случае непредвиденного поведения '''
#     await message.answer(f"Непредвиденная текстовая команда : {message.text}")
        
 
# @user_handler.message(F.photo)
# async def unpredictable_img(message : Message):
#     '''В случае непредвиденного поведения '''
#     await message.answer("Ух ты какая клевая фотка")
        
 

    
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

