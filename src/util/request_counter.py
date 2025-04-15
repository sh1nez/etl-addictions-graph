import re
from collections import Counter


class SQLCommandAnalyzer:
    """Class for analyzing SQL commands in a file."""

    def __init__(self, file_path):
        self.file_path = file_path

    def analyze(self):
        # Read the file content
        with open(self.file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Define SQL commands to search for
        sql_commands = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
            "TRUNCATE",
            "MERGE",
            "CALL",
            "EXPLAIN",
            "GRANT",
            "REVOKE",
        ]

        # Create a regex pattern to find all commands
        pattern = r"\b(?:" + "|".join(sql_commands) + r")\b"

        # Find all matches in the content
        matches = re.findall(pattern, content, re.IGNORECASE)

        # Count the occurrences of each command
        command_counts = Counter(matches)

        return command_counts


def get_analiz(file_path):
    # Example usage
    analiz_list = []
    statistics = SQLCommandAnalyzer(file_path).analyze()

    for a, b in statistics.items():
        analiz_list.append(f"{a} {b}")

    print("SQL Command Usage Statistics:")
    for command, count in statistics.items():
        print(f"{command}: {count}")

    # Возвращаем словарь с толщинами линий
    edge_widths = {
        command: count / 10 for command, count in statistics.items()
    }  # Пример: делим на 10 для масштабирования
    return analiz_list, edge_widths


if __name__ == "__main__":
    # Example usage
    file_path = "./ddl/Pigeon_etl.sql"  # Replace with your file path
    analyzer = SQLCommandAnalyzer(file_path)
    statistics = analyzer.analyze()

    print("SQL Command Usage Statistics:")
    for command, count in statistics.items():
        print(f"{command}: {count}")

    print()
    print(get_analiz(file_path))
