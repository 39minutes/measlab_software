# lab5/sub133_window.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from utils.tables.read_voltage_button import ReadVoltageButton   # ← добавлено


R4_ROWS      = [200, 100]
COL_R4       = 0
COL_UOUT     = 1
COL_USM      = 2
COL_USM_AVG  = 3

HEADERS = ["R4, кОм", "Uвых, мВ", "Uсм, мВ", "Uсм ср, мВ"]


class Sub133Window(Lab5SubBase):
    def __init__(self, parent=None):
        super().__init__("lab5_1.3.3", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("Измерение значения напряжения смещения операционного усилителя")
        self.resize(620, 280)

        self.table = PasteTableWidget(2, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        for i, r4 in enumerate(R4_ROWS):
            self._set_fixed(i, COL_R4, str(r4))

        self._set_fixed(0, COL_USM_AVG, "")
        self._set_fixed(1, COL_USM_AVG, "")

        self.table.setSpan(0, COL_USM_AVG, 2, 1)

        avg_item = QTableWidgetItem("")
        avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, COL_USM_AVG, avg_item)

        # Кнопка считывания Uвых со стенда (возвращена)
        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._fill_selected_uout,
            label_text="Uвых, мВ:"
        )

        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.5 Uсм": self.table})
        )

        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица</b> Напряжение смещения ОУ<br>"
            "U<sub>см</sub> вводится вручную. В последнем столбце — среднее значение U<sub>см</sub></small>"
        ))
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)          # ← кнопка возвращена
        layout.addWidget(btn_save)
        layout.addStretch()
        layout.addWidget(self.timer_label)
        layout.addWidget(btn_exit)

        timer = QTimer(self)
        timer.timeout.connect(
            lambda: update_timer_label(self.start_time, self.timer_label)
        )
        timer.start(1000)
        update_timer_label(self.start_time, self.timer_label)

        self._load_session()

    def _fill_selected_uout(self, value):
        """Заполняет выбранную ячейку в колонке Uвых (переводим в мВ)"""
        row = self.table.currentRow()
        if row < 0:
            row = 0
        self.table.setItem(row, COL_UOUT, self._editable_item(f"{value * 1000:.1f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))

    def _do_recalculate(self):
        usm_list = []

        for i in range(len(R4_ROWS)):
            usm = self._get_float(i, COL_USM)
            if usm is not None:
                usm_list.append(usm)

        avg_text = ""
        if usm_list:
            avg_text = f"{sum(usm_list) / len(usm_list):.4f}"

        item = self.table.item(0, COL_USM_AVG)
        if item is None:
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, COL_USM_AVG, item)

        item.setText(avg_text)