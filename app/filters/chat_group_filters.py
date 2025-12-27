from aiogram.filters import Filter
from aiogram.types import Message


class GroupFilter(Filter):
    '''фильтр для группы регулирующий режим диалога в группе к основному каналу,
    что бы в групповом чате не было режима меню и прочего, мешающего беседе'''
    
    def __init__(self, chat_types:list[str]):
        self.chat_types = chat_types # список из типов чатов
        
    async def __call__(self, message:Message):
        return message.chat.type in self.chat_types