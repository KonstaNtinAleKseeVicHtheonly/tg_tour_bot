from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
# фитры 
from aiogram.filters import CommandStart, Command
from app.filters.chat_group_filters import GroupFilter
#KB
from app.keyboards.user_kb.inline_keyboards import user_inline_main_menu
from app.keyboards.base_keyboards import create_inline_kb
from app.keyboards.user_kb.reply_keboards import request_user_contact
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.FSM.user_states.states import UserRegistration
from aiogram.filters import StateFilter, or_f
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from dotenv import load_dotenv

# DB
from app.database import db_managers
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_queries import get_current_banner_query, check_user_existance, _create_new_user_query, get_current_user_query# слой абстракции для менеджера БД(маленькая связанность)
logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env



user_main_handler = Router()
user_main_handler.message.filter(GroupFilter(['private']))


@user_main_handler.message(Command('start'))
async def initial_menu(message : Message, state:FSMContext, session: AsyncSession):
    '''запуск стартовой клавы для юзреа + регисрация(или проверка юзера в бд если он уже зарегался
    по telegram_id)'''
    await state.clear()
    await message.delete()
    if not await check_user_existance(session, user_tg_id=message.from_user.id):
        logger.warning('Новый юзер, регистрация в базе')
        await state.set_state(UserRegistration.set_phone_number)
        await message.answer("Я смортю ты тут новенький, сейчас зарегистрируем тебя")
        new_user_info = {'telegram_id' : message.from_user.id,
                            'username' : message.from_user.username,
                            'first_name' : message.from_user.first_name,
                            'last_name' : message.from_user.last_name}
        await state.update_data(**new_user_info)
        await message.answer("Укажите пожалуйста свой номер телефона или введите вручную", reply_markup= request_user_contact())
    else: # юзер уже есть в базе
        main_theme = await get_current_banner_query(session)
        if main_theme:# банер подгрузился все ок
            await message.answer(f"Привет {message.from_user.username}")
            await message.answer_photo(photo = main_theme.image,
                                                caption = main_theme.description,
                                                reply_markup = user_inline_main_menu)
        else:# если банер не подгрузился 
            await message.answer(f"Привет {message.from_user.username}, чего изволите?", reply_markup=user_inline_main_menu)
        
@user_main_handler.callback_query(F.data=='user_main_menu')
async def back_to_initial_menu(callback: CallbackQuery, session:AsyncSession):
    '''что бы в  можно было возвращаться к изначальному меню'''
    await callback.message.delete()
    main_theme = await get_current_banner_query(session)
    if main_theme:# банео подгрузился все ок
        await callback.message.answer_photo(photo = main_theme.image,caption = main_theme.description, reply_markup = user_inline_main_menu)
    else:# если банер не подгрузился
            await callback.message.answer(f"Привет {callback.message.from_user.username}, чего изволите?", reply_markup=user_inline_main_menu)
    await callback.message.answer("Вот список всех туров", reply_markup= user_inline_main_menu)

    
@user_main_handler.message(F.contact,StateFilter(UserRegistration.set_phone_number))
async def get_phone_from_contact(message : Message, state:FSMContext):
    '''юзер выбрал номер телефона из своих контактов'''
    user_contact = message.contact.phone_number
    await state.update_data(phone_number=user_contact)
    await state.set_state(UserRegistration.confirm_registation) # доп состояние что бы данные из state никуда ен делись
    confirm_kb = create_inline_kb([{'text':'Да, все верно','callback_data':'correct_number'},
                                   {'text':'Указать другой телефон', 'callback_data':'wrong_number'}])
    await message.answer(f"Ваш номер телефона :{user_contact}, верно?", reply_markup= confirm_kb)
    
@user_main_handler.message(F.text, StateFilter(UserRegistration.set_phone_number))
async def get_phone_directlry(message: Message, state:FSMContext):
    '''юзер ввел вручную номер телефона'''
    if message.text.startswith('+'):
        user_phone = message.text[1:]
    else:
        user_phone = message.text # если начинается с 8
    if not user_phone.isdigit():
        await message.answer("ПОжалуйста введите корректный номер телефона")
        return
    await state.update_data(phone_number = user_phone)
    await state.set_state(UserRegistration.confirm_registation) # доп состояние что бы данные из state никуда ен делись
    confirm_kb = create_inline_kb([{'text':'Да, все верно','callback_data':'correct_number'},
                                {'text':'Указать другой телефон', 'callback_data':'wrong_number'}])
    await message.answer(f"Ваш номер телефона :{user_phone}, верно?", reply_markup= confirm_kb)
        
