# lab18/sub184_window.py
# 18.4 — Неинвертирующий сумматор при синусоидальном Uвх1 (R4=1 кОм)
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox
)
from PyQt6.QtCore import QTimer

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab18.sub_base18 import Lab18SubBase
from lab18.lab18_delegate import Lab18Delegate
from lab18.calculations_lab18 import calc_k_noninv

R4_FIXED_184 = 1.0

COL_U1AC  = 0
COL_U2DC  = 1
COL_UC_AC = 2
COL_UE_AC = 3
COL_UC_DC = 4
COL_UE_DC = 5

HEADERS = [
    "Uвх1~, В (СКЗ)", "Uвх2=, В",
    "Uвых расч~, В", "Uвых эксп~, В",
    "Uвых расч=, В", "Uвых эксп=, В"
]
N_ROWS = 1


class Sub184Window(Lab18SubBase):
    def __init__(self, parent=None):
        super().__init__("lab18_18.4", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("Неинвертирующий сумматор при входном напряжении в виде синусоидального сигнала")
        self.resize(760, 360)

        param_grp = QGroupBox("Параметры (R4 = 1 кОм фикс., f = 1000 Гц)")
        p_hl = QHBoxLayout(param_grp)
        p_hl.addWidget(QLabel("R2 (= R5), кОм:"))
        self.r2_spin = QDoubleSpinBox()
        self.r2_spin.setRange(0.1, 100.0)
        self.r2_spin.setDecimals(2)
        self.r2_spin.setValue(1.0)
        self.r2_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.r2_spin)
        self.k_label = QLabel("   K = —")
        p_hl.addWidget(self.k_label)
        p_hl.addStretch()

        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab18Delegate(self._safe_recalculate, self))

        osc_grp = QGroupBox("Осциллограммы (рассчитанные, f = 1000 Гц)")
        o_hl = QHBoxLayout(osc_grp)
        btn_osc1 = QPushButton("Uвх1~ и Uвых~ (переменная сост.)")
        btn_osc1.clicked.connect(self._plot_osc_ac)
        btn_osc2 = QPushButton("Uвх2= и Uвых (суммарный сигнал)")
        btn_osc2.clicked.connect(self._plot_osc_dc)
        o_hl.addWidget(btn_osc1)
        o_hl.addWidget(btn_osc2)

        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.3 НеинвСумм~": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 3.</b> Неинвертирующий сумматор: синус + постоянное<br>"
            "<small>R4=1 кОм, K=(R2+R4)/(2·R2). "
            "Uвых~ = K·Uвх1~  ;  Uвых= = K·Uвх2=</small>"
        ))
        layout.addWidget(param_grp)
        layout.addWidget(self.table)
        layout.addWidget(osc_grp)
        hl = QHBoxLayout()
        hl.addWidget(btn_save)
        layout.addLayout(hl)
        layout.addStretch()
        layout.addWidget(self.timer_label)
        layout.addWidget(btn_exit)

        tmr = QTimer(self)
        tmr.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        tmr.start(1000)
        update_timer_label(self.start_time, self.timer_label)
        self._load_session()

    def _do_recalculate(self):
        r2 = self.r2_spin.value()
        k  = calc_k_noninv(R4_FIXED_184, r2)
        self.k_label.setText(f"   K = {k:.4f}")
        for row in range(N_ROWS):
            u1ac = self._get_float(row, COL_U1AC)
            u2dc = self._get_float(row, COL_U2DC)
            if u1ac is not None:
                self._set_calc(row, COL_UC_AC, f"{k * u1ac:.4f}")
            if u2dc is not None:
                self._set_calc(row, COL_UC_DC, f"{k * u2dc:.4f}")

    def _plot_osc_ac(self):
        r2   = self.r2_spin.value()
        k    = calc_k_noninv(R4_FIXED_184, r2)
        u1ac = self._get_float(0, COL_U1AC)
        if u1ac is None:
            return
        t     = np.linspace(0, 3e-3, 2000)
        amp   = u1ac * np.sqrt(2)
        u_in  = amp * np.sin(2 * np.pi * 1000 * t)
        u_out = k * amp * np.sin(2 * np.pi * 1000 * t)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(t * 1e3, u_in,  "b-",
                label=f"Uвх1~ (A={amp:.3f} В, СКЗ={u1ac:.3f} В)")
        ax.plot(t * 1e3, u_out, "r--",
                label=f"Uвых~ (A={k * amp:.3f} В)")
        ax.set_xlabel("t, мс"); ax.set_ylabel("U, В")
        ax.set_title("18.4 — Осц.: Uвх1~ и Uвых (переменная составляющая)")
        ax.legend(); ax.grid(True); plt.tight_layout(); plt.show()

    def _plot_osc_dc(self):
        r2   = self.r2_spin.value()
        k    = calc_k_noninv(R4_FIXED_184, r2)
        u1ac = self._get_float(0, COL_U1AC)
        u2dc = self._get_float(0, COL_U2DC)
        if None in (u1ac, u2dc):
            return
        t     = np.linspace(0, 3e-3, 2000)
        amp   = u1ac * np.sqrt(2)
        u_ac  = amp * np.sin(2 * np.pi * 1000 * t)
        u_out = k * (u_ac + u2dc)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.axhline(u2dc, color="b", linestyle="-",
                   label=f"Uвх2= = {u2dc:.3f} В (пост.)")
        ax.plot(t * 1e3, u_out, "r--",
                label=f"Uвых = K·(Uвх1~+Uвх2=),  K={k:.3f}")
        ax.set_xlabel("t, мс"); ax.set_ylabel("U, В")
        ax.set_title("18.4 — Осц.: Uвх2= и Uвых (суммарный сигнал)")
        ax.legend(); ax.grid(True); plt.tight_layout(); plt.show()