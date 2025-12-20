from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import ForeignKey, BigInteger, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, validates
#
from dotenv import load_dotenv
import os
#логгер
from project_logger.loger_configuration import setup_logging
from sqlalchemy import func


load_dotenv()


engine = create_async_engine(url=os.getenv('DB_URL_SQLite'))

logger = setup_logging()

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs,DeclarativeBase):
    ...
    
class User(Base):
    ''''''
    __tablename__ = 'users'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name:Mapped[str] = mapped_column(String(30), nullable=True)# nullable т.к нужен еще процесс регистрации
    phone_number:Mapped[str] = mapped_column(String(30), nullable=True)
    # Отношение с Order
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    
class Category(Base):
    ''''''
    __tablename__ = 'categories'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(30))
    category_image:Mapped[str] = mapped_column(String(50), nullable=True)
    
    # обратная связь с продуктом
    products: Mapped[list["Card"]] = relationship(back_populates="category")
    
    
class Card(Base):
    '''Модель карточки товара'''
    __tablename__ = 'cards'
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(50))
    description:Mapped[str] =  mapped_column(String(256))
    price:Mapped[int]= mapped_column(Integer())
    card_image = mapped_column(String(500), nullable=True)
    category_id:Mapped[int]= mapped_column(ForeignKey('categories.id'))
    
    # Отношение с Order
    orders: Mapped[list["Order"]] = relationship(back_populates="product")
    # Отношение с Category
    category: Mapped["Category"] = relationship(back_populates="products")
    
class Order(Base):
    '''Инфа о заказе при покупке'''
    __tablename__ = 'orders'
    id:Mapped[int] = mapped_column(primary_key=True)
    user_tg_id : Mapped[int]= mapped_column(ForeignKey('users.tg_id'))
    address:Mapped[str] = mapped_column(String(200))
    card_id : Mapped[int] = mapped_column(ForeignKey('cards.id'))
    created_at = mapped_column(DateTime, server_default=func.now())
    # Отношения c User и Card
    user: Mapped["User"] = relationship(back_populates="orders")
    product: Mapped["Card"] = relationship(back_populates="orders")
    

async def async_db_main():
    logger.info("ЗАпуск асинхронного движка для SQLite")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)# создание всех наследюущих от Base моделей