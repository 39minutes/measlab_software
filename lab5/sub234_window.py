# lab5/sub234_window.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QTableWidgetItem
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

HEADERS = ["Uвх, В", "Uвых.эксп, В", "Uвых.расч, В", "Ku.э"]
N_ROWS  = 13


class Sub234Window(Lab5SubBase):
    def __init__(self, parent=None):
        super().__init__("lab5_2.3.4", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("2.3.4 — Передаточная характеристика ИУ")
        self.resize(650, 520)

        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        r4_layout = QHBoxLayout()
        r4_layout.addWidget(QLabel("R4 (из варианта), кОм:"))
        self.r4_spin = QDoubleSpinBox()
        self.r4_spin.setRange(0.1, 1000.0)
        self.r4_spin.setDecimals(1)
        self.r4_spin.setValue(1.0)
        self.r4_spin.valueChanged.connect(self._safe_recalculate)
        r4_layout.addWidget(self.r4_spin)

        self.ku_label = QLabel("Ku.теор = —")
        r4_layout.addWidget(self.ku_label)
        r4_layout.addStretch()

        btn_graph = QPushButton("График передаточной характеристики ИУ")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.8(ИУ)": self.table})
        )
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        self.timer_label = QLabel()
        timer = QTimer(self)
        timer.timeout.connect(
            lambda: update_timer_label(self.start_time, self.timer_label)
        )
        timer.start(1000)
        update_timer_label(self.start_time, self.timer_label)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>2.3.4.</b> Передаточная характеристика ИУ (постоянный ток)<br>"
            "<small>K<sub>u.теор</sub> = −R4/R1, R1 = 1 кОм</small>"
        ))
        layout.addLayout(r4_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btn_graph)
        buttons_layout.addWidget(btn_save)
        layout.addLayout(buttons_layout)

        layout.addStretch()
        layout.addWidget(self.timer_label)
        layout.addWidget(btn_exit)

        self._load_session()

    def _do_recalculate(self):
        r4 = self.r4_spin.value()
        kt = -r4 / 1.0                        # R1 = 1 кОм (инвертирующий)
        self.ku_label.setText(f"Ku.теор = {kt:.3f}")

        for row in range(N_ROWS):
            uin = self._get_float(row, COL_UIN)
            uout_exp = self._get_float(row, COL_UOUT_E)

            # Uвых.расч = Ku × Uвх × 11   ← именно это даёт ~16.5 при Uвх = -1.5
            if uin is not None:
                u_th = kt * uin * 11
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
        points = []
        for row in range(N_ROWS):
            uin = self._get_float(row, COL_UIN)
            uout = self._get_float(row, COL_UOUT_E)
            if uin is not None and uout is not None:
                points.append((uin, uout))
        if not points:
            return
        points.sort()
        uin_arr = np.array([p[0] for p in points])
        uout_exp_arr = np.array([p[1] for p in points])

        r4 = self.r4_spin.value()
        kt = -r4 / 1.0
        uout_theor_arr = kt * uin_arr * 11

        plt.figure(figsize=(9, 5))
        plt.plot(uin_arr, uout_exp_arr, "bo-", label="Экспериментальная")
        plt.plot(uin_arr, uout_theor_arr, "r--", label=f"Расчётная (Ku={kt:.2f})")
        plt.axvline(0, color="k", linewidth=0.5)
        plt.axhline(0, color="k", linewidth=0.5)
        plt.xlabel("Uвх, В")
        plt.ylabel("Uвых, В")
        plt.title(f"Передаточная характеристика ИУ (R4 = {r4} кОм)")
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