# logger_config.py
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = "dependency_analyzer.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)
os.makedirs(LOG_DIR, exist_ok=True)

# Создаем глобальный логгер
logger = logging.getLogger("DependencyAnalyzer")


def setup_logger(mode: str = "normal"):
    # Очистка обработчиков
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Форматтер для всех обработчиков
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # Файловый обработчик (всегда DEBUG + ротация)
    file_handler = RotatingFileHandler(
        LOG_PATH,
        mode="a",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
        delay=False,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Консольный обработчик (только для normal/errors режимов)
    if mode != "quiet":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        if mode == "errors_only":
            console_handler.setLevel(logging.ERROR)
        else:
            console_handler.setLevel(logging.DEBUG)

        logger.addHandler(console_handler)

    # Общий уровень логгера (минимальный уровень)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Важно для VS Code!


# Инициализация логгера по умолчанию
setup_logger("normal")
