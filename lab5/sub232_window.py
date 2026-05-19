# lab5/sub232_window.py
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
from utils.tables.read_voltage_button import ReadVoltageButton


COL_UIN    = 0
COL_UOUT_E = 1
COL_UOUT_T = 2
COL_KU     = 3
HEADERS    = ["Uвх, В", "Uвых.эксп, В", "Uвых.расч, В", "Ku.э"]
N_ROWS     = 13


class Sub232Window(Lab5SubBase):
    def __init__(self, parent=None):
        super().__init__("lab5_2.3.2", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("2.3.2 — Передаточная характеристика НУ")
        self.resize(620, 520)

        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        r4_hl = QHBoxLayout()
        r4_hl.addWidget(QLabel("R4 (из варианта), кОм:"))
        self.r4_spin = QDoubleSpinBox()
        self.r4_spin.setRange(0.1, 1000.0)
        self.r4_spin.setDecimals(1)
        self.r4_spin.setValue(1.0)
        self.r4_spin.valueChanged.connect(self._safe_recalculate)
        r4_hl.addWidget(self.r4_spin)
        self.ku_label = QLabel("Ku.теор = —")
        r4_hl.addWidget(self.ku_label)
        r4_hl.addStretch()

        btn_graph = QPushButton("График передаточной характеристики НУ")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.8 НУ": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 5.8.</b> Передаточная характеристика НУ<br>"
            "<small>K<sub>u.теор</sub> = 1 + R4/R1, R1 = 10 кОм</small>"
        ))
        layout.addLayout(r4_hl)
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
        r4 = self.r4_spin.value()
        kt = 1 + r4 / 10.0                     # Ku.теор
        self.ku_label.setText(f"Ku.теор = {kt:.3f}")

        for row in range(N_ROWS):
            uin = self._get_float(row, COL_UIN)
            uout_exp = self._get_float(row, COL_UOUT_E)

            # Uвых.расч = Ku × Uвх  × 10   ← вот здесь было умножение на 10
            if uin is not None:
                u_th = kt * uin * 10
                self._set_calc(row, COL_UOUT_T, f"{u_th:.3f}")
            else:
                self._set_calc(row, COL_UOUT_T, "")

            # Ku.эксп
            if uout_exp is not None and uin is not None and uin != 0:
                ku_exp = uout_exp / uin
                self._set_calc(row, COL_KU, f"{ku_exp:.3f}")
            elif uout_exp is not None and uin == 0:
                self._set_calc(row, COL_KU, "X")
            else:
                self._set_calc(row, COL_KU, "")

    def _plot(self):
        pts = [
            (self._get_float(r, COL_UIN), self._get_float(r, COL_UOUT_E))
            for r in range(N_ROWS)
        ]
        pts = [(u, o) for u, o in pts if u is not None and o is not None]
        if not pts:
            return
        pts.sort()
        u_s = np.array([p[0] for p in pts])
        ue_s = np.array([p[1] for p in pts])

        r4 = self.r4_spin.value()
        kt = 1 + r4 / 10.0

        plt.figure(figsize=(9, 5))
        plt.plot(u_s, ue_s, "bo-", label="Экспериментальная")
        plt.plot(u_s, kt * u_s * 10, "r--", label=f"Расчётная (Ku={kt:.2f})")  # ← *10
        plt.axvline(0, color="k", linewidth=0.5)
        plt.axhline(0, color="k", linewidth=0.5)
        plt.xlabel("Uвх, В")
        plt.ylabel("Uвых, В")
        plt.title(f"Передаточная характеристика НУ (R4 = {r4} кОм)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def _set_current_uout(self, value_v):
        row = self.table.currentRow()
        if row < 0:
            row = 0
        self.table.setItem(row, COL_UOUT_E, self._editable_item(f"{value_v:.3f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))