import shlex

from primitive_db.constants import META_FILE
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def welcome():
    print("Первый запуск программы")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        command = input("Введите команду: ")

        if command.lower() == "exit":
            print("Выход из программы...")
            break
        elif command.lower() == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print("Неизвестная команда. Введите 'help' для справки.")




def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Главный цикл программы."""
    print("***База данных***")

    while True:
        metadata = load_metadata(META_FILE)

        try:
            user_input = input(">>>Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из программы.")
            break

        if not user_input.strip():
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0].lower()

        if command == "create_table":
            if len(args) < 2:
                print(f"Некорректное значение: {' '.join(args)}. Попробуйте снова.")
                continue

            table_name = args[1]
            columns = args[2:]
            new_metadata, success = create_table(metadata, table_name, columns)

            if success:
                save_metadata(META_FILE, new_metadata)

        elif command == "list_tables":
            if len(args) != 1:
                print(f"Некорректное значение: {' '.join(args[1:])}. Попробуйте снова.")
                continue
            list_tables(metadata)

        elif command == "drop_table":
            if len(args) != 2:
                bad = " ".join(args[1:]) or "drop_table"
                print(f"Некорректное значение: {bad}. Попробуйте снова.")
                continue

            new_metadata, success = drop_table(metadata, args[1])

            if success:
                save_metadata(META_FILE, new_metadata)

        elif command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print(f"Функции {args[0]} нет. Попробуйте снова.")

