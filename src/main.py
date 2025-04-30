import sys
import logging
from logging import StreamHandler, FileHandler

import field.run
import func.run
import table.run
from util.cli import parse_arguments
from logger_config import logger, setup_logger


def configure_logging(mode: str, log_file: str = None):
    """
    Configure the global logger based on the selected mode:
      - normal: console INFO+, file DEBUG+ (if file handler present)
      - quiet: no console output, file DEBUG+
      - error: console ERROR+, file DEBUG+
    """
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler for quiet or error, or if explicit log_file
    if log_file or mode in ("quiet", "error"):
        log_path = log_file or "app.log"
        if not any(isinstance(h, FileHandler) for h in logger.handlers):
            fh = FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            logger.debug(f"FileHandler added, logging to {log_path}")

    # Adjust console handlers
    for handler in list(logger.handlers):
        if isinstance(handler, StreamHandler):
            if mode == "quiet":
                logger.debug("Removing console handler for quiet mode")
                logger.removeHandler(handler)
            elif mode == "error":
                handler.setLevel(logging.ERROR)
                logger.debug("Console handler set to ERROR level")
            else:  # normal
                handler.setLevel(logging.INFO)
                logger.debug("Console handler set to INFO level")


def select_logger_mode() -> str:
    print("Выберите режим логгирования:")
    print("  1) Обычный       — console INFO+, file DEBUG+")
    print("  2) Тихий         — вывод только в файл DEBUG+")
    print("  3) Отладочный    — console ERROR+, file DEBUG+")
    choice = input("Введите цифру [1-3]: ").strip()
    mapping = {"1": "normal", "2": "quiet", "3": "error"}
    if choice not in mapping:
        print(f"Неверный выбор: {choice}")
        sys.exit(1)
    return mapping[choice]


def select_program_mode() -> str:
    print("\nВыберите режим работы программы:")
    print("  1) Table      (табличный режим)")
    print("  2) Field      (полевая обработка)")
    print("  3) Functional (функциональный режим)")
    choice = input("Введите цифру [1-3]: ").strip()
    mapping = {"1": "table", "2": "field", "3": "functional"}
    if choice not in mapping:
        print(f"Неверный выбор режима программы: {choice}")
        sys.exit(1)
    return mapping[choice]


def select_input_method() -> str:
    print("\nВыберите источник SQL:")
    print("  1) Директория (.ddl файлы)")
    print("  2) Ввод SQL-кода")
    choice = input("Введите цифру [1-2]: ").strip()
    mapping = {"1": "dir", "2": "sql"}
    if choice not in mapping:
        print(f"Неверный выбор: {choice}")
        sys.exit(1)
    return mapping[choice]


def main():
    # 1) выбор режима логирования
    mode = select_logger_mode()  # normal, quiet или errors_onlyё
    setup_logger(mode)

    # 2) выбор режима работы программы
    prog_mode = select_program_mode()

    # 3) выбор источника SQL-кода или директории
    input_method = select_input_method()

    # 4) собираем argv для parse_arguments
    new_argv = [sys.argv[0], "--mode", prog_mode]
    if input_method == "dir":
        directory = input("Введите путь к директории: ").strip()
        new_argv += ["--directory_path", directory]
        sep = input("Отдельный граф для каждого файла? (true/false): ").strip().lower()
        if sep not in ("true", "false"):
            print(f"Неверное значение separate_graph: {sep}")
            sys.exit(1)
        new_argv += ["--separate_graph", sep]
    else:
        sql_code = input("Введите SQL-код (в кавычках или без): ").strip()
        new_argv += ["--sql_code", sql_code]

    # 5) перезаписываем sys.argv и парсим
    sys.argv = new_argv
    args = parse_arguments()

    # 6) делегируем выполнение
    if args.mode == "table":
        table.run.process_args(args)
    elif args.mode == "field":
        field.run.process_args(args)
    elif args.mode == "functional":
        func.run.process_args(args)
    else:
        logger.error(f"Неизвестный режим программы: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
