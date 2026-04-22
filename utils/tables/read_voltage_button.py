from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt


class ReadVoltageButton(QWidget):
    def __init__(self, stand_controller, on_success, label_text="Uвых, В:", parent=None):
        super().__init__(parent)
        self._stand = stand_controller
        self._on_success = on_success

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._btn = QPushButton("⟳ Считать Uвых со стенда")
        self._btn.clicked.connect(self._read)

        self._lbl = QLabel(label_text)
        self._val_lbl = QLabel("—")
        self._val_lbl.setMinimumWidth(80)
        self._val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._btn)
        layout.addWidget(self._lbl)
        layout.addWidget(self._val_lbl)
        layout.addStretch()

    def _read(self):
        try:
            m = self._stand.get_voltage_current()
            u_out = m.u_out
        except Exception as e:
            QMessageBox.critical(self, "Ошибка считывания", str(e))
            return

        self._val_lbl.setText(f"{u_out:.4f} В")

        try:
            self._on_success(u_out)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка вставки", str(e))