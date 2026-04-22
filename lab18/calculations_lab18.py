# lab18/calculations_lab18.py
R1_DEFAULT = 1.0
R2_DEFAULT = 1.0


def calc_uout_inv(r4_kohm: float, u1: float, u2: float,
                  r1: float = R1_DEFAULT, r2: float = R2_DEFAULT) -> float:
    return -(r4_kohm / r1 * u1 + r4_kohm / r2 * u2)


def calc_uout_noninv(r4_kohm: float, u1: float, u2: float,
                     r2: float = R2_DEFAULT) -> float:
    return (r2 + r4_kohm) / (2.0 * r2) * (u1 + u2)


def calc_k_noninv(r4_kohm: float, r2: float = R2_DEFAULT) -> float:
    return (r2 + r4_kohm) / (2.0 * r2)


def calc_error_percent(calc: float, exp: float) -> float:
    if calc == 0:
        return 0.0
    return abs(exp - calc) / abs(calc) * 100.0