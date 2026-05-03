# utils/stand_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
from utils.data.measurement import Measurement


class StandWorker(QThread):
    """Опрашивает стенд в фоновом потоке, чтобы не крашить GUI-поток Qt."""

    result_ready = pyqtSignal(object)   # Measurement или None
    error        = pyqtSignal(str)

    def __init__(self, stand, parent=None):
        super().__init__(parent)
        self.stand = stand

    def run(self):
        try:
            m = self.stand.get_voltage_current()
            self.result_ready.emit(m)
        except Exception as e:
            self.error.emit(str(e))
            self.result_ready.emit(None)