import os
import logging
from pathlib import Path

def setup_logging():
    """
    Простая настройка логирования - всегда создает файл в поддиректории logger
    относительно места запуска или файла с кодом.
    """
    # Вариант A: Логи в папке logger относительно текущей рабочей директории
    log_dir = Path("project_logger")# название папки с логером
    log_file = log_dir / "logs_history.log"
    
    # # Вариант B: Логи в папке logger относительно файла с этой функцией
    # current_file = Path(__file__).parent  # директория этого файла
    # log_dir = current_file / "logger"
    # log_file = log_dir / "logs_history.log"
    
    # Вариант C: Логи рядом с местом запуска (самый простой)
    # log_file = Path("app.log")
    
    # Создаем директорию
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем файл
    if not log_file.exists():
        log_file.touch()
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file), encoding='utf-8')
        ]
    )
    
    return logging.getLogger(__name__)