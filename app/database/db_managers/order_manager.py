from app.database.db_managers.base_manager import BaseManager
from app.database.all_models.models import Order, OrderStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select,Update, select, and_, delete
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
        

        async def cancel_order_2(self, session:AsyncSession, order_criterion:int|Order)->bool|None:
                '''отменяет заказ если он в статусе Pending т.к геморно возвращать уже отмененный заказ, после вызова метода не забыть 
                session.commit()!!!'''
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
                                return None
                        logger.warning(f"Статус заказа {current_order.id} переведен на cancelled")
                        current_order.status = OrderStatus.CANCELLED
                        return True        
                except Exception as err:
                        logger.error(f"Ошибка при отмене текущего заказа: {err}")
                        return None
        
                
        def check_order_expiration(self, order:Order, expiration_limit:int)->bool|None:
                '''ПРоверяет срок заказа(если он больше указанного , то вернет True, иначе False)'''
                try:
                        logger.info(f"Проверка заказа {order.id} на экспирацию")
                        if order.status != OrderStatus.CANCELLED:
                                logger.warning(f"ЗАказ {order.id} еще акутален. СТатус {order.status}")
                                return False
                        current_date = datetime.now(timezone.utc)# день на момент проверки
                        days_passed = (current_date - order.booked_at).days# сколько дней прошло от создания заказа
                        if days_passed> expiration_limit:
                                logger.warning(f"Заказ {order.id} просрочен на {days_passed - expiration_limit} дней")
                                return True
                        logger.info(f"Заказ {order.id} акутален еще {expiration_limit - days_passed} дней")
                        return False
                except Exception as err:
                        logger.error(f"ошибка при проверки заказа {order.id} на экспирацию {err}")
                        return None
                        
        async def _delete_expired_orders(self, session: AsyncSession, current_expired_orders:list[Order],expiration_limit:int=5)->tuple[bool,str]|None:
                '''Проходится по всем переданным и 
                удаляет отмененные просроченные заказы, вышедшие за границу epxiration_limit(по умолчанию 5 дней) не забыть после вызова 
                данного метода session.commit()!!!'''
                logger.info("Запущен процесс удаления просроченных отмененных заказов")
                order_ids_to_delete = []
                try:
                        for order in current_expired_orders:
                                try:
                                        expiration_result = self.check_order_expiration(order,expiration_limit)
                                        if expiration_result: # значит заказ просрочен
                                                order_ids_to_delete.append(order.id)
                                                logger.warning(f"Заказ с id {order.id} просрочен выше лимита, добавил его id в очередь на удаление")
                                except Exception as err:
                                        logger.error(f"ошибка при проверке заказа на просроченность{order.id} : {err}")
                                        continue
                        if not order_ids_to_delete:
                                logger.warning(f"из указанных заказов не один не истек выше нормы {expiration_limit}")
                                return False, f"из указанных заказов не один не истек выше нормы {expiration_limit}"
                        delete_stmt = delete(Order).where(Order.id.in_(order_ids_to_delete))
                        result = await session.execute(delete_stmt)
                        # session.commit() удален - должен вызываться извне
                        logger.info(f"Удалено {result.rowcount} заказов одним запросом, закомидьте изменения в сессии")
                        return True, result.rowcount
                except Exception as err:
                        logger.error(f"Общая ошибка при удалении заказов:{err}")
                        return None