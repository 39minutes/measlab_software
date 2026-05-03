# lab5/sub233_window.py
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from utils.tables.read_voltage_button import ReadVoltageButton
from lab5.const_lab5 import UIN_REPEATER
from lab5.calculations_lab5 import calc_ku_exp

COL_UIN  = 0
COL_UOUT = 1
COL_KU   = 2
HEADERS  = ["Uвх, В", "Uвых.э, В", "Ku.э"]


class Sub233Window(Lab5SubBase):
    def __init__(self, controller, parent=None):
        super().__init__("lab5_2.3.3", controller, parent)
        self.start_time = datetime.now()
        self.setWindowTitle("2.3.3 — Передаточная характеристика повторителя")
        self.resize(400, 300)

        self.table = PasteTableWidget(len(UIN_REPEATER), len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        self.read_uout_btn = ReadVoltageButton(
            self.controller.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        for i, uin in enumerate(UIN_REPEATER):
            self._set_fixed(i, COL_UIN, str(uin))
            if uin == 0:
                self._set_fixed(i, COL_KU, "X")

        btn_graph = QPushButton("График характеристики повторителя")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.9 Повт.": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 5.9.</b> Передаточная характеристика повторителя<br>"
            "<small>Теор.: K<sub>u</sub> = 1 (U<sub>вых</sub> = U<sub>вх</sub>)</small>"
        ))
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)
        hl = QHBoxLayout()
        hl.addWidget(btn_graph)
        hl.addWidget(btn_save)
        layout.addLayout(hl)
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
        for i, uin in enumerate(UIN_REPEATER):
            if uin == 0:
                continue
            uout = self._get_float(i, COL_UOUT)
            if uout is not None:
                self._set_calc(i, COL_KU, f"{calc_ku_exp(uout, uin):.4f}")

    def _plot(self):
        uin_pts, uout_pts = [], []
        for i, uin in enumerate(UIN_REPEATER):
            uout = self._get_float(i, COL_UOUT)
            if uout is not None:
                uin_pts.append(uin); uout_pts.append(uout)
        if not uin_pts:
            return
        u_arr = np.array(uin_pts)
        plt.figure(figsize=(8, 5))
        plt.plot(u_arr, uout_pts, "bo-", label="Экспериментальная")
        plt.plot(u_arr, u_arr,    "r--", label="Идеальная (Ku = 1)")
        plt.axvline(0, color="k", linewidth=0.5)
        plt.axhline(0, color="k", linewidth=0.5)
        plt.xlabel("Uвх, В"); plt.ylabel("Uвых, В")
        plt.title("Передаточная характеристика повторителя напряжения")
        plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    def _set_current_uout(self, value_v):
        row = self.table.currentRow()
        if row < 0:
            row = 0
        self.table.setItem(row, COL_UOUT, self._editable_item(f"{value_v:.4f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))
