import os
from base.manager import GraphManager
from base.storage import GraphStorage
from logger_config import logger  # Импорт логгера


def main():
    logger.info("Запуск модуля анализа SQL")
    manager = GraphManager()

    logger.debug("Инициализация интерфейса")
    print("SQL Syntax Corrector and Dependency Analyzer")
    print("-------------------------------------------")

    try:
        # Логирование выбора режима
        choice = (
            input("Would you like to enter SQL code manually? (y/n): ").strip().lower()
        )
        logger.debug(f"Режим ввода: {'ручной' if choice == 'y' else 'директория'}")

        if choice == "y":
            logger.info("Начало ручного ввода SQL")
            print("Enter your SQL code (type 'END' on a new line to finish):")
            sql_lines = []
            while True:
                line = input()
                if line.upper() == "END":
                    break
                sql_lines.append(line)
            sql_code = "\n".join(sql_lines)

            logger.debug("Обработка SQL-кода")
            corrections = manager.process_sql(sql_code)

            if corrections:
                logger.info(f"Внесено исправлений: {len(corrections)}")
                print("\nCorrections made:")
                for i, correction in enumerate(corrections, 1):
                    print(f"{i}. {correction}")
            else:
                logger.debug("SQL не требовал исправлений")

            manager.visualize("Dependencies Graph")

        else:
            directory = input("Enter the directory path containing SQL files: ").strip()
            logger.debug(f"Обработка директории: {directory}")

            choice = (
                input("Display graphs separately for each file? (y/n): ")
                .strip()
                .lower()
            )
            sep_parse = choice == "y"
            logger.debug(
                f"Режим раздельной визуализации: {'включен' if sep_parse else 'выключен'}"
            )

            if sep_parse:
                logger.info("Запуск раздельного парсинга файлов")
                parse_results = manager.parser.parse_directory(
                    directory, sep_parse=True
                )

                for dependencies, corrections, file_path in parse_results:
                    logger.debug(f"Обработка файла: {file_path}")
                    print(f"\nFile: {file_path}")

                    if corrections:
                        logger.info(
                            f"Файл {file_path}: исправлений — {len(corrections)}"
                        )
                        print("Corrections made:")
                        for i, correction in enumerate(corrections, 1):
                            print(f"{i}. {correction}")

                    temp_storage = GraphStorage()
                    temp_storage.add_dependencies(dependencies)
                    manager.visualizer.render(
                        temp_storage,
                        f"Dependencies for {os.path.basename(file_path)}",
                    )
            else:
                logger.info("Запуск пакетной обработки")
                results = manager.process_directory(directory)

                for file_path, corrections in results:
                    logger.debug(f"Обработка файла: {file_path}")
                    print(f"\nFile: {file_path}")

                    if corrections:
                        logger.info(
                            f"Файл {file_path}: исправлений — {len(corrections)}"
                        )
                        print("Corrections made:")
                        for i, correction in enumerate(corrections, 1):
                            print(f"{i}. {correction}")

                manager.visualize("Full Dependencies Graph")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
        print("Произошла ошибка. Подробности в логах.")

    logger.info("Завершение работы модуля")


if __name__ == "__main__":
    main()
