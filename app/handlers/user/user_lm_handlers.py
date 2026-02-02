from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
# фитры 
from app.filters.chat_group_filters import GroupFilter
#KB
from app.keyboards.user_kb.inline_keyboards import  current_tour_landmarks_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.filters import StateFilter, or_f
# системыне утилиты
from project_logger.loger_configuration import setup_logging
from dotenv import load_dotenv

# DB
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_queries import get_current_banner_query, get_current_lm_query, get_tour_landmarks_query# слой абстракции для менеджера БД(маленькая связанность)
logger = setup_logging()
load_dotenv() # для подгрузки переменных из .env


user_lm_handler = Router()
user_lm_handler.message.filter(GroupFilter(['private']))

@user_lm_handler.callback_query(F.data.startswith("tour_landmarks"))
async def show_tour_landmarks(callback: CallbackQuery, session : AsyncSession):
    '''покажет все связанные с Туром достопримечательности'''
    await callback.message.delete()
    tour_id = int(callback.data.split('_')[-1])

    landmarks_banner = await get_current_banner_query(session, banner_name='all_lm_banner')
    tour_landmarks = await get_tour_landmarks_query(session, tour_id) # берем все landmarks связанные с данным туром по его id
    current_lms_kb = await current_tour_landmarks_kb(tour_id, tour_landmarks)
    if landmarks_banner:
        await callback.message.answer_photo(photo = landmarks_banner.image,caption = landmarks_banner.description, 
                                            reply_markup = current_lms_kb)
    else:
        await callback.message.answer("Список достопримечательностей по текущему туру:", reply_markup= current_lms_kb) # тут же передаем lanmarks для создания адаптивной клавиатуры
        
        
        
        
@user_lm_handler.callback_query(F.data.startswith("show_landmark"))
async def show_landmark_info(callback: CallbackQuery, session : AsyncSession):
    '''по выбранному туру покажет все связанные с ним достопримечательнстти'''
    #в колбэке у нас id данной landmark и общей для данных landmarks тура, пришлось изъебнуться немного
    await callback.message.delete()
    landmarks_tour_id = int(callback.data.split('|')[-1].split('_')[-1]) #тур общий для данных достопримечательностей
    current_lm_id =  int(callback.data.split('|')[0].split('_')[-1]) # id выбранной Достопримечательности
    current_landmark = await get_current_lm_query(session=session, lm_id=current_lm_id)
    back_to_common_info = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data=f"show_tour_{landmarks_tour_id}")]])
    if not current_landmark:
        await callback.message.answer(f"данная lm с id : {current_landmark} не найдена в базе", reply_markup=back_to_common_info)
    else:
        await callback.message.answer_photo(photo = current_landmark.image_url,
                                                caption = f'''{current_landmark.name}\n
                                                Описание{current_landmark.description}\n
                                                Ссылка на достопримечательность в интернете: {current_landmark.url}''',
                                                reply_markup = back_to_common_info)