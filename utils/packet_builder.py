import struct


class PacketBuilder:
    def __init__(self, header: bytes):
        self.header = header

    def build(self, payload: bytes) -> bytes:
        checksum = 0
        for b in self.header + payload:
            checksum ^= b

        return self.header + payload + bytes([checksum, 0x00])

    def build_float(self, value: float) -> bytes:
        payload = struct.pack('<f', value)

        return self.build(payload)
