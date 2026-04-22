import struct
import serial
from utils.data.measurement import Measurement


def parse_float(data_bytes):
    return struct.unpack('<f', data_bytes)[0]


class StandController:
    def __init__(self):
        self.ser = None

    def _ensure_connection(self):
        if self.ser and self.ser.is_open:
            return True
        try:
            self.ser = serial.Serial(
                port='COM5',
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.2
            )
            return True
        except serial.SerialException:
            return False

    def get_voltage_current(self):
        if not self._ensure_connection():
            raise RuntimeError(f"Не удалось подключиться к COM-порту {'COM5'}")

        try:
            # Запрос Uвых и Iвых
            self.ser.write(bytes.fromhex("14 10 00 02 01 02 05 00"))
            response1 = self.ser.read(32)

            # Запрос Uвх
            self.ser.write(bytes.fromhex("20 10 00 02 02 04 34 00"))
            response2 = self.ser.read(32)

            if len(response1) >= 18:
                u_vyk = parse_float(response1[6:10])
                i_vyk = parse_float(response1[12:16])
            else:
                u_vyk = i_vyk = 0.0

            if len(response2) >= 18:
                u_vkh = parse_float(response2[12:16])
            else:
                u_vkh = 0.0

            return Measurement(u_vkh, abs(u_vyk), i_vyk * 1000)  # в мА

        except serial.SerialException as e:
            try:
                self.ser.close()
            except:
                pass
            self.ser = None
            raise RuntimeError(f"Ошибка связи со стендом: {e!s}")

    def send_bytes(self, data: bytes):
        if not self._ensure_connection():
            raise RuntimeError(f"Не удалось подключиться к COM-порту {'COM5'}")

        self.ser.write(data)
        self.ser.read(32)
