import func.run
import field.run
import table.run


def main():
    print("Run mode: (1 - table; 2 - field; 3 - functional)")
    while True:
        choice = input("Input your mode: ")
        if choice == "1":
            table.run.main()
        elif choice == "2":
            field.run.main()
        elif choice == "3":
            func.run.main()
        else:
            continue
        break


if name == "main":
    main()