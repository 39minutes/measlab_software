# lab5/sub_base.py
import traceback
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
import utils.session_store as ss
from utils.stand_controller import StandController


class Lab5SubBase(QWidget):
    """
    Базовый класс всех подокон Лаб. 5.
    Теперь с автоматическим расширением окна под таблицу.
    """

    def __init__(self, session_key: str, parent=None):
        super().__init__(parent)
        self._session_key = session_key
        self.stand = StandController()
        self._updating = False

        # ← НОВОЕ: таблица будет растягиваться и влиять на размер окна
        self.table: 'PasteTableWidget' = None  # будет задаваться в дочерних классах

    # ── Автоматическое расширение окна ───────────────────────────────
    def _auto_resize_window(self):
        """Подгоняет размер таблицы и всего окна под содержимое"""
        if not hasattr(self, 'table') or self.table is None:
            return

        # Растягиваем столбцы и строки под данные
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        # Даём layout'у пересчитаться
        QTimer.singleShot(10, self._final_adjust)

    def _final_adjust(self):
        """Финальная подгонка размера окна"""
        # Минимальный размер окна = размер таблицы + отступы + заголовок
        hint = self.sizeHint()
        # Добавляем небольшой запас (заголовок окна, кнопки и т.д.)
        new_width = max(hint.width() + 40, 600)   # минимум 600 px по ширине
        new_height = max(hint.height() + 80, 300) # минимум 300 px по высоте

        self.resize(new_width, new_height)
        # Можно сделать окно ещё больше, если данных очень много:
        # self.setMinimumSize(new_width, new_height)

    # ── Остальные методы (без изменений) ─────────────────────────────
    def _format_number(self, value, decimals: int = 2) -> str:
        if value is None:
            return ""
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    def _set_fixed(self, row: int, col: int, value):
        text = self._format_number(value, decimals=2)
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, col, item)

    def _set_calc(self, row: int, col: int, value):
        text = self._format_number(value, decimals=2)
        item = QTableWidgetItem(text)
        self.table.setItem(row, col, item)

    def _get_float(self, row: int, col: int):
        item = self.table.item(row, col)
        if not item:
            return None
        text = item.text().strip().replace(",", ".")
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _safe_recalculate(self):
        if self._updating:
            return
        self._updating = True
        try:
            self._do_recalculate()
            self._auto_resize_window()          # ← НОВОЕ: пересчёт после изменений
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
        # ←←← НОВОЕ: закрываем COM-порт при закрытии подокна
        if (hasattr(self, 'stand') and
                self.stand and
                self.stand.ser and
                getattr(self.stand.ser, 'is_open', False)):
            try:
                self.stand.ser.close()
                self.stand.ser = None  # чтобы следующий StandController мог открыть заново
            except Exception:
                pass  # не ломаем закрытие окна, если что-то пошло не так

        # Сохраняем данные таблицы (как было раньше)
        ss.save_table(self._session_key, self.table,
                      sheet_name=self.windowTitle())
        super().closeEvent(event)

    # ← НОВОЕ: автоматически подгоняем размер при первом показе окна
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self._auto_resize_window)