# lab16_17/sub1654_window.py
# 16.5.4 — Исследование инвертирующего усилителя
# Схема рис. 16.8. Таблица: Uвых = f(Uвх) при фиксированном R4.
# График передаточной характеристики (как в 16.5.2, но для инвертирующего).
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
    calc_ku_inv, calc_uout_inv, calc_error_percent, R1_DEFAULT
)

# Uвх берём из таблицы 16.5.1 — 16 строк ±Uвх
N_ROWS  = 16
COL_UIN    = 0
COL_UOUT_C = 1
COL_UOUT_E = 2
COL_KU_E   = 3

HEADERS = ["Uвх, В", "Uвых расч, В", "Uвых эксп, В", "Ku эксп"]


class Sub1654Window(Lab1617SubBase):
    def __init__(self, parent=None):
        super().__init__("lab1617_16.5.4", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("16.5.4 — Инвертирующий усилитель")
        self.resize(560, 560)

        # ── Параметры схемы (рис. 16.8) ──────────────────────────────────
        param_grp = QGroupBox("Параметры схемы (рис. 16.8)")
        p_hl = QHBoxLayout(param_grp)
        p_hl.addWidget(QLabel("R4 ="))
        self.r4_spin = QDoubleSpinBox()
        self.r4_spin.setRange(0.1, 1000.0)
        self.r4_spin.setDecimals(1)
        self.r4_spin.setValue(100.0)
        self.r4_spin.setToolTip("R4 схемы инвертирующего усилителя, кОм")
        self.r4_spin.valueChanged.connect(self._on_param_changed)
        p_hl.addWidget(self.r4_spin)
        p_hl.addWidget(QLabel("кОм  |  R1 ="))
        self.r1_spin = QDoubleSpinBox()
        self.r1_spin.setRange(0.1, 200.0)
        self.r1_spin.setDecimals(1)
        self.r1_spin.setValue(R1_DEFAULT)
        self.r1_spin.valueChanged.connect(self._on_param_changed)
        p_hl.addWidget(self.r1_spin)
        p_hl.addWidget(QLabel("кОм"))
        self.ku_label = QLabel("   Ku расч = —")
        p_hl.addWidget(self.ku_label)
        p_hl.addStretch()

        # ── Таблица ───────────────────────────────────────────────────────
        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab1617Delegate(self._safe_recalculate, self))

        note = QLabel(
            "<small><b>Uвх</b> вводится из таблицы 16.5.1 (от −8 до +8 В и т.д.)."
            " Uвых эксп — измеренное значение.</small>"
        )
        note.setWordWrap(True)

        # ── Кнопки ────────────────────────────────────────────────────────
        btn_plot = QPushButton("График передаточной характеристики")
        btn_plot.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(
                self, {"Табл.16.5.4 ИнвУс": self.table}
            )
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>16.5.4.</b> Инвертирующий усилитель — передаточная характеристика<br>"
            "<small>Uвых расч = −(R4/R1)·Uвх,  схема рис. 16.8</small>"
        ))
        layout.addWidget(param_grp)
        layout.addWidget(note)
        layout.addWidget(self.table)
        hl = QHBoxLayout()
        hl.addWidget(btn_plot)
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

    def _on_param_changed(self):
        r4 = self.r4_spin.value()
        r1 = self.r1_spin.value()
        ku = calc_ku_inv(r4, r1)
        self.ku_label.setText(f"   Ku расч = {ku:.3f}")
        self._safe_recalculate()

    # ── Пересчёт ──────────────────────────────────────────────────────────
    def _do_recalculate(self):
        r4 = self.r4_spin.value()
        r1 = self.r1_spin.value()
        ku = calc_ku_inv(r4, r1)
        self.ku_label.setText(f"   Ku расч = {ku:.3f}")
        for row in range(N_ROWS):
            uin  = self._get_float(row, COL_UIN)
            uexp = self._get_float(row, COL_UOUT_E)
            if uin is None:
                continue
            ucalc = calc_uout_inv(uin, r4, r1)
            self._set_calc(row, COL_UOUT_C, f"{ucalc:.4f}")
            if uexp is not None:
                self._set_calc(
                    row, COL_KU_E,
                    "X" if uin == 0 else f"{uexp / uin:.4f}"
                )

    # ── График ────────────────────────────────────────────────────────────
    def _plot(self):
        pts_c = []
        pts_e = []
        for row in range(N_ROWS):
            uin   = self._get_float(row, COL_UIN)
            ucalc = self._get_float(row, COL_UOUT_C)
            uexp  = self._get_float(row, COL_UOUT_E)
            if uin is not None:
                if ucalc is not None: pts_c.append((uin, ucalc))
                if uexp  is not None: pts_e.append((uin, uexp))
        if not pts_c and not pts_e:
            return
        r4 = self.r4_spin.value()
        r1 = self.r1_spin.value()
        fig, ax = plt.subplots(figsize=(9, 5))
        if pts_c:
            pts_c.sort(); xs, ys = zip(*pts_c)
            ax.plot(xs, ys, "b-", label=f"Uвых расч (Ku={calc_ku_inv(r4,r1):.2f})")
        if pts_e:
            pts_e.sort(); xs, ys = zip(*pts_e)
            ax.plot(xs, ys, "ro--", label="Uвых эксп")
        ax.axvline(0, color="k", linewidth=0.5)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_xlabel("Uвх, В"); ax.set_ylabel("Uвых, В")
        ax.set_title(
            f"16.5.4 — Передаточная хар-ка инв. усилителя "
            f"(R4={r4} кОм, R1={r1} кОм)"
        )
        ax.legend(); ax.grid(True); plt.tight_layout(); plt.show()