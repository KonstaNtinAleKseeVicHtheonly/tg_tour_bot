from sqlalchemy.ext.asyncio import AsyncSession
#DB
from app.database.db_queries import get_current_tour_query
from app.database.all_models.models import OrderStatus
from aiogram.types import LabeledPrice
#логгепр
from project_logger.loger_configuration import setup_logging


logger = setup_logging()

class OrderPaymentManager:
    '''класс с методами расчета стоимости заказа в телеграм(tg_stars, pay система), в зависимости от типа платежа'''
    DIRECT_PAYMENT = ("tgstars", 'card') # Типы оплаты сразу через tg_stars или по карте
    INDIRECT_PAYMENT = ('cash', 'transfering') # тип оплаты через время на месте или переводом
    DOLLAR_EXCHANGE_RATE = 77 # курс доллара
    RUB_STAR_RATE = 1.66 # рубля за одну звезду 
    BYN_USD_RATE = 3.2 # курс беларусского BYN к доллару
    RUB_BYN_RATE = 28 # рублей 1 одному BYN
    


    def calculate_tg_star_price(self, tour_sum_byn: int) -> int:
        stars_amount_for_rub = tour_sum_byn / self.RUB_STAR_RATE   # количество Stars с учетом русского рубля(курс российский отображается у меня)
        amount_minor = int(stars_amount_for_rub * self.RUB_BYN_RATE)  # количество звезд в беларусских рублях
        return [LabeledPrice(label='XTR', amount=amount_minor)]
   
    def calculate_rub_price(self, tour_sum:int)->LabeledPrice:
        '''из переданной сумы в  рублях расчитывает в рублях для программы
        для оплаты операции'''
        logger.info(f"Пересчет суммы {tour_sum} для оплаты в paymaster")
        amount_minor = int(tour_sum  * 100) * self.RUB_BYN_RATE
        return [LabeledPrice(label='RUB', amount=amount_minor)]# в минимальных единицах (100 = 1 Star), как рубль == 100 копеек
    
    async def _accomplish_successful_transaction(self, session:AsyncSession, order_object,order_data:dict):
        '''порядок дейсвтйи в случае удачной покупки
        изменение в БД и прочее'''
        try:
            transaction_type = order_data.get('payment_type')
            if transaction_type in self.INDIRECT_PAYMENT: # при наличной оплате или переводом
                logger.info(f"Выполнение алгоритма в бд при потенциалльной оплате через {transaction_type} оплату")
                tour_id = order_data.get('tour_id')
                current_tour = await get_current_tour_query(session, tour_id)
                current_tour.booked_seats += order_data['quantity']# изменение забронированных мест в туре
                order_object.status = OrderStatus.PENDING # статус заказа меняем на рассмотрении
                logger.info(f"Изменения  после покупки  заказа :{order_data} в БД произошли успешно")
                return order_object# возвращаем объект созданного заказа
            elif transaction_type in self.DIRECT_PAYMENT:# в остальных случаях схожий алгоритм(при олпате через pay и tg_stars)
                logger.info("Выполнение алгоритма в бд при успешной оплает через tg_stars оплату")
                current_tour = await get_current_tour_query(session, tour_id)
                current_tour.booked_seats += order_data['quantity']# изменение забронированных мест в туре
                order_object.status = OrderStatus.CONFIRMED # статус заказа меняем на подтвержден
                return order_object
            else:
                logger.warning(f"тип заказа не соответсвует ни одному из существуущих : {transaction_type}, проверьте inline callback на соверешение оплаты")
                return False
        except Exception as err:
            logger.error(f"Ошибка при выполнении действий после оплаты заказа : {err}")
            return None

