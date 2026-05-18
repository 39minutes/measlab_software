# lab16_17/sub1654_window.py
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
from lab16_17.calculations_lab1617 import calc_ku_inv


R4_VALUES = [1.0, 2.0, 4.7, 10.0, 20.0, 100.0]

# Строки таблицы
ROW_UOUT_EXP   = 0   # Uвых.э, В
ROW_KU_EXP     = 1   # Ки.э
ROW_KU_THEOR   = 2   # Ки.т
ROW_UOUT_THEOR = 3   # Uвых.т, В

N_ROWS = 4
N_COLS = len(R4_VALUES)

H_HEADERS = ["1", "2", "4,7", "10", "20", "100"]
V_HEADERS = ["Uвых.э, В", "Ки.э", "Ки.т", "Uвых.т, В"]


class Sub1654Window(Lab1617SubBase):
    def __init__(self, parent=None):
        super().__init__("lab1617_16.5.4", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("16.5.4 — Инвертирующий усилитель")
        self.resize(920, 480)

        # Параметры схемы
        param_grp = QGroupBox("Параметры схемы")
        p_hl = QHBoxLayout(param_grp)

        p_hl.addWidget(QLabel("R1 ="))
        self.r1_spin = QDoubleSpinBox()
        self.r1_spin.setRange(0.1, 200.0)
        self.r1_spin.setDecimals(1)
        self.r1_spin.setValue(1.0)
        self.r1_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.r1_spin)

        p_hl.addWidget(QLabel("кОм   |   Uвх ="))
        self.uin_spin = QDoubleSpinBox()
        self.uin_spin.setRange(-20.0, 20.0)
        self.uin_spin.setDecimals(3)
        self.uin_spin.setSingleStep(0.1)
        self.uin_spin.setValue(0.5)
        self.uin_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.uin_spin)
        p_hl.addWidget(QLabel("В"))
        p_hl.addStretch()

        # Таблица
        self.table = PasteTableWidget(N_ROWS, N_COLS)
        self.table.setHorizontalHeaderLabels(H_HEADERS)
        self.table.setVerticalHeaderLabels(V_HEADERS)

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        note = QLabel(
            "<small>Столбцы соответствуют R4 = R5, кОм.<br>"
            "<b>Uвых.э</b> заносится экспериментально (обычно отрицательное значение).<br>"
            "<b>Ки.т</b> и <b>Uвых.т</b> рассчитываются автоматически.</small>"
        )
        note.setWordWrap(True)

        btn_plot_u = QPushButton("График Uвых = f(R4)")
        btn_plot_u.clicked.connect(self._plot_uout)

        btn_plot_ku = QPushButton("График Ku = f(R4)")
        btn_plot_ku.clicked.connect(self._plot_ku)

        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.16.5 ИнвУс": self.table})
        )

        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Зависимость выходного напряжения от сопротивления обратной связи "
            "инвертирующего усилителя</b>"
        ))
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
        uin = self.uin_spin.value()

        for col, r4 in enumerate(R4_VALUES):
            # Ku теоретический (модуль)
            ku_theor = calc_ku_inv(r4, r1)
            self._set_calc(ROW_KU_THEOR, col, abs(ku_theor))

            # Uвых теоретический (с отрицательным знаком — инверсия)
            uout_theor = -abs(ku_theor) * uin
            self._set_calc(ROW_UOUT_THEOR, col, uout_theor)

            # Ku экспериментальный (модуль)
            uout_exp = self._get_float(ROW_UOUT_EXP, col)
            if uout_exp is not None and uin != 0:
                ku_exp = uout_exp / uin
                self._set_calc(ROW_KU_EXP, col, abs(ku_exp))
            else:
                self._set_calc(ROW_KU_EXP, col, "")

    def _plot_uout(self):
        r4_vals = R4_VALUES[:]
        u_calc = []
        u_exp = []

        uin = self.uin_spin.value()
        r1 = self.r1_spin.value()

        for r4 in R4_VALUES:
            ku = abs(calc_ku_inv(r4, r1))
            u_calc.append(-ku * uin)                     # отрицательное из-за инверсии

            val = self._get_float(ROW_UOUT_EXP, R4_VALUES.index(r4))
            if val is not None:
                u_exp.append(val)

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(r4_vals, u_calc, "b-o", label="Uвых.т")
        if len(u_exp) == len(r4_vals):
            ax.plot(r4_vals, u_exp, "rs--", label="Uвых.э")

        ax.set_xlabel("R4 = R5, кОм")
        ax.set_ylabel("Uвых, В")
        ax.set_title("Зависимость выходного напряжения от R4")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def _plot_ku(self):
        r4_vals = R4_VALUES[:]
        ku_theor_vals = []
        ku_exp_vals = []

        for col in range(N_COLS):
            ku_theor_vals.append(self._get_float(ROW_KU_THEOR, col) or 0.0)

            uout_exp = self._get_float(ROW_UOUT_EXP, col)
            uin = self.uin_spin.value()
            if uout_exp is not None and uin != 0:
                ku_exp_vals.append(abs(uout_exp / uin))

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(r4_vals, ku_theor_vals, "b-o", label="Ки.т")
        if len(ku_exp_vals) == len(r4_vals):
            ax.plot(r4_vals, ku_exp_vals, "rs--", label="Ки.э")

        ax.set_xlabel("R4 = R5, кОм")
        ax.set_ylabel("Ku")
        ax.set_title("Зависимость коэффициента усиления от R4")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def _set_current_uout(self, value_v):
        col = self.table.currentColumn()
        if col < 0:
            col = 0
        self.table.setItem(ROW_UOUT_EXP, col, self._editable_item(value_v))
        self._safe_recalculate()

    def _editable_item(self, text):
        """Округление до сотых"""
        try:
            num = float(text)
            return QTableWidgetItem(f"{num:.2f}")
        except (ValueError, TypeError):
            return QTableWidgetItem(str(text))