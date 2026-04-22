from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
import os

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600


class FormulasWindow(QWidget):
    def __init__(self, lab_number: int):
        super().__init__()
        self.setWindowTitle(f"Формулы для Лабораторной №{lab_number}")
        self.resize(WINDOW_HEIGHT, WINDOW_WIDTH)

        layout = QVBoxLayout()
        label = QLabel()

        image_filename = f"formulas_lab{lab_number}.png"
        image_path = os.path.join(os.path.dirname(__file__), "res", image_filename)

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            label.setText(f"Не удалось загрузить изображение: {image_filename}")
        else:
            label.setPixmap(pixmap)
            label.setScaledContents(True)

        layout.addWidget(label)
        self.setLayout(layout)
