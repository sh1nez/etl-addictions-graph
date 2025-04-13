import logging
import os
import sys

LOG_DIR = "logs"
LOG_FILE = "dependency_analyzer.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Убедимся, что директория для логов существует
os.makedirs(LOG_DIR, exist_ok=True)

# Создание форматтера
formatter = logging.Formatter(
    "[%(levelname)s] %(asctime)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)

# Создание и настройка корневого логгера
logger = logging.getLogger("DependencyAnalyzer")
logger.setLevel(logging.DEBUG)

# Обработчик для stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Обработчик для записи в файл
file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Добавляем обработчики, если их ещё нет
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
