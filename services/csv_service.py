import csv
import os
from typing import List, Dict, Optional
from pathlib import Path

DATA_DIR = Path("data")


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def get_csv_path(filename: str) -> Path:
    return DATA_DIR / filename


def read_csv(filename: str) -> List[Dict]:
    """Lee todos los registros de un CSV y los retorna como lista de dicts."""
    path = get_csv_path(filename)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(filename: str, data: List[Dict], fieldnames: List[str]):
    """Escribe/sobreescribe un CSV con la lista de dicts dada."""
    _ensure_data_dir()
    path = get_csv_path(filename)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def get_next_id(filename: str) -> int:
    """Genera el siguiente ID autoincremental para un CSV."""
    records = read_csv(filename)
    if not records:
        return 1
    ids = [int(r["id"]) for r in records if r.get("id", "").isdigit()]
    return max(ids) + 1 if ids else 1


def find_by_id(filename: str, record_id: int) -> Optional[Dict]:
    """Busca un registro por ID. Retorna None si no existe."""
    records = read_csv(filename)
    for r in records:
        if r.get("id") == str(record_id):
            return r
    return None


def str_to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "sí", "si")
