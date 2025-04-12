import os
from request_counter import read_sql_queries, plot_query_frequencies


def process_file(to_file_path):
    # Ваша логика обработки файла
    qwery_plot = read_sql_queries(to_file_path)
    plot_query_frequencies(qwery_plot)

    print(f"Processing file: {to_file_path}")


def scan_and_process_folder(folder_path):
    # Получаем список всех файлов в папке
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Проверяем расширение файла
            if file.endswith(".sql") or file.endswith(".ddl"):
                file_path = os.path.join(root, file)
                # Обрабатываем файл
                process_file(file_path)


# Пример использования
folder_path = "./ddl"  # Укажите путь к вашей папке
scan_and_process_folder(folder_path)
