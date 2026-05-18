# lab18/sub_base18.py
import traceback
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, QTimer
import utils.session_store as ss
from utils.stand_controller import StandController


class Lab18SubBase(QWidget):
    def __init__(self, session_key: str, parent=None):
        super().__init__(parent)
        self._session_key = session_key
        self._updating    = False
        self.stand = StandController()

    # ====================== ФОРМАТИРОВАНИЕ ЧИСЕЛ ======================

    def _format_number(self, value, decimals: int = 2) -> str:
        """Автоматическое округление до указанного количества знаков после запятой"""
        if value is None:
            return ""
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    # ====================== УТИЛИТЫ ТАБЛИЦЫ ======================

    def _set_fixed(self, row: int, col: int, value):
        """Устанавливает фиксированное значение с округлением до сотых"""
        text = self._format_number(value, decimals=2)
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, col, item)

    def _set_calc(self, row: int, col: int, value):
        """Устанавливает рассчитанное значение с округлением до сотых"""
        text = self._format_number(value, decimals=2)
        item = QTableWidgetItem(text)
        self.table.setItem(row, col, item)

    def _get_float(self, row: int, col: int):
        """Получение числа из ячейки"""
        item = self.table.item(row, col)
        if not item:
            return None
        try:
            return float(item.text().strip().replace(",", "."))
        except ValueError:
            return None

    # ====================== ПЕРЕСЧЁТ ======================

    def _safe_recalculate(self):
        if self._updating:
            return
        self._updating = True
        try:
            self._do_recalculate()
        except Exception:
            traceback.print_exc()
        finally:
            self._updating = False

    def _do_recalculate(self):
        pass

    # ====================== СОХРАНЕНИЕ / ЗАГРУЗКА ======================

    def _load_session(self):
        ss.load_table(self._session_key, self.table)
        QTimer.singleShot(150, self._safe_recalculate)

    def closeEvent(self, event):
        ss.save_table(self._session_key, self.table,
                      sheet_name=self.windowTitle())
        super().closeEvent(event)