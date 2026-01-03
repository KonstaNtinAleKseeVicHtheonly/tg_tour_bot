# database/core/base_manager.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from project_logger.loger_configuration import setup_logging
from typing import Dict, Any, List
logger = setup_logging()



class BaseManager:
    """Базовый менеджер для всех сущностей, содердащий методы для CRUD операций"""
    
    def __init__(self, model):
        self.model = model
    
    async def get(self,session:AsyncSession, **filters):
        """
        Найти одну запись по любым фильтрам
        
        Примеры:
        await manager.get(session, id=1)
        await manager.get(session, telegram_id=123, is_active=True)
        """
        try: 
            if not filters:
                raise ValueError("Нужен хотя бы один фильтр")
            exist_checker = await self.exists(session, **filters)
            if not exist_checker:
                return exist_checker
            stmt = select(self.model).filter_by(**filters)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as err:
            logger.error(f"ошиька при чтении строки по параметрам {filters}: {err}")
    
    async def get_all(self, session:AsyncSession,skip: int = 0, limit: int = 100):
        try:
            stmt = select(self.model).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as err:
            logger.error(f"Ошибка при выводе всех туров из БД : {err}")
            return False
    
    async def create(self, session:AsyncSession,data:dict):
        try:
            exist_checker = await self.exists(session, **data)
            if exist_checker:
                logger.warning("попытка создать уже существующу строку")
                return None
            params_checker = await self._validate_model_fields(data)
            if not params_checker:
                return None
            obj = self.model(**data)
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            return obj
        except Exception as err:
            logger.error(f"ошибка при создании строки с данными {data} : {err}")
            return None
    
    async def update(self, session:AsyncSession,data:dict):
        try:
            params_checker = await self._validate_model_fields(data)
            if not await params_checker:
                return None
            exist_checker = await self.exists(session,**data)
            if not await exist_checker:
                    return None
            obj = await self.get(session=session,**data)
            if obj:
                for key, value in data.items():
                    setattr(obj, key, value)
            await session.flush()
            await session.refresh(obj)
            return obj
        except Exception as err:
            logger.error(f"Ошибка при обновлении строки с id : {id} новыми параметрами {data} : {err}")
    
    async def delete(self, session:AsyncSession,id: int):
        try:
            if not await self.exists(session,id):
                    return False
            obj = await self.get(id)
            if obj:
                await session.delete(obj)
                return True
            return False
        except Exception as err:
            logger.error(f"Ошибка при удалении строки по id {id} : {err}")
    
    async def _delete_all(self, session:AsyncSession):
        ...
        
    async def exists(self,session:AsyncSession, **params) -> bool:
        """Проверить существование"""
        current_request= select(self.model).filter_by(**params)
        current_object = await session.execute(current_request)
        result = current_object.scalar_one_or_none()
        if result is None:
            return False
        return True
    
        
    async def _validate_model_fields(self, data: Dict[str, Any]) -> None:
        """Проверяет что все переданные поля есть в модели"""
        # Получаем все колонки модели
        model_columns = {column.name for column in self.model.__table__.columns}
        
        # Проверяем каждое переданное поле
        for field in data.keys():
            if field not in model_columns:
                logger.error(f"Поле '{field}' не существует в модели {self.model.__name__}. "
                    f"Доступные поля: {', '.join(sorted(model_columns))}")
                return False
        logger.info("параметры соотвествуют столбцам таблицы")
        return True