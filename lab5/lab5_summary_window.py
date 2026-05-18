# lab5/lab5_summary_window.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt

from lab5.sub131_window import Sub131Window
from lab5.sub132_window import Sub132Window
from lab5.sub133_window import Sub133Window
from lab5.sub231_window import Sub231Window
from lab5.sub232_window import Sub232Window
from lab5.sub233_window import Sub233Window
from lab5.sub234_window import Sub234Window
from lab5.sub235_window import Sub235Window
from utils.excel_timer_helper import export_tables_to_excel


# Соответствие вкладок: (название вкладки, класс, название листа Excel)
TABS = [
    ("1.3.1  Хар-ка ОУ",     Sub131Window, "1.3.1 Хар-ка ОУ"),
    ("1.3.2  Umax(I)",        Sub132Window, "1.3.2 Umax(I)"),
    ("1.3.3  Uсм",            Sub133Window, "1.3.3 Uсм"),
    ("2.3.1  Ku(R4) НУ",      Sub231Window, "2.3.1 Ku(R4) НУ"),
    ("2.3.2  Хар-ка НУ",      Sub232Window, "2.3.2 Хар-ка НУ"),
    ("2.3.3  Повторитель",     Sub233Window, "2.3.3 Повторитель"),
    ("2.3.4  Хар-ка ИУ",      Sub234Window, "2.3.4 Хар-ка ИУ"),
    ("2.3.5  ИУ перем. ток",  Sub235Window, "2.3.5 ИУ AC"),
]


class Lab5SummaryWindow(QWidget):
    """
    Сводное окно Лабораторной работы №5.
    Каждый подпункт — отдельная вкладка.
    Все вкладки разделяют единый controller, поэтому данные,
    введённые в любом подокне, видны и здесь.
    Кнопка «Экспорт всего» сохраняет все таблицы в один .xlsx.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Лабораторная работа")

        self.tabs = QTabWidget()
        self.sub_windows: list[QWidget] = []

        for tab_title, WinClass, _ in TABS:
            win = WinClass(controller)
            self.sub_windows.append(win)
            self.tabs.addTab(win, tab_title)

        # Кнопка экспорта всех таблиц в один файл
        btn_export_all = QPushButton("📥  Экспортировать все таблицы в один Excel")
        btn_export_all.setMinimumHeight(40)
        btn_export_all.clicked.connect(self._export_all)

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.close)

        header = QLabel(
            "<b>Лабораторная работа</b>"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 13px; padding: 6px;")

        btn_hl = QHBoxLayout()
        btn_hl.addWidget(btn_export_all)
        btn_hl.addWidget(btn_close)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.tabs)
        layout.addLayout(btn_hl)
        self.setLayout(layout)

    def _export_all(self):
        """Собирает таблицы из всех подокон и сохраняет в один .xlsx."""
        tables_dict = {}
        for win, (_, _, sheet_name) in zip(self.sub_windows, TABS):
            # У каждого подокна есть атрибут .table (PasteTableWidget)
            if hasattr(win, "table"):
                tables_dict[sheet_name] = win.table

        if not tables_dict:
            return

        export_tables_to_excel(
            self,
            tables_dict,
            dialog_title="Сохранить все данные Лаб. №5",
            file_filter="Excel Files (*.xlsx)"
        )