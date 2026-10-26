import json
import os
from pathlib import Path

from primitive_db.constants import DATA_DIR


def load_metadata(filepath: str | Path) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_metadata(filepath: str | Path, data: dict) -> None:
    directory = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_table_data(table_name: str, data_dir: str = DATA_DIR) -> list:
    """Загружает данные таблицы из data/<table_name>.json.

    Если файла нет — возвращает пустой список.
    """
    filepath = Path(data_dir) / f"{table_name}.json"
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_table_data(table_name: str, data: list, data_dir: str = DATA_DIR) -> None:
    directory = Path(data_dir)
    directory.mkdir(parents=True, exist_ok=True)
    filepath = directory / f"{table_name}.json"
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def delete_table_data(table_name: str, data_dir: str = DATA_DIR) -> None:
    filepath = Path(data_dir) / f"{table_name}.json"
    if filepath.exists():
        filepath.unlink()
