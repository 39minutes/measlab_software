import json
import sys
from pathlib import Path

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


# ============================================================
# Правильное определение пути к файлу (работает и в .exe, и при разработке)
# ============================================================
def get_base_path() -> Path:
    if getattr(sys, 'frozen', False):
        # Запущено как собранный .exe
        return Path(sys.executable).parent
    else:
        # Запущено из исходников Python
        return Path(__file__).parent.parent


BASE_PATH = get_base_path()
JSON_FILE = BASE_PATH / "session_data.json"

_cache: dict = {}


def _ensure_loaded():
    """Загружает данные из JSON-файла (если он существует)"""
    global _cache
    if _cache:          # уже загружено
        return

    if JSON_FILE.exists():
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}
    else:
        _cache = {}


def _flush():
    """Сохраняет данные в JSON-файл"""
    try:
        JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
        JSON_FILE.write_text(
            json.dumps(_cache, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"[session_store] Ошибка сохранения: {e}")


# ============================================================
# Основные функции
# ============================================================

def save_table(key: str, table: QTableWidget, sheet_name: str = ""):
    _ensure_loaded()

    headers = [
        (table.horizontalHeaderItem(c).text()
         if table.horizontalHeaderItem(c) else f"Col{c + 1}")
        for c in range(table.columnCount())
    ]

    rows = [
        [
            (table.item(r, c).text() if table.item(r, c) else "")
            for c in range(table.columnCount())
        ]
        for r in range(table.rowCount())
    ]

    _cache[key] = {
        "sheet_name": (sheet_name or key)[:31],
        "headers": headers,
        "rows": rows,
    }
    _flush()


def load_table(key: str, table: QTableWidget):
    _ensure_loaded()
    entry = _cache.get(key)
    if not entry:
        return

    table.blockSignals(True)
    try:
        for r, row_data in enumerate(entry.get("rows", [])):
            if r >= table.rowCount():
                break
            for c, text in enumerate(row_data):
                if c >= table.columnCount():
                    break
                if not text:
                    continue
                item = table.item(r, c)
                if item:
                    item.setText(text)
                else:
                    table.setItem(r, c, QTableWidgetItem(text))
    finally:
        table.blockSignals(False)


def get_all_for_prefix(prefix: str) -> dict:
    _ensure_loaded()
    return {k: v for k, v in _cache.items() if k.startswith(prefix)}