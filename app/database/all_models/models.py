from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Boolean, 
    Numeric, CheckConstraint, func, BigInteger, Enum, Text, 
    select, and_, case
)
from sqlalchemy import Index
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates, DeclarativeBase
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.asyncio import AsyncAttrs

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import enum


# Перечисления
class OrderStatus(str, enum.Enum):
    PENDING = "pending"       # Ожидание оплаты
    CONFIRMED = "confirmed"   # Подтвержден
    CANCELLED = "cancelled"   # Отменен
    COMPLETED = "completed"   # Завершен



class Base(AsyncAttrs,DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=func.now(),onupdate=func.now())

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
    """Ассоциативная таблица для связи Tour-Landmark. Связь many to many"""
    __tablename__ = 'tour_landmark_association'
    
    tour_id: Mapped[int] = mapped_column(
        ForeignKey('tours.id', ondelete='CASCADE'), 
        primary_key=True
    )
    landmark_id: Mapped[int] = mapped_column(
        ForeignKey('landmarks.id', ondelete='CASCADE'), 
        primary_key=True
    )
    
    # Связи
    tour: Mapped['Tour'] = relationship(back_populates='landmark_associations')
    landmark: Mapped['Landmark'] = relationship(back_populates='tour_associations')


# Модель достопримечательности
class Landmark(Base):
    """Модель достопримечательности"""
    __tablename__ = 'landmarks'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Связи
    tour_associations: Mapped[List[TourLandmarkAssociation]] = relationship(
        back_populates='landmark',
        cascade='save-update, merge' 
    )
    
    @property# мб удалить потом
    def tours(self) -> List['Tour']:
        return [assoc.tour for assoc in self.tour_associations]
    
    def __repr__(self):
        return f"<Landmark(id={self.id}, name={self.name})>"

# Модель экскурсии
class Tour(Base):
    """Модель экскурсии"""
    __tablename__ = 'tours'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price_per_person: Mapped[Optional[str]] = mapped_column(String(20), nullable=False, comment='Цена за человека в рублях')
    image_url : Mapped[Optional[str]] = mapped_column(String(500))
    max_people: Mapped[int] = mapped_column(nullable=False, default=10)
    booked_seats: Mapped[int] = mapped_column(nullable=False, default=0)
    duration: Mapped[Optional[str]] = mapped_column(String(25),nullable=False, comment='Продолжительность тура')
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True) # мб отдельную модель сделать
    meeting_point: Mapped[Optional[str]] = mapped_column(String(500), comment='Место встречи', nullable=True)
    meeting_time: Mapped[Optional[str]] = mapped_column(String(50), comment='Время встречи', nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Связи
    landmark_associations: Mapped[List[TourLandmarkAssociation]] = relationship(
        back_populates='tour',
        cascade='save-update, merge',
    )
    orders: Mapped[List['Order']] = relationship(back_populates='tour', cascade='all, delete-orphan')
    
    # проврека при добавлении и обновлении
    __table_args__ = (
        CheckConstraint('max_people > 0', name='check_max_people_positive'),
    )
    
    @validates('max_people')
    def validate_max_people(self, key, value):
        """Проверка максимального количества людей"""
        if value < 0:
            raise ValueError("max_people должен быть больше 0")
        
        if hasattr(self, 'booked_seats') and self.booked_seats is not None: # если не указать это условие то на 
            #момент валидации booked_seats еще не будет присвоена и возникнет ошибка сравнения None и int
            if self.booked_seats > value:
                raise ValueError("Забронировано мест больше чем максимум")
        
        return value

    @validates('booked_seats')
    def validate_booked_seats(self, key, value):
        """Проверка забронированных мест"""
        if value < 0:  # Может быть 0, но не отрицательным
            raise ValueError("booked_seats не может быть отрицательным")
        
        if hasattr(self, 'max_people') and value > self.max_people:
            raise ValueError("Забронировано мест больше чем максимум")
        
        return value
    
    @property
    def available_seats(self)->int:
        '''возвращает количество оставшихся мест'''
        return self.max_people - self.booked_seats

    
    def can_book(self, quantity: int) -> bool:
        """Проверка возможности бронирования"""
        if quantity <= 0:
            return False, "Количество мест должно быть положительным"
        
        if quantity > self.max_people:
            print(f"Максимальное количество мест: {self.max_people}")
            return False
        if quantity > self.booked_seats:
            return False, f"Доступно только {self.booked_seats} мест"
        
        return True
    
    # def calculate_total_price(self, quantity: int) -> Decimal:
    #     """Рассчитать общую стоимость"""
    #     return self.price_per_person * Decimal(quantity)
    
    def __repr__(self):
        return f"<Tour(id={self.id}, name='{self.name}', price={self.price_per_person})>"

# Модель заказа
class Order(Base):
    """Модель заказа на экскурсию"""
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
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
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(200), comment='ID платежа в платежной системе')
    
    # Связи
    user: Mapped[User] = relationship(back_populates='orders')
    tour: Mapped[Tour] = relationship(back_populates='orders')
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_order_quantity_positive'),
        CheckConstraint('total_price >= 0', name='check_total_price_non_negative'),
        CheckConstraint(
            '(cancelled_at IS NULL) OR (confirmed_at IS NULL)',
            name='check_mutually_exclusive_timestamps'
        ),
        Index('idx_user_tour_status', 'user_id', 'tour_id', 'status'),
        Index('idx_booked_at', 'booked_at'),  # для поиска по дате заказа
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
        if old_status != OrderStatus.CANCELLED.value and new_status == OrderStatus.CANCELLED.value:
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
    
    
