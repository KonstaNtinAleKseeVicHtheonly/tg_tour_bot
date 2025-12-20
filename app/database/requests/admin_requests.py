from app.utils.system_decorators import set_session_connection
from app.database.models import User, Category, Card
from sqlalchemy import Select,Update, select

from project_logger.loger_configuration import setup_logging


logger = setup_logging()


@set_session_connection
async def check_product(session, product_info:dict):
    '''если продукт с указанными параметрами есть вернет его иначе False'''
    query = select(Card)
    for field_name, field_value in product_info.items():
        if hasattr(Card, field_name):
            # Добавляем условие WHERE
            query = query.where(getattr(Card, field_name) == field_value)
    existed_product = await session.scalar(query)
    if existed_product:
        logger.warning('Товар с указанными парамтерами уже существует')
        return existed_product
    return False

@set_session_connection
async def check_category(session, category_info:dict):
    '''если категория  с указанными параметрами есть вернет его иначе False'''
    query = select(Category)
    for field_name, field_value in category_info.items():
        if hasattr(Category, field_name):
            # Добавляем условие WHERE
            query = query.where(getattr(Category, field_name) == field_value)
    existed_category = await session.scalar(query)
    if existed_category:
        logger.warning('Категория с указанными парамтерами уже существует')
        return existed_category
    return False


@set_session_connection
async def create_product(session, product_info:dict):
    '''по данным собранным из FSM в админ хэндлерах создаем запись в БД'''
    try:
        if  await check_product(product_info):
            return False
        logger.info("создание продукта")
        new_product = Card()
        for k,v in product_info.items():
            if hasattr(new_product, k):
                new_product.__setattr__(k,v)
            else:
                logger.warning(f"поля {k} полученного из FSM создания продукта нет в полях таблицы Card")
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        logger.info(f"ПРодукт с данными {product_info} умпешно создан")
        return new_product
    except Exception as err:
        logger.error(f"Ошибка при создании товара : {err}")
        return False
    
@set_session_connection
async def create_category(session, category_info:dict):
    '''по данным собранным из FSM в админ хэндлерах создаем запись в БД'''
    try:
        if await check_category(category_info):
            return False
        logger.info("создание категории")
        new_category = Category()
        for k,v in category_info.items():
            if hasattr(new_category, k):
                new_category.__setattr__(k,v)
            else:
                logger.warning(f"поля {k} полученного из FSM создания категории нет в полях таблицы Category")
        session.add(new_category)
        await session.commit()
        await session.refresh(new_category)
        logger.info(f"Категория  с данными {category_info} умпешно создан")
        return new_category
    except Exception as err:
        logger.error(f"Ошибка при создании категории : {err}")
        return False

    
