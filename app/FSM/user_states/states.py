from aiogram.fsm.state import State, StatesGroup

class ChatMode(StatesGroup):
    waiting = State()
class NewsLetter(StatesGroup):
    '''класс, Отвечающий за рассылку новостей'''
    ...
    
    
class AdminMode(StatesGroup):
    '''промежуточное состояние, дающее опред полномочия админам в группе если их id есть в env'''
    is_admin = State()