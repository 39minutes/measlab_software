from dataclasses import dataclass


@dataclass
class Measurement:
    u_in: float
    u_out: float
    i_out_mA: float
