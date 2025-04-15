import os
from base.manager import GraphManager
from base.storage import GraphStorage


def main():
    manager = GraphManager(column_mode=True)
    print("SQL Syntax Corrector and Dependency Analyzer")
    print("-------------------------------------------")
    choice = input("Would you like to enter SQL code manually? (y/n): ")
    if choice.lower() == "y":
        print("Enter your SQL code (type 'END' on a new line to finish):")
        sql_lines = []
        while True:
            line = input()
            if line.upper() == "END":
                break
            sql_lines.append(line)
        sql_code = "\n".join(sql_lines)
        corrections = manager.process_sql(sql_code)
        if corrections:
            print("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction}")
    else:
        directory = input("Enter the directory path containing SQL files: ")
        choice = input("Display graphs separately for each file? (y/n): ")
        if choice.lower() == "y":
            parse_results = manager.parser.parse_directory(directory, sep_parse=True)
            for dependencies, corrections, file_path in parse_results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
        else:
            results = manager.process_directory(directory)
            for file_path, corrections in results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")


if __name__ == "__main__":
    main()
