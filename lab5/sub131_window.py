# lab5/sub131_window.py
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from lab5 import calculations_lab5 as calc

COL_U_SAT_P = 0
COL_U1_P    = 1
COL_UIN_P   = 2
COL_U_SAT_M = 3
COL_U1_M    = 4
COL_UIN_M   = 5
COL_K0      = 6
COL_K0L     = 7

HEADERS = [
    "+Uнас, В", "U1+, В", "Uвх+, мкВ",
    "-Uнас, В", "U1-, В", "Uвх-, мкВ",
    "k0", "k0L, дБ"
]
ROW_LABELS = ["Неинвертирующий ОУ", "Инвертирующий ОУ"]
R5  = 200_000
RH1 = 100


class Sub131Window(Lab5SubBase):
    def __init__(self, parent=None):
        super().__init__("lab5_1.3.1", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("Снятие передаточной характеристики ОУ на постоянном токе")
        self.resize(820, 260)

        self.table = PasteTableWidget(2, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setVerticalHeaderLabels(ROW_LABELS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        btn_graph = QPushButton("График передаточных характеристик ОУ")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(
                self, {"Табл.5.3 Хар-ка ОУ": self.table}
            )
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 5.3.</b> Параметры передаточной характеристики ОУ<br>"
            "<small>Uвх± (мкВ) = U1± · Rн1/R5 · 10⁶ — рассчитывается автоматически</small>"
        ))
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
        for row in range(2):
            u_sat_p = self._get_float(row, COL_U_SAT_P)
            u1p     = self._get_float(row, COL_U1_P)
            u_sat_m = self._get_float(row, COL_U_SAT_M)
            u1m     = self._get_float(row, COL_U1_M)
            if u1p is not None:
                self._set_calc(row, COL_UIN_P, f"{u1p * RH1 / R5 * 1e6:.2f}")
            if u1m is not None:
                self._set_calc(row, COL_UIN_M, f"{u1m * RH1 / R5 * 1e6:.2f}")
            if None not in (u_sat_p, u_sat_m, u1p, u1m):
                k0, k0L = calc.calc_k0(u_sat_p, u_sat_m, u1p, u1m)
                self._set_calc(row, COL_K0,  f"{k0:.4g}")
                self._set_calc(row, COL_K0L, f"{k0L:.2f}")

    def _plot(self):
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        titles = ["Неинвертирующий режим", "Инвертирующий режим"]
        for row, ax in enumerate(axes):
            u_sat_p = self._get_float(row, COL_U_SAT_P)
            u_sat_m = self._get_float(row, COL_U_SAT_M)
            u1p     = self._get_float(row, COL_U1_P)
            u1m     = self._get_float(row, COL_U1_M)
            if None in (u_sat_p, u_sat_m, u1p, u1m):
                ax.set_title(f"{titles[row]}\n(недостаточно данных)")
                ax.grid(True)
                continue
            uinp_v = u1p * RH1 / R5
            uinm_v = u1m * RH1 / R5
            margin = max(abs(uinp_v - uinm_v) * 2, 1e-6)
            U     = np.linspace(uinm_v - margin, uinp_v + margin, 300)
            U_out = np.clip(
                np.interp(U, [uinm_v, uinp_v], [-abs(u_sat_m), abs(u_sat_p)]),
                -abs(u_sat_m), abs(u_sat_p)
            )
            ax.plot(U * 1e6, U_out, "b-")
            ax.axhline( abs(u_sat_p), color="r", linestyle="--",
                        label=f"+Uнас = {u_sat_p:.2f} В")
            ax.axhline(-abs(u_sat_m), color="g", linestyle="--",
                        label=f"−Uнас = {u_sat_m:.2f} В")
            ax.axvline(0, color="k", linewidth=0.5)
            ax.axhline(0, color="k", linewidth=0.5)
            ax.set_xlabel("Uвх, мкВ"); ax.set_ylabel("Uвых, В")
            ax.set_title(titles[row]); ax.legend(); ax.grid(True)
        plt.tight_layout(); plt.show()