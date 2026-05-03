# lab16_17/sub_base1617.py
import traceback
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, QTimer
import utils.session_store as ss
from utils.stand_controller import StandController


class Lab1617SubBase(QWidget):
    def __init__(self, session_key: str, parent=None):
        super().__init__(parent)
        self._session_key = session_key
        self._updating    = False
        self.stand = StandController()

    def _set_fixed(self, row: int, col: int, text: str):
        item = QTableWidgetItem(str(text))
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, col, item)

    def _set_calc(self, row: int, col: int, text: str):
        self._set_fixed(row, col, text)

    def _get_float(self, row: int, col: int):
        item = self.table.item(row, col)
        if not item:
            return None
        try:
            return float(item.text().strip().replace(",", "."))
        except ValueError:
            return None

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

    def _load_session(self):
        ss.load_table(self._session_key, self.table)
        QTimer.singleShot(150, self._safe_recalculate)

    def closeEvent(self, event):
        ss.save_table(self._session_key, self.table,
                      sheet_name=self.windowTitle())
        super().closeEvent(event)