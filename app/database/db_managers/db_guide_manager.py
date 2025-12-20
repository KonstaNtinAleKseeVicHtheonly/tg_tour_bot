from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from typing import Dict, Any, Optional

class OrderManager:
    """Менеджер для работы с заказами"""
    
    def __init__(self, session_factory):
        self.SessionLocal = session_factory
    
    @contextmanager
    def get_session(self):
        """Контекстный менеджер для сессии"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_order(
        self, 
        user_id: int, 
        tour_id: int, 
        quantity: int,
        notes: Optional[str] = None
    ) -> tuple[Optional[Order], Optional[str]]:
        """Создать новый заказ с проверками"""
        with self.get_session() as session:
            try:
                # Получаем тур с блокировкой для избежания race condition
                tour = (
                    session.query(Tour)
                    .with_for_update()
                    .filter_by(id=tour_id, is_active=True)
                    .first()
                )
                
                if not tour:
                    return None, "Экскурсия не найдена"
                
                # Проверяем возможность бронирования
                can_book, message = tour.can_book(quantity)
                if not can_book:
                    return None, message
                
                # Проверяем, не превышает ли пользователь лимит
                user_orders_count = (
                    session.query(func.sum(Order.quantity))
                    .filter_by(
                        user_id=user_id,
                        tour_id=tour_id,
                        status=OrderStatus.CONFIRMED.value
                    )
                    .scalar() or 0
                )
                
                if user_orders_count + quantity > tour.max_people:
                    return None, f"Вы уже забронировали {user_orders_count} мест. Доступно еще {tour.max_people - user_orders_count}"
                
                # Рассчитываем стоимость
                total_price = tour.calculate_total_price(quantity)
                
                # Создаем заказ
                order = Order(
                    user_id=user_id,
                    tour_id=tour_id,
                    quantity=quantity,
                    total_price=total_price,
                    notes=notes,
                    status=OrderStatus.PENDING.value
                )
                
                session.add(order)
                session.flush()  # Получаем ID
                
                # Возвращаем заказ с актуальными данными
                session.refresh(order)
                return order, None
                
            except IntegrityError as e:
                return None, f"Ошибка базы данных: {str(e)}"
            except Exception as e:
                return None, f"Ошибка при создании заказа: {str(e)}"
    
    def get_user_orders(self, user_id: int, status: Optional[str] = None) -> List[Dict]:
        """Получить заказы пользователя"""
        with self.SessionLocal() as session:
            query = (
                session.query(Order, Tour, User)
                .join(Tour, Order.tour_id == Tour.id)
                .join(User, Order.user_id == User.id)
                .filter(Order.user_id == user_id)
            )
            
            if status:
                query = query.filter(Order.status == status)
            
            results = query.order_by(Order.booked_at.desc()).all()
            
            orders_data = []
            for order, tour, user in results:
                orders_data.append({
                    'order_id': order.id,
                    'tour_name': tour.name,
                    'quantity': order.quantity,
                    'total_price': float(order.total_price),
                    'status': order.status,
                    'booked_at': order.booked_at,
                    'tour_date': tour.start_date,
                    'available_seats': tour.available_seats
                })
            
            return orders_data
    
    def cancel_order(self, order_id: int, user_id: int) -> tuple[bool, str]:
        """Отменить заказ"""
        with self.get_session() as session:
            order = (
                session.query(Order)
                .filter_by(id=order_id, user_id=user_id)
                .first()
            )
            
            if not order:
                return False, "Заказ не найден"
            
            if order.status == OrderStatus.CANCELLED.value:
                return False, "Заказ уже отменен"
            
            if order.status == OrderStatus.COMPLETED.value:
                return False, "Завершенный заказ нельзя отменить"
            
            order.cancel()
            return True, "Заказ успешно отменен"
    
    def get_tour_availability(self, tour_id: int) -> Dict[str, Any]:
        """Получить информацию о доступности тура"""
        with self.SessionLocal() as session:
            tour = session.query(Tour).get(tour_id)
            
            if not tour:
                return {}
            
            # Количество забронированных мест по статусам
            status_counts = (
                session.query(
                    Order.status,
                    func.sum(Order.quantity).label('total_quantity')
                )
                .filter_by(tour_id=tour_id)
                .group_by(Order.status)
                .all()
            )
            
            booked_by_status = {status: quantity for status, quantity in status_counts}
            
            return {
                'tour_id': tour.id,
                'tour_name': tour.name,
                'max_people': tour.max_people,
                'min_people': tour.min_people,
                'available_seats': tour.available_seats,
                'booked_seats': tour.booked_seats,
                'price_per_person': float(tour.price_per_person),
                'booked_by_status': booked_by_status
            }
    
    def get_user_tour_bookings(self, user_id: int, tour_id: int) -> List[Order]:
        """Получить бронирования пользователя на конкретный тур"""
        with self.SessionLocal() as session:
            return (
                session.query(Order)
                .filter_by(
                    user_id=user_id,
                    tour_id=tour_id,
                    status=OrderStatus.CONFIRMED.value
                )
                .all()
            )