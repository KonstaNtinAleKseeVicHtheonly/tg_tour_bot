from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Boolean, 
    Numeric, CheckConstraint, func, BigInteger, Enum, Text, 
    select, and_, case
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import enum

Base = declarative_base()

# Перечисления
class OrderStatus(str, enum.Enum):
    PENDING = "pending"       # Ожидание оплаты
    CONFIRMED = "confirmed"   # Подтвержден
    CANCELLED = "cancelled"   # Отменен
    COMPLETED = "completed"   # Завершен

class TourDifficulty(int, enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

# Модель пользователя (Telegram пользователь)
class User(Base):
    """Модель пользователя Telegram"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    orders: Mapped[List['Order']] = relationship(back_populates='user', cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint('telegram_id > 0', name='check_telegram_id_positive'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"

# Ассоциативный класс для Tour-Landmark
class TourLandmarkAssociation(Base):
    """Ассоциативная таблица для связи Tour-Landmark"""
    __tablename__ = 'tour_landmark_association'
    
    tour_id: Mapped[int] = mapped_column(
        ForeignKey('tours.id', ondelete='CASCADE'), 
        primary_key=True
    )
    landmark_id: Mapped[int] = mapped_column(
        ForeignKey('landmarks.id', ondelete='CASCADE'), 
        primary_key=True
    )
    order_index: Mapped[int] = mapped_column(default=0)
    visit_duration: Mapped[int] = mapped_column(default=30, comment='Длительность посещения в минутах')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    tour: Mapped['Tour'] = relationship(back_populates='landmark_associations')
    landmark: Mapped['Landmark'] = relationship(back_populates='tour_associations')

# Модель достопримечательности
class Landmark(Base):
    """Модель достопримечательности"""
    __tablename__ = 'landmarks'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, comment='Широта для карт')
    longitude: Mapped[Optional[float]] = mapped_column(Float, comment='Долгота для карт')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    tour_associations: Mapped[List[TourLandmarkAssociation]] = relationship(
        back_populates='landmark',
        cascade='all, delete-orphan'
    )
    
    @property
    def tours(self) -> List['Tour']:
        return [assoc.tour for assoc in self.tour_associations]
    
    def __repr__(self):
        return f"<Landmark(id={self.id}, name='{self.name}')>"

# Модель экскурсии
class Tour(Base):
    """Модель экскурсии"""
    __tablename__ = 'tours'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price_per_person: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment='Цена за человека в рублях')
    max_people: Mapped[int] = mapped_column(nullable=False, default=10)
    min_people: Mapped[int] = mapped_column(nullable=False, default=1)
    duration_hours: Mapped[int] = mapped_column(nullable=False, comment='Продолжительность в часах')
    difficulty: Mapped[int] = mapped_column(default=TourDifficulty.EASY.value, comment='Сложность 1-4')
    meeting_point: Mapped[Optional[str]] = mapped_column(String(500), comment='Место встречи')
    meeting_time: Mapped[Optional[str]] = mapped_column(String(50), comment='Время встречи')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment='Дата начала тура')
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment='Дата окончания тура')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    landmark_associations: Mapped[List[TourLandmarkAssociation]] = relationship(
        back_populates='tour',
        cascade='all, delete-orphan',
        order_by='TourLandmarkAssociation.order_index'
    )
    orders: Mapped[List['Order']] = relationship(back_populates='tour', cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint('max_people >= min_people', name='check_max_people'),
        CheckConstraint('max_people > 0', name='check_max_people_positive'),
        CheckConstraint('min_people > 0', name='check_min_people_positive'),
        CheckConstraint('price_per_person > 0', name='check_price_positive'),
        CheckConstraint('duration_hours > 0', name='check_duration_positive'),
        CheckConstraint('difficulty >= 1 AND difficulty <= 4', name='check_difficulty_range'),
    )
    
    @validates('max_people', 'min_people')
    def validate_people_count(self, key, value):
        """Валидация количества людей"""
        if value <= 0:
            raise ValueError(f"{key} must be positive")
        return value
    
    @hybrid_property
    def available_seats(self) -> int:
        """Количество свободных мест"""
        if not hasattr(self, '_available_seats'):
            # Будет вычислено через запрос
            return self.max_people - self.booked_seats
        return self.max_people - self._available_seats
    
    @available_seats.expression
    def available_seats(cls):
        """SQL выражение для расчета свободных мест"""
        from sqlalchemy import select, func, case
        
        confirmed_statuses = [OrderStatus.CONFIRMED.value, OrderStatus.PENDING.value]
        
        booked_subquery = (
            select(func.coalesce(func.sum(Order.quantity), 0))
            .where(and_(
                Order.tour_id == cls.id,
                Order.status.in_(confirmed_statuses)
            ))
            .label('booked_seats')
        )
        
        return cls.max_people - booked_subquery
    
    @hybrid_property
    def booked_seats(self) -> int:
        """Количество забронированных мест"""
        confirmed_statuses = [OrderStatus.CONFIRMED.value, OrderStatus.PENDING.value]
        return sum(order.quantity for order in self.orders 
                  if order.status in confirmed_statuses)
    
    @booked_seats.expression
    def booked_seats(cls):
        """SQL выражение для расчета забронированных мест"""
        from sqlalchemy import select, func
        
        return (
            select(func.coalesce(func.sum(Order.quantity), 0))
            .where(and_(
                Order.tour_id == cls.id,
                Order.status.in_([OrderStatus.CONFIRMED.value, OrderStatus.PENDING.value])
            ))
            .label('booked_seats')
        )
    
    def can_book(self, quantity: int) -> tuple[bool, str]:
        """Проверка возможности бронирования"""
        if quantity <= 0:
            return False, "Количество мест должно быть положительным"
        
        if quantity < self.min_people:
            return False, f"Минимальное количество мест: {self.min_people}"
        
        if quantity > self.max_people:
            return False, f"Максимальное количество мест: {self.max_people}"
        
        available = self.available_seats
        if quantity > available:
            return False, f"Доступно только {available} мест"
        
        return True, ""
    
    def calculate_total_price(self, quantity: int) -> Decimal:
        """Рассчитать общую стоимость"""
        return self.price_per_person * Decimal(quantity)
    
    def __repr__(self):
        return f"<Tour(id={self.id}, name='{self.name}', price={self.price_per_person})>"

# Модель заказа
class Order(Base):
    """Модель заказа на экскурсию"""
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey('tours.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(OrderStatus, name='order_status'),
        default=OrderStatus.PENDING.value,
        nullable=False,
        index=True
    )
    booked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Примечания к заказу')
    payment_id: Mapped[Optional[str]] = mapped_column(String(100), comment='ID платежа в платежной системе')
    
    # Связи
    user: Mapped[User] = relationship(back_populates='orders')
    tour: Mapped[Tour] = relationship(back_populates='orders')
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_order_quantity_positive'),
        CheckConstraint('total_price > 0', name='check_total_price_positive'),
        Index('idx_user_tour_status', 'user_id', 'tour_id', 'status'),
    )
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        """Валидация количества мест при создании/обновлении заказа"""
        if quantity <= 0:
            raise ValueError("Количество мест должно быть положительным")
        
        # Проверка доступности мест при создании заказа
        if self.tour and self.status in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            available_seats = self.tour.available_seats
            if quantity > available_seats:
                raise ValueError(f"Доступно только {available_seats} мест")
        
        return quantity
    
    @validates('status')
    def validate_status_change(self, key, new_status):
        """Валидация изменения статуса"""
        old_status = self.status if hasattr(self, 'status') else None
        
        # Если статус меняется на CONFIRMED, устанавливаем confirmed_at
        if old_status != OrderStatus.CONFIRMED.value and new_status == OrderStatus.CONFIRMED.value:
            self.confirmed_at = datetime.now(timezone.utc)
        
        # Если статус меняется на CANCELLED, устанавливаем cancelled_at
        if old_status != OrderStatus.CANCELLED.value and new_status == OrderStatus.CONFIRMED.value:
            self.cancelled_at = datetime.now(timezone.utc)
        
        return new_status
    
    def cancel(self):
        """Отмена заказа"""
        self.status = OrderStatus.CANCELLED.value
        self.cancelled_at = datetime.now(timezone.utc)
    
    def confirm(self):
        """Подтверждение заказа"""
        self.status = OrderStatus.CONFIRMED.value
        self.confirmed_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, tour_id={self.tour_id}, quantity={self.quantity})>"
    
    
