from aiogram.fsm.state import State, StatesGroup
    
    
    
    
class AdminTourMode(StatesGroup):
    '''FSM класс для CRUD операций с туром'''
    # === СОЗДАНИЕ ТОВАРА ===
    create_name = State()
    create_description = State()
    create_price = State()
    create_photo = State()
    set_max_people = State()
    set_booked_places = State()
    set_duration = State()
    set_category = State()
    set_meeting_point = State()
    
    
    # === РЕДАКТИРОВАНИЕ ТОВАРА ===
    set_param_for_change = State()        # Выбор поля для редактирования
    set_new_value = State()
    
    # === УДАЛЕНИЕ ТОВАРА ===
    delete_select_product = State()
    delete_confirm = State()
    
    # промежуточное состояние дя избежания прерывания операций
    waiting = State()
    texts = {
        'AdminMode:create_name' : 'Введите имя заново',
        'AdminMode:create_description' : 'Введите описание заново',
        'AdminMode:create_price' : 'Введите цену заново',
        'AdminMode:create_photo' : 'Отправьте фото заново',

    }
    
class AdminLandMarkMode(StatesGroup):
    '''FSM класс для CRUD операций с достопримечательностями'''
    # === СОЗДАНИЕ ТОВАРА ===
    create_name = State()
    create_description = State()
    create_url = State()
    create_photo = State()
    create_confirm = State()
    
    # === РЕДАКТИРОВАНИЕ ТОВАРА ===
    edit_select_lm = State()      # Выбор товара для редактирования
    set_param_for_change = State()        # Выбор поля для редактирования
    set_new_value = State()
    # === УДАЛЕНИЕ ТОВАРА ===
    delete_select_lm = State()
    delete_confirm = State()
    
    # промежуточное состояние дя избежания прерывания операций
    waiting = State()
    texts = {
        'AdminMode:create_name' : 'Введите имя заново',
        'AdminMode:create_description' : 'Введите описание заново',
        'AdminMode:create_price' : 'Введите цену заново',
        'AdminMode:create_photo' : 'Отправьте фото заново',

    }
    
    
class Admin_LM_Tour_Bound_Mode(StatesGroup):
    '''FSM класс для CRUD операций с ассоциативной таблицей'''
    # === СОЗДАНИЕ ТОВАРА ===
    set_tour_id = State()
    set_lm_id = State()
    current_bound = State()
    change_tour_bound = State()
    change_lm_bound = State()
    
    # === РЕДАКТИРОВАНИЕ ТОВАРА ===
    edit_select_lm = State()      # Выбор товара для редактирования
    edit_choose_field = State()        # Выбор поля для редактирования
    edit_name = State()
    edit_description = State()
    edit_url = State()
    edit_photo = State()
    edit_confirm = State()
    
    # === УДАЛЕНИЕ ТОВАРА ===
    delete_select_lm = State()
    delete_confirm = State()
    
    # промежуточное состояние дя избежания прерывания операций
    waiting = State()
    texts = {
        'AdminMode:create_name' : 'Введите имя заново',
        'AdminMode:create_description' : 'Введите описание заново',
        'AdminMode:create_price' : 'Введите цену заново',
        'AdminMode:create_photo' : 'Отправьте фото заново',

    }
class ChatMode(StatesGroup):
    waiting = State()
    
class AdminBannerMode(StatesGroup):
    '''FSM класс для CRUD операций с банерами'''
    # === СОЗДАНИЕ ТОВАРА ===
    create_name = State()
    create_img = State() # ссылка на url баннера
    create_description = State()
    #
    waiting = State()

class AdminUsersMode(StatesGroup):
    '''FSM класс для CRUD операций с юзерами бота(зарегестрированными)'''
    # === СОЗДАНИЕ ТОВАРА ===
    #
    waiting = State()

class AdminOrderMode(StatesGroup):
    '''FSM класс для CRUD операций с заказами юзера'''
    waiting = State()
    # изменение текущего заказа
    edit_choose_field = State()# Для выбора поля под изменение
    edit_new_value = State()# новое значение в указанное поле
    