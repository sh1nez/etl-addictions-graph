# logger_config.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Путь до директории и имени лог-файла (можно переопределить через env)
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "dependency_analyzer.log")
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Создадим папку под логи, если ещё нет
os.makedirs(LOG_DIR, exist_ok=True)

# Единый логгер приложения
logger = logging.getLogger("dependency_graph")
logger.setLevel(logging.DEBUG)
logger.propagate = False  # не подниматься к root


def setup_logger(mode: str = "normal"):
    """
    Перестраивает хендлеры логгера:
      - normal      — console INFO+, file DEBUG+
      - quiet       — no console, file DEBUG+
      - errors_only — console ERROR+, file DEBUG+
    """
    # Удаляем и закрываем все старые хендлеры
    for h in logger.handlers[:]:
        logger.removeHandler(h)
        h.close()

    # Общий форматтер
    fmt = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    # Файловый хендлер с ротацией (всегда DEBUG)
    file_h = RotatingFileHandler(
        LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(formatter)
    logger.addHandler(file_h)

    # Консольный хендлер по режиму
    if mode != "quiet":
        console_h = logging.StreamHandler(sys.stdout)
        console_h.setFormatter(formatter)
        if mode == "errors_only":
            console_h.setLevel(logging.ERROR)
        elif mode == "debug":
            console_h.setLevel(logging.DEBUG)
        else:  # normal
            console_h.setLevel(logging.INFO)
        logger.addHandler(console_h)
