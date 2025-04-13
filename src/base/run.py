import os
from base.manager import GraphManager
from base.storage import GraphStorage
from logger_config import logger


def main():
    logger.info("Приложение запущено.")
    manager = GraphManager()

    print("SQL Syntax Corrector and Dependency Analyzer")
    print("-------------------------------------------")

    choice = input("Would you like to enter SQL code manually? (y/n): ").strip().lower()
    logger.debug(f"Режим ввода: {'ручной' if choice == 'y' else 'директория'}")

    if choice == "y":
        print("Enter your SQL code (type 'END' on a new line to finish):")
        sql_lines = []
        while True:
            line = input()
            if line.upper() == "END":
                break
            sql_lines.append(line)

        sql_code = "\n".join(sql_lines)
        logger.debug("Получен SQL-код от пользователя.")

        try:
            corrections = manager.process_sql(sql_code)
            if corrections:
                print("\nCorrections made:")
                for i, correction in enumerate(corrections, 1):
                    print(f"{i}. {correction}")
                logger.info(f"Внесено исправлений: {len(corrections)}")
            manager.visualize("Dependencies Graph")
        except Exception as e:
            logger.error(f"Ошибка при обработке SQL: {e}")

    else:
        directory = input("Enter the directory path containing SQL files: ").strip()
        logger.debug(f"Указана директория: {directory}")

        choice = (
            input("Display graphs separately for each file? (y/n): ").strip().lower()
        )
        separate = choice == "y"
        logger.debug(f"Отображать графы отдельно: {separate}")

        try:
            if separate:
                parse_results = manager.parser.parse_directory(
                    directory, sep_parse=True
                )
                for dependencies, corrections, file_path in parse_results:
                    print(f"\nFile: {file_path}")
                    if corrections:
                        print("Corrections made:")
                        for i, correction in enumerate(corrections, 1):
                            print(f"{i}. {correction}")
                        logger.info(
                            f"{file_path}: Внесено исправлений — {len(corrections)}"
                        )

                    temp_storage = GraphStorage()
                    temp_storage.add_dependencies(dependencies)
                    manager.visualizer.render(
                        temp_storage,
                        f"Dependencies for {os.path.basename(file_path)}",
                    )
            else:
                results = manager.process_directory(directory)
                for file_path, corrections in results:
                    print(f"\nFile: {file_path}")
                    if corrections:
                        print("Corrections made:")
                        for i, correction in enumerate(corrections, 1):
                            print(f"{i}. {correction}")
                        logger.info(
                            f"{file_path}: Внесено исправлений — {len(corrections)}"
                        )
                manager.visualize("Full Dependencies Graph")
        except Exception as e:
            logger.error(f"Ошибка при обработке файлов в директории: {e}")

    logger.info("Завершение работы программы.")


if __name__ == "__main__":
    main()
