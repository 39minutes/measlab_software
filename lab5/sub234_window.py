# lab5/sub234_window.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox
)
from PyQt6.QtCore import QTimer
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from lab5.calculations_lab5 import calc_ku_theor_iu

COL_UIN    = 0
COL_UOUT_E = 1
COL_UOUT_T = 2
COL_KU     = 3
HEADERS    = ["Uвх, В", "Uвых.эксп, В", "Uвых.расч, В", "Ku.э"]
N_ROWS     = 16


class Sub234Window(Lab5SubBase):
    def __init__(self, controller, parent=None):
        super().__init__("lab5_2.3.4", controller, parent)
        self.start_time = datetime.now()
        self.setWindowTitle("2.3.4 — Передаточная характеристика ИУ (пост. ток)")
        self.resize(600, 500)

        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        r4_hl = QHBoxLayout()
        r4_hl.addWidget(QLabel("R4 (из варианта), кОм:"))
        self.r4_spin = QDoubleSpinBox()
        self.r4_spin.setRange(0.1, 1000.0)
        self.r4_spin.setDecimals(1)
        self.r4_spin.setValue(10.0)
        self.r4_spin.valueChanged.connect(self._safe_recalculate)
        r4_hl.addWidget(self.r4_spin)
        self.ku_label = QLabel("Ku.теор = —")
        r4_hl.addWidget(self.ku_label)
        r4_hl.addStretch()

        btn_graph = QPushButton("График передаточной характеристики ИУ")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.8(ИУ)": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>2.3.4.</b> Передаточная характеристика ИУ (постоянный ток)<br>"
            "<small>K<sub>u.теор</sub> = −R4/R1, R1 = 10 кОм</small>"
        ))
        layout.addLayout(r4_hl)
        layout.addWidget(self.table)
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
        r4 = self.r4_spin.value()
        kt = calc_ku_theor_iu(r4)
        self.ku_label.setText(f"Ku.теор = {kt:.3f}")
        for row in range(N_ROWS):
            uin  = self._get_float(row, COL_UIN)
            uout = self._get_float(row, COL_UOUT_E)
            if uin is not None:
                u_th, ku_exp = self.controller.compute_transfer_iu_row(
                    uin, uout if uout is not None else 0.0, r4
                )
                self._set_calc(row, COL_UOUT_T, f"{u_th:.4f}")
                if uout is not None:
                    self._set_calc(row, COL_KU,
                                   "X" if uin == 0 else f"{ku_exp:.4f}")

    def _plot(self):
        pts = [
            (self._get_float(r, COL_UIN), self._get_float(r, COL_UOUT_E))
            for r in range(N_ROWS)
        ]
        pts = [(u, o) for u, o in pts if u is not None and o is not None]
        if not pts:
            return
        pts.sort()
        u_s  = np.array([p[0] for p in pts])
        ue_s = np.array([p[1] for p in pts])
        r4   = self.r4_spin.value()
        kt   = calc_ku_theor_iu(r4)
        plt.figure(figsize=(9, 5))
        plt.plot(u_s, ue_s, "bo-", label="Экспериментальная")
        plt.plot(u_s, kt * u_s, "r--", label=f"Расчётная (Ku={kt:.2f})")
        plt.axvline(0, color="k", linewidth=0.5)
        plt.axhline(0, color="k", linewidth=0.5)
        plt.xlabel("Uвх, В"); plt.ylabel("Uвых, В")
        plt.title(f"Передаточная характеристика ИУ (R4 = {r4} кОм)")
        plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()