from aiogram.fsm.state import State, StatesGroup

class ChatMode(StatesGroup):
    waiting = State()
class NewsLetter(StatesGroup):
    '''класс, Отвечающий за рассылку новостей'''
    ...
    
class NewOrder(StatesGroup):
    '''FSM для создания заказа(покупки тура)'''
    
    select_tour = State()
    select_place_number = State()
    