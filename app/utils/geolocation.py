import ssl
import certifi
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from project_logger.loger_configuration import setup_logging

logger = setup_logging()


ctx = ssl.create_default_context(cafile=certifi.where()) #сертиифкат безопасности при обращении к geopy

geolocator = Nominatim(user_agent="Tgshoppingbot", ssl_context=ctx) # Синхронная версия определяет точную геолокацию юзера по запрошенным от него координатам



async def get_user_location(message):
    '''по message  с запрошенной геолокацией от юзера запрашивает инфу о геолокации и возваращает ее в строке, в читаемом виде'''
    async with Nominatim(user_agent='my_tg_bot',adapter_factory=AioHTTPAdapter, timeout=15) as geolocator:
                location = await geolocator.reverse(f"{message.location.latitude}, {message.location.longitude}", exactly_one=True, language='ru')
                logger.info(f"Получена инфа о геолокации : {location}")
                return location.address if location else "адрес не найден"