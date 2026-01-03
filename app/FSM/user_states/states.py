from aiogram.fsm.state import State, StatesGroup

class ChatMode(StatesGroup):
    waiting = State()
class NewsLetter(StatesGroup):
    '''класс, Отвечающий за рассылку новостей'''
    ...
    
    
