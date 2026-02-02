from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import User, Order
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select,Update, select
from project_logger.loger_configuration import setup_logging
from sqlalchemy.orm import selectinload



logger = setup_logging()



class UserManager(BaseManager):
    
        def __init__(self):
                super().__init__(User)
             
        async def show_user_orders(self, session:AsyncSession, **user_params):
                '''по Id юзера вернет список с его заказами(для формирования дальнейшей клавиатуры)
                либо если нет юзера либо заказов, то False и подробную инфу о ошибке'''
                logger.info(f"Поиск заказов юзера по его данным {user_params}")
                current_user = await self.get(session, **user_params)
                if not current_user:
                        logger.warning(f"Юзера с данными {user_params} нет базе данных")
                        return []
                stmt = (
                        select(Order)
                        .options(selectinload(Order.tour))  # ← ВАЖНО: загружаем связь с туром
                        .where(Order.user_id == current_user.id)
                        .order_by(Order.status, Order.created_at.desc())  # ← Добавил сортировку по дате
                        )
                result = await session.execute(stmt)
                all_orders = result.scalars().all()
                if  all_orders:
                        logger.info(f'Успешно найдены заказы юзера, всего {len(all_orders)} шт.')
                        return all_orders
                logger.info("У данного юзера нет заказрв")
                return []
                     
        async def show_user_current_order(self, session:AsyncSession, order_id:int):
                '''По id заказа и заказа вернет инфу о нем (для формирования дальнейшей клавиатуры)
                либо если нет юзера либо заказов, то False и подробную инфу о ошибке'''
                logger.info(f"Поиск заказа {order_id} ")
                stmt = (
                        select(Order)
                        .options(selectinload(Order.tour)) 
                        .where(Order.id==order_id) 
                        )
                        
                result = await session.execute(stmt)
                current_order = result.scalars().one_or_none()
                if  current_order:
                        logger.info(f'Успешно найден заказ с id {order_id}')
                        return current_order
                logger.info(f"Не найден заказ с id {order_id}")
                return None

                
        