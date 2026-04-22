# lab16_17/sub1653_window.py
# 16.5.3 — Исследование дифференциального усилителя
# Таблица 16.4: R4 варьируется {2, 4.7, 10, 20 кОм}, U2=0.5 В фикс.,
# U1 берётся из п.16.5.1 (вводится пользователем).
# График Uвых = f(R4) — расчётный и экспериментальный.
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox
)
from PyQt6.QtCore import QTimer

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab16_17.sub_base1617 import Lab1617SubBase
from lab16_17.lab1617_delegate import Lab1617Delegate
from lab16_17.calculations_lab1617 import (
    calc_ku_diff, calc_uout_diff, calc_error_percent, R1_DEFAULT
)

# R4 по таблице 16.1 / 16.4
R4_VALUES   = [2.0, 4.7, 10.0, 20.0]   # кОм
ROW_LABELS  = [f"R4={r} кОм" for r in R4_VALUES]
N_ROWS      = len(R4_VALUES)

COL_R4      = 0
COL_U1      = 1   # Uвх1 (из 16.5.1, фиксир. для данной строки — одно значение)
COL_U2      = 2   # Uвх2 = 0.5 В (фикс.)
COL_KU_C    = 3   # Ku расч
COL_UOUT_C  = 4   # Uвых расч
COL_UOUT_E  = 5   # Uвых эксп
COL_ERR     = 6   # Погрешность, %

HEADERS = [
    "R4, кОм", "Uвх1, В", "Uвх2=0.5В",
    "Ku расч", "Uвых расч, В", "Uвых эксп, В", "Погреш., %"
]

U2_FIXED = 0.5   # В — по условию задания


class Sub1653Window(Lab1617SubBase):
    def __init__(self, parent=None):
        super().__init__("lab1617_16.5.3", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("16.5.3 — Дифференциальный усилитель")
        self.resize(760, 380)

        # ── Параметры ─────────────────────────────────────────────────────
        param_grp = QGroupBox("Параметры схемы (рис. 16.7)")
        p_hl = QHBoxLayout(param_grp)
        p_hl.addWidget(QLabel("R1 ="))
        self.r1_spin = QDoubleSpinBox()
        self.r1_spin.setRange(0.1, 200.0)
        self.r1_spin.setDecimals(1)
        self.r1_spin.setValue(R1_DEFAULT)
        self.r1_spin.setToolTip("R1 схемы дифф. усилителя, кОм")
        self.r1_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.r1_spin)
        p_hl.addWidget(QLabel("кОм  |  R3=R1, R4=R5  |  U2 (фикс.) = 0.5 В"))
        p_hl.addStretch()

        # ── Таблица ───────────────────────────────────────────────────────
        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setVerticalHeaderLabels(ROW_LABELS)
        self.table.setItemDelegate(Lab1617Delegate(self._safe_recalculate, self))

        for i, r4 in enumerate(R4_VALUES):
            self._set_fixed(i, COL_R4, str(r4))
            self._set_fixed(i, COL_U2, str(U2_FIXED))

        # ── Пояснение к Uвх1 ─────────────────────────────────────────────
        note = QLabel(
            "<small><b>Uвх1</b> — вводится из результатов п.16.5.1 "
            "(напряжение снятое при RP1). U2 = 0.5 В фиксировано по заданию.</small>"
        )
        note.setWordWrap(True)

        # ── Кнопки ────────────────────────────────────────────────────────
        btn_plot_r4 = QPushButton("График Uвых = f(R4)")
        btn_plot_r4.clicked.connect(self._plot_vs_r4)
        btn_plot_ku = QPushButton("График Ku = f(R4)")
        btn_plot_ku.clicked.connect(self._plot_ku_vs_r4)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.16.4 ДифУс": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 16.4.</b> Дифференциальный усилитель — Uвых = f(R4)<br>"
            "<small>Uвых расч = (R4/R1)·(U2 − U1),  Ku = R4/R1</small>"
        ))
        layout.addWidget(param_grp)
        layout.addWidget(note)
        layout.addWidget(self.table)
        hl = QHBoxLayout()
        hl.addWidget(btn_plot_r4)
        hl.addWidget(btn_plot_ku)
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

    # ── Пересчёт ──────────────────────────────────────────────────────────
    def _do_recalculate(self):
        r1 = self.r1_spin.value()
        for i in range(N_ROWS):
            r4   = self._get_float(i, COL_R4)
            u1   = self._get_float(i, COL_U1)
            uexp = self._get_float(i, COL_UOUT_E)
            if r4 is None:
                continue
            ku = calc_ku_diff(r4, r1)
            self._set_calc(i, COL_KU_C, f"{ku:.4f}")
            if u1 is not None:
                ucalc = calc_uout_diff(u1, U2_FIXED, r4, r1)
                self._set_calc(i, COL_UOUT_C, f"{ucalc:.4f}")
                if uexp is not None:
                    self._set_calc(i, COL_ERR,
                                   f"{calc_error_percent(ucalc, uexp):.2f}")

    # ── Графики ───────────────────────────────────────────────────────────
    def _plot_vs_r4(self):
        r4c, uc, r4e, ue = [], [], [], []
        for i in range(N_ROWS):
            r4    = self._get_float(i, COL_R4)
            ucalc = self._get_float(i, COL_UOUT_C)
            uexp  = self._get_float(i, COL_UOUT_E)
            if r4 is not None:
                if ucalc is not None: r4c.append(r4); uc.append(ucalc)
                if uexp  is not None: r4e.append(r4); ue.append(uexp)
        fig, ax = plt.subplots(figsize=(9, 5))
        if r4c: ax.plot(r4c, uc, "b-o", label="Uвых расч")
        if r4e: ax.plot(r4e, ue, "rs--", label="Uвых эксп")
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_xlabel("R4, кОм"); ax.set_ylabel("Uвых, В")
        ax.set_title("16.5.3 — Дифф. усилитель: Uвых = f(R4)")
        ax.legend(); ax.grid(True); plt.tight_layout(); plt.show()

    def _plot_ku_vs_r4(self):
        r4_pts, ku_c, ku_e = [], [], []
        r1 = self.r1_spin.value()
        for i in range(N_ROWS):
            r4    = self._get_float(i, COL_R4)
            u1    = self._get_float(i, COL_U1)
            uexp  = self._get_float(i, COL_UOUT_E)
            if r4 is None:
                continue
            r4_pts.append(r4)
            ku_c.append(calc_ku_diff(r4, r1))
            if u1 is not None and uexp is not None and (U2_FIXED - u1) != 0:
                ku_e.append((r4, uexp / (U2_FIXED - u1)))
        fig, ax = plt.subplots(figsize=(9, 5))
        if r4_pts: ax.plot(r4_pts, ku_c, "b-o", label="Ku расч")
        if ku_e:
            xs, ys = zip(*sorted(ku_e))
            ax.plot(xs, ys, "rs--", label="Ku эксп")
        ax.set_xlabel("R4, кОм"); ax.set_ylabel("Ku")
        ax.set_title("16.5.3 — Дифф. усилитель: Ku = f(R4)")
        ax.legend(); ax.grid(True); plt.tight_layout(); plt.show()