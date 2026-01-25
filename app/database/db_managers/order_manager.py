from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Order, OrderStatus
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession
from sqlalchemy import Select,Update, select, and_
from project_logger.loger_configuration import setup_logging
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime, timedelta, timezone# для проверки экспирации заказа

logger = setup_logging()



class OrderManager(BaseManager):

        
        def __init__(self):
                super().__init__(Order)

        def set_order_payment_id(self):
                '''генерирует рандомное числовое id заказа'''
                payment_id = str(uuid.uuid4()) # иначе ошибка при записи в таблицу, Там тип str 
                return payment_id
            
        async def show_user_current_order(self, session:AsyncSession, order_id:int):
                '''По id заказа и заказа вернет инфу о нем (для формирования дальнейшей клавиатуры)
                либо если нет юзера либо заказов, то False и подробную инфу о ошибке'''
                logger.info(f"Поиск заказа {order_id} ")
                stmt = (
                        select(self.model)
                        .options(selectinload(self.model.tour)) 
                        .where(self.model.id==order_id) 
                        )
                        
                result = await session.execute(stmt)
                current_order = result.scalars().one_or_none()
                if current_order:
                        logger.info(f'Успешно найден заказ с id {order_id}')
                        return current_order
                logger.info(f"Не найден заказ с id {order_id}")
                return None
        
        async def cancel_order(self, session:AsyncSession, order_criterion:int|Order)->bool|None:
                '''отменяет заказ(если он недавшнинй (date.time.now - 5 дней), 
                то статус меняется на отменен - cancelled), если старше то он удаляется из бд совсем
                Указать либо id заказа либо сам заказ(своместил применение метода для админа и юзера пришлось изъебнуться)'''
                try:
                        logger.info(f"Начало процесса отмены заказа order{order_criterion}")
                        if not isinstance(order_criterion, int) and not isinstance(order_criterion,Order):
                                raise ValueError("передано неверное значение в метод")
                        if isinstance(order_criterion, int):
                                logger.warning("Указан id заказа")
                                current_order = await self.get(session, id=order_criterion) # тогда находим по id
                        elif isinstance(order_criterion, Order):
                                logger.warning("Передан сам заказа (экз модели ORder)")
                                current_order = order_criterion
                        if not current_order: # если не найдне заказ по указанному id
                                return current_order # None вернет
                        if current_order.status == OrderStatus.CANCELLED:
                                logger.warning(f"Заказ с id {current_order.id} уже отменен")
                                if await self.check_order_expiration(current_order):# просрочен ли отмененный заказ или нет
                                        await self.delete(session,current_order.id)
                                        return True
                        logger.warning(f"Статус заказа {current_order.id} переведен на cancelled")
                        current_order.status = OrderStatus.CANCELLED
                        return True        
                except Exception as err:
                        logger.error(f"Ошибка при отмене текущего заказа: {err}")
                        return None
                
        async def check_order_expiration(self,order:Order, expiration_limit:int=5)->bool|None:
                '''ПРоверяет срок заказа(если он больше указанного , то вернет True, иначе False)'''
                try:
                        logger.info(f"Проверка заказа {order.id} на экспирацию")
                        if order.status != OrderStatus.CANCELLED:
                                logger.warning(f"ЗАказ {order.id} еще акутален. СТатус {order.status}")
                                return False
                        current_date = datetime.now(timezone.utc)# день на момент проверки
                        days_passed = (current_date - order.booked_at).days# сколько дней прошло от создания заказа
                        is_expired = days_passed - expiration_limit
                        if is_expired > 0:
                                logger.warning(f"Заказ {order.id} просрочен на {is_expired} дней")
                                return True
                        logger.info(f"Заказ {order.id} акутален еще {-1 * is_expired} дней")
                        return False
                except Exception as err:
                        logger.error(f"ошибка при проверки заказа {order.id} на экспирацию {err}")
                        return None
                        
        async def _delete_expired_orders(self, session: AsyncSession, current_user_id:int):
                '''Проходится по всем заказам юзера по указанному id и 
                удаляет отмененные просроченные заказы, не забыть после вызова 
                данного метода session.commit()!!!'''
                try:
                        logger.info(f"Запущен процесс удаления просроченных отмененных заказов юзера с id {current_user_id}")
                        stmt = select(Order).where(and_(
                                        Order.user_id == current_user_id,
                                        Order.status == OrderStatus.CANCELLED))
                        result = await session.execute(stmt)
                        cancelled_orders = result.scalars().all()
                        for order in cancelled_orders:
                                await self.cancel_order(session, order)# 
                        logger.info(f"ЗАвершен процесс удаления просроченных заказов Юзера с id{current_user_id}")
                        return True
                except Exception as err:
                        logger.error(f"ошибка при удалении просроченнхы заказов юзера {current_user_id} : {err}")
                        return False
                # expiration_date = datetime.now(timezone.utc) - timedelta(days=expiration_limit)
                # if order.booked_at < expiration_date:
                #         logger.warning(f"Заказ {order.id} просрочен")
                #         return True
                # remaining_days = (order.booked_at - expiration_date).days
                # logger.warning(f"заказ акутален еще {remaining_days} дней")
                # return False
