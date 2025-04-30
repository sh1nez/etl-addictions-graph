import sys
import logging
from logging import StreamHandler, FileHandler

import field.run
import func.run
import table.run
from util.cli import parse_arguments
from logger_config import logger, setup_logger


def configure_logging(mode: str, log_file: str = None):  # перенести по умолчанию
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


def main():
    # 1) выбор режима логирования
    setup_logger()

    # 4) собираем argv для parse_arguments
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
