import shlex

from primitive_db.constants import META_FILE
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def welcome():
    """Выводит приветствие и мини-меню при первом запуске."""
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
    """Выводит справку по командам текущего режима."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _error(parts):
    """Печатает сообщение о некорректных аргументах."""
    print(f"Некорректное значение: {' '.join(parts)}. Попробуйте снова.")


def _handle_create(metadata, args):
    """create_table <name> <col:type> ...

    args — полный список, включая имя команды.
    """
    if len(args) < 2:
        _error(args)
        return metadata
    table_name, *columns = args[1:]
    new_metadata, success = create_table(metadata, table_name, columns)
    if success:
        save_metadata(META_FILE, new_metadata)
    return new_metadata


def _handle_list(metadata, args):
    """list_tables — без аргументов."""
    if len(args) != 1:
        _error(args[1:])
        return metadata
    list_tables(metadata)
    return metadata


def _handle_drop(metadata, args):
    """drop_table <name>."""
    if len(args) != 2:
        _error(args[1:] or ["drop_table"])
        return metadata
    new_metadata, success = drop_table(metadata, args[1])
    if success:
        save_metadata(META_FILE, new_metadata)
    return new_metadata


def _handle_help(metadata, args):
    """help — выводит справку."""
    print_help()
    return metadata


COMMANDS = {
    "create_table": _handle_create,
    "list_tables": _handle_list,
    "drop_table": _handle_drop,
    "help": _handle_help,
}


def _parse_args(user_input):
    """Разбирает строку ввода через shlex (обрабатывает ValueError)."""
    try:
        return shlex.split(user_input)
    except ValueError:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return []


def run():
    """Главный цикл программы."""
    welcome()
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

        args = _parse_args(user_input)
        if not args:
            continue

        command = args[0].lower()

        if command == "exit":
            print("Выход из программы.")
            break

        handler = COMMANDS.get(command)
        if handler is None:
            print(f"Функции {args[0]} нет. Попробуйте снова.")
            continue

        metadata = handler(metadata, args)
