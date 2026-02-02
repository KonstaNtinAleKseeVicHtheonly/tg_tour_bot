from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject, StateFilter,and_f,or_f
#KB
from app.keyboards.admin_kb.inline_keyboards import all_banners_kb, current_banner_kb
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.admin_states.states import  AdminBannerMode

from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database import db_managers
from sqlalchemy.ext.asyncio import AsyncSession

#логгер
from project_logger.loger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_banner_handler = Router()
admin_banner_handler.message.filter(AdminFilter()) # только юзеры с id адинов прописанных в env могут пользоваться данными хэндлерами

    
#_______________________________________________________________________________________
#LANDMARKS(достопримечательности)
    
    
@admin_banner_handler.message(StateFilter(AdminBannerMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")

    
@admin_banner_handler.callback_query(F.data=='show_all_banners')
async def show_all_banners(callback: CallbackQuery, session : AsyncSession):
    banner_db_manager = db_managers.BannerManager()
    all_banners = await banner_db_manager.get_all(session)   
    await callback.message.answer("Вот список всех банеров", reply_markup= await all_banners_kb(all_banners)) # выведет список всех достопримечательностей


@admin_banner_handler.callback_query(F.data.startswith('show_banner'))
async def show_current_banner(callback: CallbackQuery, session:AsyncSession):
    current_banner_id =  int(callback.data.split('_')[-1])
    banner_db_manager = db_managers.BannerManager()
    current_banner = await banner_db_manager.get(session=session, id=current_banner_id)
    if not current_banner:
        await callback.message.answer(f"данная lm с id : {current_banner} не найдена в базе")
        return
    await callback.message.answer_photo(photo = current_banner.image,
                                            caption = f'''{current_banner.name}\n
                                            {current_banner.description}''',
                                            reply_markup = current_banner_kb(current_banner_id))


        
@admin_banner_handler.callback_query(F.data == 'create_banner')
async def create_banner_mode(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await state.set_state(AdminBannerMode.create_name)
    await callback.message.answer("Активирован режим создания банера, пожалуйста введите название")
    
    
@admin_banner_handler.message(F.text,F.text.len()>4, StateFilter(AdminBannerMode.create_name))
async def set_banner_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text.lower())
    await state.set_state(AdminBannerMode.create_description)
    await message.answer("Введите текстовое описание")
    
@admin_banner_handler.message(StateFilter(AdminBannerMode.create_name))
async def wrong_name(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите еткстовое название банера")
    
    
@admin_banner_handler.message(F.text, F.text.len()>7,StateFilter(AdminBannerMode.create_description))
async def set_banner_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text.capitalize())
    await state.set_state(AdminBannerMode.create_img)
    await message.answer("Отправьте фотографию банера")
    
@admin_banner_handler.message(StateFilter(AdminBannerMode.create_description))
async def wrong_description(message: Message, state:FSMContext):
    await message.answer("Пожалуйста введите валидное текстовое описание банреа")
       
    
        
@admin_banner_handler.message(F.photo, StateFilter(AdminBannerMode.create_img))
async def set_banner_image(message: Message, state:FSMContext, session: AsyncSession):
    try:
        img = message.photo[-1]
        img_id = img.file_id
        await state.update_data(image = img_id)
        # сбор всей инфы и сохранение в БД
        banner_info = await state.get_data()
        logger.info("Данные о достопримечательности успешно собраны")
        banner_db_manager = db_managers.BannerManager()
        logger.info(f"Приступаю к записи банера в таблицу с параметрами : {banner_info}")
        await state.set_state(AdminBannerMode.waiting)
        creation_result = await banner_db_manager.create(session, banner_info)
        if creation_result:
                await message.answer("Банер успешно добавлена в БД")
                await session.commit() # нужно именно в хэндлере указать, Т.к в менеджере flush используем для вохможности отката
        else:
            await message.answer("ошибка при создании записив БД, чекни логи")
        await state.clear()
    except Exception as err:
        logger.error(f"Произошла какая то шляпа в хэндлере на запись строки в Banner:{err}")
        await session.rollback()
        await state.clear()
        await message.answer(f'Произошла непредвиденная ошибка : {err}, чекни логи')


    
@admin_banner_handler.message(StateFilter(AdminBannerMode.create_img))
async def wrong_picture(message: Message, state:FSMContext):
    await message.answer("Пожалуйста отправьте фотографию")
    
            
@admin_banner_handler.callback_query(F.data.startswith('delete_banner'))
async def delete_current_landmark(callback: CallbackQuery, session : AsyncSession):
    current_lm_id = int(callback.data.split('_')[-1])
    banner_db_manager = db_managers.BannerManager()
    delete_result = await banner_db_manager.delete(session, current_lm_id)
    if delete_result:
        await session.commit() 
        await callback.answer(f"БАнер с id : {current_lm_id} удалена успешно", show_alert=True)
    else:
        await callback.answer(f"Ошибка при удалении Банера с id : {current_lm_id}, чекаай логи", show_alert=True)
    



