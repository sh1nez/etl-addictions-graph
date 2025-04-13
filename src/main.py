# main.py (обновленный)
import func.run
import field.run
import table.run
from logger_config import setup_logger


def select_logger_mode():
    print("\n=== Logger Modes ===")
    print("1. Normal (console + file)")
    print("2. Quiet (file only)")
    print("3. Errors only (errors to console + full file)")

    while True:
        choice = input("Select logger mode (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return {"1": "normal", "2": "quiet", "3": "errors_only"}[choice]
        print("Invalid choice. Try again.")


def main():
    # Настройка логгера перед всеми операциями
    logger_mode = select_logger_mode()
    setup_logger(logger_mode)

    # Остальная логика
    print("\n=== Run Mode ===")
    print("1 - table; 2 - field; 3 - functional")
    while True:
        choice = input("Input your mode: ").strip()
        if choice in ("1", "2", "3"):
            {"1": table.run.main, "2": field.run.main, "3": func.run.main}[choice]()
            break
        print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
