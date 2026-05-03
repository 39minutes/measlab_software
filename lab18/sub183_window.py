# lab18/sub183_window.py
# 18.3 — Неинвертирующий сумматор при постоянных напряжениях
from datetime import datetime
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
from utils.tables.read_voltage_button import ReadVoltageButton
from lab18.calculations_lab18 import calc_uout_noninv, calc_k_noninv, calc_error_percent

ROW_LABELS = ["R4 = 1 кОм", "R4 = 2 кОм", "R4 max", "R4 нас"]
R4_FIXED   = [1.0, 2.0]
N_ROWS     = len(ROW_LABELS)

COL_R4     = 0
COL_U1     = 1
COL_U2     = 2
COL_K      = 3
COL_UOUT_C = 4
COL_UOUT_E = 5
COL_ERR    = 6

HEADERS = [
    "R4, кОм", "Uвх1 изм., В", "Uвх2 изм., В",
    "K=(R2+R4)/2R2", "Uвых расч., В", "Uвых эксп., В", "Погреш., %"
]


class Sub183Window(Lab18SubBase):
    def __init__(self, parent=None):
        super().__init__("lab18_18.3", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("18.3 — Неинвертирующий сумматор (пост. напряжения)")
        self.resize(800, 360)

        param_grp = QGroupBox("Параметры схемы")
        p_hl = QHBoxLayout(param_grp)
        p_hl.addWidget(QLabel("R2 (= R5), кОм:"))
        self.r2_spin = QDoubleSpinBox()
        self.r2_spin.setRange(0.1, 100.0)
        self.r2_spin.setDecimals(2)
        self.r2_spin.setValue(1.0)
        self.r2_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.r2_spin)
        p_hl.addWidget(QLabel("  R4 max, кОм:"))
        self.r4max_spin = QDoubleSpinBox()
        self.r4max_spin.setRange(0.1, 1000.0)
        self.r4max_spin.setDecimals(2)
        self.r4max_spin.setValue(10.0)
        self.r4max_spin.valueChanged.connect(self._on_r4max_changed)
        p_hl.addWidget(self.r4max_spin)
        p_hl.addWidget(QLabel("  R4 нас, кОм:"))
        self.r4sat_spin = QDoubleSpinBox()
        self.r4sat_spin.setRange(0.1, 2000.0)
        self.r4sat_spin.setDecimals(2)
        self.r4sat_spin.setValue(12.0)
        self.r4sat_spin.valueChanged.connect(self._on_r4max_changed)
        p_hl.addWidget(self.r4sat_spin)
        p_hl.addStretch()

        self.table = PasteTableWidget(N_ROWS, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setVerticalHeaderLabels(ROW_LABELS)
        self.table.setItemDelegate(Lab18Delegate(self._safe_recalculate, self))

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        for i, r4 in enumerate(R4_FIXED):
            self._set_fixed(i, COL_R4, str(r4))
        self._update_r4_labels()

        btn_plot = QPushButton("График Uвых = f(R4)")
        btn_plot.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.2 НеинвСумм": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 2.</b> Неинвертирующий сумматор (постоянные напряжения)<br>"
            "<small>Uвых расч = (R2+R4)/(2·R2)·(Uвх1+Uвх2)</small>"
        ))
        layout.addWidget(param_grp)
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)
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

    def _update_r4_labels(self):
        self._set_fixed(2, COL_R4, f"{self.r4max_spin.value():.2f}")
        self._set_fixed(3, COL_R4, f"{self.r4sat_spin.value():.2f}")

    def _on_r4max_changed(self):
        self._update_r4_labels()
        self._safe_recalculate()

    def _do_recalculate(self):
        r2 = self.r2_spin.value()
        for row in range(N_ROWS):
            r4   = self._get_float(row, COL_R4)
            u1   = self._get_float(row, COL_U1)
            u2   = self._get_float(row, COL_U2)
            uexp = self._get_float(row, COL_UOUT_E)
            if r4 is None:
                continue
            k = calc_k_noninv(r4, r2)
            self._set_calc(row, COL_K, f"{k:.4f}")
            if None not in (u1, u2):
                ucalc = calc_uout_noninv(r4, u1, u2, r2)
                self._set_calc(row, COL_UOUT_C, f"{ucalc:.4f}")
                if uexp is not None:
                    self._set_calc(row, COL_ERR,
                                   f"{calc_error_percent(ucalc, uexp):.2f}")

    def _plot(self):
        r4c, uc, ue_pts = [], [], []
        for row in range(N_ROWS):
            r4    = self._get_float(row, COL_R4)
            ucalc = self._get_float(row, COL_UOUT_C)
            uexp  = self._get_float(row, COL_UOUT_E)
            if r4 is not None:
                if ucalc is not None: r4c.append(r4); uc.append(ucalc)
                if uexp  is not None: ue_pts.append((r4, uexp))
        fig, ax = plt.subplots(figsize=(9, 5))
        if r4c:
            ax.plot(r4c, uc, "b-o", label="Uвых расч")
        if ue_pts:
            xs, ys = zip(*sorted(ue_pts))
            ax.plot(xs, ys, "rs--", label="Uвых эксп")
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_xlabel("R4, кОм"); ax.set_ylabel("Uвых, В")
        ax.set_title("18.3 — Неинвертирующий сумматор: Uвых = f(R4)")
        ax.legend(); ax.grid(True); plt.tight_layout(); plt.show()

    def _set_current_uout(self, value_v):
        row = self.table.currentRow()
        if row < 0:
            row = 0
        self.table.setItem(row, COL_UOUT_E, self._editable_item(f"{value_v:.4f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))
