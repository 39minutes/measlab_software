# lab16_17/sub1653_window.py
from datetime import datetime
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox, QTableWidgetItem
)
from PyQt6.QtCore import QTimer

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab16_17.sub_base1617 import Lab1617SubBase
from utils.tables.read_voltage_button import ReadVoltageButton
from lab16_17.calculations_lab1617 import calc_ku_diff, calc_uout_diff, R1_DEFAULT


R4_VALUES = [1.0, 2.0, 4.7, 10.0, 20.0, 100.0]
U2_FIXED = 0.5

ROW_UOUT_E = 0
ROW_KU_THEOR = 1
ROW_KU_EXP = 2

N_ROWS = 3
N_COLS = len(R4_VALUES)

H_HEADERS = ["1", "2", "4,7", "10", "20", "100"]
V_HEADERS = ["Uвых, В", "Ku теор", "Ku эксп"]


class Sub1653Window(Lab1617SubBase):
    def __init__(self, parent=None):
        super().__init__("lab1617_16.5.3", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("16.5.3 — Дифференциальный усилитель")
        self.resize(860, 420)

        param_grp = QGroupBox("Параметры схемы (рис. 16.7)")
        p_hl = QHBoxLayout(param_grp)

        p_hl.addWidget(QLabel("R1 ="))
        self.r1_spin = QDoubleSpinBox()
        self.r1_spin.setRange(0.1, 200.0)
        self.r1_spin.setDecimals(1)
        self.r1_spin.setValue(R1_DEFAULT)
        self.r1_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.r1_spin)

        p_hl.addWidget(QLabel("кОм   |   U1 ="))
        self.u1_spin = QDoubleSpinBox()
        self.u1_spin.setRange(-20.0, 20.0)
        self.u1_spin.setDecimals(4)
        self.u1_spin.setSingleStep(0.1)
        self.u1_spin.setValue(0.0)
        self.u1_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.u1_spin)

        p_hl.addWidget(QLabel("В   |   U2 = 0.5 В"))
        p_hl.addStretch()

        self.table = PasteTableWidget(N_ROWS, N_COLS)
        self.table.setHorizontalHeaderLabels(H_HEADERS)
        self.table.setVerticalHeaderLabels(V_HEADERS)

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        note = QLabel(
            "<small>Столбцы таблицы соответствуют значениям R4, кОм. "
            "В строку <b>Uвых, В</b> заносятся экспериментальные значения. "
            "<b>Ku теор</b> и <b>Ku эксп</b> рассчитываются автоматически.</small>"
        )
        note.setWordWrap(True)

        btn_plot_u = QPushButton("График Uвых = f(R4)")
        btn_plot_u.clicked.connect(self._plot_uout)

        btn_plot_ku = QPushButton("График Ku = f(R4)")
        btn_plot_ku.clicked.connect(self._plot_ku)

        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.16.4 ДифУс": self.table})
        )

        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 16.4.</b> Дифференциальный усилитель"
        ))
        layout.addWidget(QLabel("<small><b>Столбцы: R4, кОм</b></small>"))
        layout.addWidget(param_grp)
        layout.addWidget(note)
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)

        hl = QHBoxLayout()
        hl.addWidget(btn_plot_u)
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
        self._safe_recalculate()

    def _do_recalculate(self):
        r1 = self.r1_spin.value()
        u1 = self.u1_spin.value()

        for col, r4 in enumerate(R4_VALUES):
            ku_theor = calc_ku_diff(r4, r1)
            self._set_calc(ROW_KU_THEOR, col, f"{ku_theor:.4f}")

            uout_exp = self._get_float(ROW_UOUT_E, col)
            if uout_exp is not None:
                denom = U2_FIXED - u1
                if denom != 0:
                    self._set_calc(ROW_KU_EXP, col, f"{uout_exp / denom:.4f}")
                else:
                    self._set_calc(ROW_KU_EXP, col, "X")
            else:
                self._set_calc(ROW_KU_EXP, col, "")

    def _plot_uout(self):
        r4_vals = []
        u_exp_vals = []
        u_calc_vals = []

        r1 = self.r1_spin.value()
        u1 = self.u1_spin.value()

        for col, r4 in enumerate(R4_VALUES):
            r4_vals.append(r4)
            u_calc_vals.append(calc_uout_diff(u1, U2_FIXED, r4, r1))

            u_exp = self._get_float(ROW_UOUT_E, col)
            if u_exp is not None:
                u_exp_vals.append((r4, u_exp))

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(r4_vals, u_calc_vals, "b-o", label="Uвых расч")

        if u_exp_vals:
            xs, ys = zip(*u_exp_vals)
            ax.plot(xs, ys, "rs--", label="Uвых эксп")

        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_xlabel("R4, кОм")
        ax.set_ylabel("Uвых, В")
        ax.set_title("16.5.3 — Дифференциальный усилитель: Uвых = f(R4)")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def _plot_ku(self):
        r4_vals = []
        ku_theor_vals = []
        ku_exp_vals = []

        u1 = self.u1_spin.value()
        denom = U2_FIXED - u1

        for col, r4 in enumerate(R4_VALUES):
            r4_vals.append(r4)
            ku_theor_vals.append(self._get_float(ROW_KU_THEOR, col) or 0.0)

            u_exp = self._get_float(ROW_UOUT_E, col)
            if u_exp is not None and denom != 0:
                ku_exp_vals.append((r4, u_exp / denom))

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(r4_vals, ku_theor_vals, "b-o", label="Ku теор")

        if ku_exp_vals:
            xs, ys = zip(*ku_exp_vals)
            ax.plot(xs, ys, "rs--", label="Ku эксп")

        ax.set_xlabel("R4, кОм")
        ax.set_ylabel("Ku")
        ax.set_title("16.5.3 — Дифференциальный усилитель: Ku = f(R4)")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def _set_current_uout(self, value_v):
        col = self.table.currentColumn()
        if col < 0:
            col = 0
        self.table.setItem(ROW_UOUT_E, col, self._editable_item(f"{value_v:.4f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        return QTableWidgetItem(str(text))