from app.utils.system_decorators import set_session_connection
from app.database.all_models.models import User
from sqlalchemy import Select,Update, select

from project_logger.loger_configuration import setup_logging


logger = setup_logging()


# @set_session_connection
# async def set_user(session, user_tg_id:int):
#     '''версия проверки наличия юзера в БД с дальнейшей логикой регистрации в FSM'''
#     try:
#         user = await session.scalar(select(User).where(User.tg_id==user_tg_id))
#         if not user:
#             logger.info(f"Юзера с tg_id {user_tg_id} нет в Базе, начинаем создание")
#             new_user = User(tg_id=user_tg_id)
#             session.add(new_user)
#             await session.commit()
#             logger.info(f"Успешно добавили нового юзера с tg_id : {user_tg_id} в базу данных")
#             return False
#         logger.info(f'Юзер с tg_id {user_tg_id} есть в БД')
#         return user if user.name else False # если нет имени у юзера то он зашел в превый раз и только создался
#     except Exception as err:
#         logger.error(f'''Ошибка при попытке вывода инфы о ЮЗере
#                      по его id {user_tg_id} : {err}''')
        

# @set_session_connection
# async def update_user(session, user_tg_id:int, user_data:dict):
#     '''Обновляет указанные данные о юзере'''
#     try:
#         user = await session.scalar(select(User).where(User.tg_id==user_tg_id))
#         if not user:
#            logger.warning("Юзера нет в бд")
#            return False
#         logger.info(f"Юзер найден, дополняем данные полученные при регистрации: {user_data.values()}")
#         for key, value in user_data.items():
#             if hasattr(user, key):
#                 setattr(user, key, value)
#         await session.commit()
#         await session.refresh(user)
#         logger.info("Данные успешно обновлены")
#         return user
#     except Exception as err:
#         logger.error(f'''Ошибка при регистрации юзера с tg_id {user_tg_id} : {err}''')
#         return False
        


# @set_session_connection
# async def get_user_additional(session, user_tg_id:int, **user_info):
#     '''Если юзер есть в  бд выводит его по tg_id иначе регистрирует его'''
#     try:
#         user = await session.scalar(select(User).where(User.tg_id==user_tg_id))
#         if user or not user_info:
#                     logger.info(f'Юзер с tg_id {user_tg_id} есть в БД')
#                     return user
#         elif not user and user_info:
#             logger.info(f"Юзера с tg_id {user_tg_id} нет в Базе, начинаем создание")
#             new_user_data = {'tg_id': user_tg_id, **user_info}
#             new_user = User(**new_user_data)
#             await session.add(new_user)
#             await session.commit()
#             await session.refresh(new_user) # обновление инфы о новм объекте в БД
#             logger.info(f"Успешно добавили нового юзера с tg_id : {user_tg_id}в базу данных")
#             return new_user
#         else:
#             logger.warning("Юзера нет в бд и не введена инфа о нем для добваления!!!")
#             return False
#     except Exception as err:
#         logger.error(f'''Ошибка при попытке вывода инфы о ЮЗере
#                      по его id {user_tg_id} : {err}''')
#         return False
        
# @set_session_connection
# async def get_categories(session):
#     try:
#         logger.info("Вывод категорий товаров пользователю")
#         all_categories_raw = await session.scalars(select(Category))
#         all_categories_final = all_categories_raw.all()
#         if not len(all_categories_final):
#             logger.warning("Пока что нет категорий товаров в БД")
#             return False
#         logger.info(f"Всего нашлось {len(all_categories_final)} категорий товаров")
#         return all_categories_final
#     except Exception as err:
#         logger.error(f"Ошибка при выводе категорий товаров : {err}")
#         return False
    
# @set_session_connection
# async def get_current_category(session, category_name:str):
#     try:
#         logger.info("Вывод текущей категории по ее имени")
#         current_category = await session.scalar(select(Category).where(Category.name==category_name))
#         if not current_category:
#             logger.warning(f"Не нашлось по категории по имени : {category_name}")
#             return False
#         logger.info(f"успешно нашлась категория {category_name}")
#         return current_category
#     except Exception as err:
#         logger.error(f"Ошибка при выводе категории {category_name} : {err}")
#         return False
        
# @set_session_connection
# async def get_cards_from_category(session, category_id:int):
#     try:
#         logger.info("Вывод карточек товара по категории")
#         all_cards_from_category = await session.scalars(select(Card).where(Card.category_id==category_id))
#         all_cards_final = all_cards_from_category.all()
#         if not len(all_cards_final):
#             logger.warning(f"Пока что нет карточек товара по данной категории : {category_id}")
#             return False
#         logger.info(f"Всего нашлось {len(all_cards_final)} карточек товаров товаров")
#         return all_cards_final
#     except Exception as err:
#         logger.error(f"Ошибка при выводе категорий товаров : {err}")
#         return False
    
    
# @set_session_connection
# async def get_card_info(session, card_id:int):
#     try:
#         logger.info(f"Вывод инфы о товаре по его id {card_id}")
#         card_info = await session.scalar(select(Card).where(Card.id == card_id))
#         if not card_info:
#             logger.warning(f"Нет инфы о товаре по id {card_id}")
#             return False
#         logger.info(f"Найдена инфа о товаре {card_info.__dict__.values()}")
#         return card_info
#     except Exception as err:
#         logger.error(f"Ошибка при выводе инфы о товаре по id : {err}")
#         return False
        
# @set_session_connection
# async def create_order(session, order_info:dict):
#     ''''По собранной инфе о юзере и товаре создает запись в модели Order'''
#     try:
#         logger.info(f"Формируем заказ : {order_info.items()}")
#         new_order = Order()
#         for k,v in order_info.items():
#             if hasattr(new_order, k):
#                 new_order.__setattr__(k,v)
#             else:
#                 logger.warning(f"поля {k} полученного из FSM создания продукта нет в полях таблицы Card")
#         session.add(new_order)
#         await session.commit()
#         await session.refresh(new_order)
#         logger.info("Заказ создан успешно")
#         return new_order
#     except Exception as err:
#         logger.error(f"Ошибка при создании заказа : {order_info.items()}\n ошибка : {err}")