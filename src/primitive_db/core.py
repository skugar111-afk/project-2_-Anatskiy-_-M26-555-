from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data, save_table_data


def _parse_column(spec):
    """Разбирает спецификацию колонки вида 'имя:тип'."""
    if ":" not in spec:
        raise ValueError(spec)
    name, type_ = spec.split(":", 1)
    name, type_ = name.strip(), type_.strip().lower()
    if not name or type_ not in VALID_TYPES:
        raise ValueError(spec)
    return name, type_


def _check_type(value, expected):
    """Проверяет, что значение соответствует ожидаемому типу колонки."""
    if expected == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "bool":
        return isinstance(value, bool)
    if expected == "str":
        return isinstance(value, str)
    return False


def _coerce(value, expected):
    """Приводит строковое значение к ожидаемому типу.

    Возвращает (успех, приведённое_значение).
    """
    if expected == "int" and isinstance(value, str):
        try:
            return True, int(value)
        except ValueError:
            return False, value
    if expected == "bool" and isinstance(value, str):
        lowered = value.lower()
        if lowered in ("true", "false"):
            return True, lowered == "true"
        return False, value
    return True, value


def _match(row, where_clause):
    """Проверяет, что строка удовлетворяет условиям выборки."""
    return all(row.get(key) == value for key, value in where_clause.items())


# ============================================================
#  Управление таблицами
# ============================================================


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу. Возвращает (metadata, success)."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata, False

    parsed = []
    for spec in columns:
        name, type_ = _parse_column(spec)  # ValueError перехватит декоратор
        parsed.append({"name": name, "type": type_})

    id_column = {"name": "ID", "type": "int"}
    rest = [c for c in parsed if c["name"].lower() != "id"]
    final_columns = [id_column] + rest

    metadata[table_name] = {"columns": final_columns}
    columns_str = ", ".join(f"{c['name']}:{c['type']}" for c in final_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata, True


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу. Возвращает (metadata, success)."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata, False
    del metadata[table_name]  # KeyError перехватит декоратор (на всякий случай)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata, True


def list_tables(metadata):
    """Выводит список таблиц. Возвращает (metadata, True)."""
    if not metadata:
        print("Таблиц нет.")
        return metadata, True
    for table_name in metadata:
        print(f"- {table_name}")
    return metadata, True


# ============================================================
#  CRUD
# ============================================================


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Вставляет запись в таблицу. Возвращает (table_data, success)."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return [], False

    schema = metadata[table_name]["columns"]
    expected = len(schema) - 1

    if len(values) != expected:
        print(f"Ошибка: Ожидалось {expected} значений, получено {len(values)}.")
        return load_table_data(table_name), False

    record = {}
    for column, raw in zip(schema[1:], values):
        ok, value = _coerce(raw, column["type"])
        if not ok or not _check_type(value, column["type"]):
            print(f"Некорректное значение: {raw}. Ожидался тип {column['type']}.")
            return load_table_data(table_name), False
        record[column["name"]] = value

    table_data = load_table_data(table_name)
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    record = {"ID": new_id, **record}

    table_data.append(record)
    save_table_data(table_name, table_data)
    print(f'Запись успешно добавлена в таблицу "{table_name}".')
    return table_data, True


# Кэшер на модульном уровне — один на весь процесс
_select_cache = create_cacher()


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает строки по условию. Возвращает (rows, True)."""
    key = (tuple(sorted((where_clause or {}).items())), len(table_data))
    rows = _select_cache(
        key,
        lambda: _select_impl(table_data, where_clause),
    )
    return rows, True


def _select_impl(table_data, where_clause=None):
    """Внутренняя реализация выборки (без обёртки контракта)."""
    if where_clause is None:
        return list(table_data)
    return [row for row in table_data if _match(row, where_clause)]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет строки по условию. Возвращает (table_data, True)."""
    updated = 0
    for row in table_data:
        if _match(row, where_clause):
            row.update(set_clause)
            updated += 1
    print(f"Обновлено записей: {updated}.")
    return table_data, True


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Удаляет строки по условию. Возвращает (remaining, True)."""
    remaining = [row for row in table_data if not _match(row, where_clause)]
    removed = len(table_data) - len(remaining)
    print(f"Удалено записей: {removed}.")
    return remaining, True

































































































