@user_main_handler.message(StateFilter('reg_phone_number'))
async def invalid_number(message: Message):
    '''если юзер вместо номера какую то шляпу вводит'''
    await message.answer("ПОжалуйста введите валидный номер телефона")
    
@user_main_handler.callback_query(F.data=='correct_number', StateFilter(UserRegistration.confirm_registation))
async def finish_user_registration(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''после подвтерждения юзео своего номера через нажатие на кнопку завершаем процесс регистрации'''
    user_info = await state.get_data()
    result = await _create_new_user_query(session,user_info)
    await state.clear()
    if result:
        await session.commit()
        await callback.message.answer("Регистрация прошла успешно", reply_markup=user_inline_main_menu)
    else:
        await callback.message.answer("Ошибка при регистрации, введите команду /start для повторного запуска")
    
@user_main_handler.callback_query(F.data=='wrong_number', StateFilter(UserRegistration.confirm_registation))
async def user_number_deny(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    '''если юзер решил другой номер ввести'''
    await callback.message.delete()
    await state.set_state(UserRegistration.set_phone_number) # по новой попросим ввести юзера номер телефона, но  остальные данные сохраним
    await callback.message.answer("Укажите пожалуйста свой номер телефона или введите вручную", reply_markup= request_user_contact())
    
    
# взаимодейтсвие с меню
    
    
@user_main_handler.callback_query(F.data=='about_company')
async def show_about_company(callback: CallbackQuery, session:AsyncSession):
    '''Инфа о компании(мб контакты владельца сделать через отдельную клаву)'''
    await callback.message.delete()
    additional_kb = create_inline_kb([{'text':'Связаться с нами', 'callback_data':'boss_contacts'},
                                      {'text' : 'Вернуться назад','callback_data':'user_main_menu'}
                                      ])
    about_company_banner = await get_current_banner_query(session,banner_name='about_company')
    if about_company_banner:
        await callback.message.answer_photo(photo = about_company_banner.image,caption = about_company_banner.description, 
                                            reply_markup = additional_kb)
    else:
        company_info = '''
                        Мы создаём маршруты, где история оживает. Не просто экскурсии, а погружение в атмосферу Беларуси — от средневековых замков до современных арт-пространств.
                        Наш подход:
                        📍 Локации с характером — выбираем места, где чувствуется дух страны
                        🕐 Продуманный тайминг — максимум впечатлений без усталости
                        👥 Небольшие группы — персональное внимание каждому гостю
                        🎯 Глубина вместо галочек — лучше узнать 5 мест, чем мельком увидеть 15
                        Каждый тур — это история, которую вы увозите с собой.'''

        await callback.message.answer(company_info, reply_markup= additional_kb) 
    
    
@user_main_handler.callback_query(F.data=='show_me')
async def show_accout_info(callback: CallbackQuery, session:AsyncSession):
    '''покажет инфо о юзере'''
    current_user = await get_current_user_query(session, telegram_id=callback.from_user.id) # по tg_id юзера находим его в базе
    if not current_user:
        await callback.message.answer("Вы еще не зарегестрировались в базе!")
    else:
        text_info = f'''Имя : {current_user.username}\n
                Телефон : {current_user.phone_number} \n'''
        await callback.message.answer(text_info)

    
@user_main_handler.callback_query(F.data=='boss_contacts')
async def show_info_about_boss(callback: CallbackQuery):
    '''что бы в  можно было возвращаться к изначальному меню'''
    await callback.message.delete()
    # мб прокинуть через модель User вместо хардкода
    boss_info = '''Владелец:Константин Алексеевич|\n
                    Номер телефона : 88005553535|\n
                    электронная почта : ept.13@inbox.ru|'''
    back_to_menu = create_inline_kb([{'text':'Вернуться назад','callback_data':'user_main_menu'}])
    await callback.message.answer(boss_info, reply_markup= back_to_menu)
    
     
   

