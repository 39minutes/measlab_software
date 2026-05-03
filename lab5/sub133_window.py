# lab5/sub133_window.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer
from datetime import datetime

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from utils.tables.read_voltage_button import ReadVoltageButton

R4_ROWS    = [200, 100]
COL_R4     = 0
COL_UOUT   = 1
COL_USM    = 2
HEADERS    = ["R4, кОм", "Uвых, мВ", "Uсм, мВ"]
ROW_LABELS = ["R4 = 200 кОм", "R4 = 100 кОм", "Среднее  Uсм.ср"]


class Sub133Window(Lab5SubBase):
    def __init__(self, controller, parent=None):
        super().__init__("lab5_1.3.3", controller, parent)
        self.start_time = datetime.now()
        self.setWindowTitle("1.3.3 — Измерение напряжения смещения ОУ")
        self.resize(420, 220)

        self.table = PasteTableWidget(3, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setVerticalHeaderLabels(ROW_LABELS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        for i, r4 in enumerate(R4_ROWS):
            self._set_fixed(i, COL_R4, str(r4))
        self._set_fixed(2, COL_R4,   "—")
        self._set_fixed(2, COL_UOUT, "—")
        self._set_fixed(2, COL_USM,  "")

        self.read_uout_btn = ReadVoltageButton(
            self.controller.stand,
            self._set_current_uout_mv,
            label_text="Uвых, В:"
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
            "<b>Таблица 5.5.</b> Напряжение смещения ОУ<br>"
            "<small>U<sub>см</sub> = U<sub>вых</sub> / (1 + R4/R1), R1 = 10 кОм</small>"
        ))
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)
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

    def _do_recalculate(self):
        usm_list = []
        for i, r4 in enumerate(R4_ROWS):
            uout = self._get_float(i, COL_UOUT)
            if uout is not None:
                usm = self.controller.compute_u_sm(uout, r4)
                self._set_calc(i, COL_USM, f"{usm:.4f}")
                usm_list.append(usm)
        if usm_list:
            self._set_calc(2, COL_USM, f"{sum(usm_list) / len(usm_list):.4f}")

    def _set_current_uout_mv(self, value_v):
        row = self.table.currentRow()
        if row < 0:
            row = 0
        self.table.setItem(row, COL_UOUT, self._editable_item(f"{value_v * 1000:.2f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))
