# database/core/base_manager.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
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
            filters_checker = await self._validate_model_fields(filters)
            if not filters_checker:
                return filters_checker
            stmt = select(self.model).filter_by(**filters)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as err:
            logger.error(f"ошиька при чтении строки по параметрам {filters}: {err}")
            return False
    
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
                logger.warning(f"попытка создать уже существующу строку добавляя данные {data}в таблице {self.model.__name__} ")
                return None
            params_checker = await self._validate_model_fields(data)
            if not params_checker:
                
                return None
            obj = self.model(**data)
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            logger.info(f"строк создана успешно в таблице {self.model.__name__} с данными {data}")
            return obj
        except Exception as err:
            logger.error(f"ошибка при создании строки с данными {data} в таблице {self.model.__name__} : {err}")
            return None
    
    async def update(self, session:AsyncSession,data_to_find_object:dict,data_to_update_object:dict):
        '''Находи по data_to_find_object строку в модели и обновляет ее данными из data_to_update_object'''
        try:
            data_to_find_object_checker = await self._validate_model_fields(data_to_find_object)
            data_to_update_object_checker = await self._validate_model_fields(data_to_update_object)
            if not data_to_find_object_checker or not data_to_update_object_checker :
                return None
            current_object = await self.get(session, **data_to_find_object)
            if not current_object:
                logger.warning(f"объект не найден по данным параметрами в таблице {self.model.__name__}")
                return None

            for key, value in data_to_update_object.items():
                setattr(current_object, key, value)
            await session.flush()
            await session.refresh(current_object) # не забыть в хэндлере прописать await session.commit() после вызова метода
            return current_object
        except Exception as err:
            logger.error(f"Ошибка  в таблице {self.model.__name__} при обновлении строки с новыми параметрами {data_to_update_object} : {err}")
            return None
    
    async def delete(self, session:AsyncSession,current_id: int):
        try:
            if not await self.exists(session,id=current_id):
                    return False
            obj = await self.get(session,id=current_id)
            if obj:
                await session.delete(obj)
                return True
            return False
        except Exception as err:
            logger.error(f"Ошибка при удалении строки по id {id} : {err}")
            return None
    
    async def show_detailed_info_for_user(self, session : AsyncSession, current_id:int,skip_fields:list[str]=None)->str:
        '''выведет строку с красивым отображением столбцов модели и их значений,
        кроме длинных занчений, таких как описание  и технической инфы(id, Дата создания и прочее)
        также передается список столбцов таблицы которые выводить не нужно (skip_fields которые)!!!'''
        try:
            if skip_fields is None:
                skip_fields = []
            logger.info(f"Вывод детальной инфы о строке в таблице {self.model.__name__ } по id : {current_id}")
            stmt = select(self.model).where(self.model.id==current_id)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            if not instance:
                logger.warning(f"❌ Запись с ID {current_id} не найдена")
                return False
            detailed_info = []
            for column in self.model.__table__.columns:
                column_name = column.name
                if column_name not in skip_fields:
                    value = getattr(instance, column_name, None)
                    if value is not None and value != "":
                            detailed_info.append(f"{column_name}: {value}")
            return '\n|'.join(detailed_info)
        except Exception as err:
            logger.error(f"Ошибка при выводе детальной инфы в таблице {self.model.__name__ }по id : {current_id} {err}")
            return False
                        
    def show_model_columns_lst(self)->list[str]:
        '''возвращает столбцы таблицы в виде списка строк'''
        return [col.name for col in self.model.__table__.columns] 

        
    async def exists(self,session:AsyncSession, **params) -> bool:
        """Проверить существование"""
        current_request= select(self.model).filter_by(**params)
        current_object = await session.execute(current_request)
        result = current_object.scalar_one_or_none()
        if result is None:
            logger.warning(f"Объект с параметрами {params} не существует в таюлице {self.model.__name__}")
            return False
        logger.info(f"Объект с параметрами{params} сущесвует в таблице {self.model.__name__}")
        return True
    
        
    async def _validate_model_fields(self, data: Dict[str, Any]) -> None:
        """Проверяет что все переданные поля есть в модели(валидация ключей)"""
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
    
    async def _find_info_by_params(
        self, 
        session: AsyncSession, 
        **searching_params
    ) -> List[Any]:
        '''По указанным параметрам ищет строки таблицы'''
        
        try:
            # 1. Проверка полей
            fields_validation = await self._validate_model_fields(searching_params)
            if not fields_validation:
                logger.warning(f"Невалидные параметры: {searching_params}")
                return []  # Возвращаем пустой список, а не False
            # 2. Строим условия
            conditions = []
            for field, value in searching_params.items():
                current_column = getattr(self.model, field)
                conditions.append(current_column == value)

            # 3. Создаем запрос
            stmt = select(self.model)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # 4. Выполняем
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Ошибка поиска по параметрам {searching_params}: {e}")
            return []