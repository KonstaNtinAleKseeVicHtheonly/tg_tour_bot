from app.database.db_configurations.db_engine import async_session
import functools

def set_session_connection(func):
    @functools.wraps(func)
    async def wrapper(*args,**kwargs):
        """автоматические открывает сессию"""
        async with async_session() as session:
            return await func(session,*args, **kwargs)    
    return wrapper
        