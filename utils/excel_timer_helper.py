import pandas as pd
from datetime import datetime
from typing import Dict
from PyQt6.QtWidgets import QTableWidget, QWidget, QFileDialog, QMessageBox


def update_timer_label(start_time: datetime, label) -> None:

    delta = datetime.now() - start_time
    total = int(delta.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    label.setText(f"Время выполнения работы {h:02d}:{m:02d}:{s:02d}")


def save_tables_to_excel(
    tables: Dict[str, QTableWidget],
    filename: str,
    engine: str = "openpyxl"
) -> None:

    with pd.ExcelWriter(filename, engine=engine) as writer:
        for sheet, table in tables.items():

            headers = [
                table.horizontalHeaderItem(c).text() or ""
                for c in range(table.columnCount())
            ]

            data = []
            for r in range(table.rowCount()):
                row = []
                for c in range(table.columnCount()):
                    item = table.item(r, c)
                    row.append(item.text() if item else "")
                data.append(row)

            pd.DataFrame(data, columns=headers).to_excel(
                writer, sheet_name=sheet, index=False
            )


def export_tables_to_excel(
    parent: QWidget,
    tables: Dict[str, QTableWidget],
    dialog_title: str = "Сохранить",
    file_filter: str = "Excel Files (*.xlsx)"
):

    path, _ = QFileDialog.getSaveFileName(parent, dialog_title, "", file_filter)
    if not path:
        return
    try:
        save_tables_to_excel(tables, path)
    except ImportError:
        QMessageBox.critical(parent, "Ошибка", "Не найден модуль для работы с Excel")
    except Exception as e:
        QMessageBox.critical(parent, "Ошибка", str(e))
    else:
        QMessageBox.information(parent, "Готово", f"Сохранено в {path}")