# utils/session_store.py
import json
from pathlib import Path
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

_SESSION_FILE = Path(__file__).resolve().parent.parent / "session_data.json"
_cache: dict = {}
_loaded = False


def _ensure_loaded():
    global _cache, _loaded
    if _loaded:
        return
    _loaded = True
    if _SESSION_FILE.exists():
        try:
            _cache = json.loads(_SESSION_FILE.read_text(encoding="utf-8"))
        except Exception:
            _cache = {}


def _flush():
    try:
        _SESSION_FILE.write_text(
            json.dumps(_cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


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
    table.blockSignals(False)


def get_all_for_prefix(prefix: str) -> dict:
    _ensure_loaded()
    return {k: v for k, v in _cache.items() if k.startswith(prefix)}