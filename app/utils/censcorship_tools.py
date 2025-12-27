import aiofiles
from aiogram.types import Message
from project_logger.loger_configuration import setup_logging

from string import punctuation



logger = setup_logging()


path_to_censcorship_file = r"D:\vsc\projects\TG_BOTS\tg_rb_guider\censorship_words.txt"



async def get_banned_words(path_to_file)->set:
    '''корутина для асинхронного откртыия файла с запрещенными словами и возвращения их как множества'''
    
    async with aiofiles.open(path_to_file,'r',encoding='utf-8') as file:
        banned_words_raw = await file.read()
    banned_words_final = {word.lower().strip() for word in banned_words_raw.split(',')}
    return banned_words_final

def clear_text(message_from_user:str):
    '''доп проверка текста на случай замасикрованных запрещенный слов: н!гер например'''
    return message_from_user.translate(str.maketrans('', '', punctuation))

async def check_banned_words(user_message:Message)->bool:
    '''Проверяет сообщения от юзеров на наличеие матерных слов 
    если таковы присутсвуют то вернет True иначе False'''
    try:
        logger.info(f"проверка сообщения от юзера {user_message.from_user.username} на цензуру")
        banned_words = await get_banned_words(path_to_censcorship_file)
        user_words = clear_text(user_message.text.lower()).split()# выводим скртые запрещенные слова
        if banned_words.intersection(user_words):
            logger.info("присустсвует запрещенное слово")
            return True
        logger.info("ЗАпрещеннных слов не выявлено")
        return False
    except Exception as err:
        logger.warning(f"Ошибка при првоерки слов на цензуру : {err}")