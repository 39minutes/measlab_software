# lab16_17/calculations_lab1617.py
"""
Формулы для Лаб. 16, 17.

16.5.3 — Дифференциальный усилитель:
    При R3=R1, R4=R2=R5 (R4=R5 — одно резисторное плечо):
    Uвых = (R4/R1) * (U2 - U1)
    Ku   = R4 / R1
    Общая формула (16.6): при R1=R2=R3=R4  Uвых = U2 - U1

    В таблице 16.4: R4 варьируется, U1 фиксировано (из 16.5.1), U2=0.5 В
    Ku.расч = R4/R1, R1 фикс. (из схемы, обычно 10 кОм)

16.5.4 — Инвертирующий усилитель:
    Uвых = -(R4/R1) * Uвх
    Ku   = -(R4 / R1)

    Таблица: Uвых = f(Uвх) при фиксированном R4
"""

R1_DEFAULT = 10.0   # кОм — по схеме лабораторного стенда


def calc_ku_diff(r4_kohm: float, r1: float = R1_DEFAULT) -> float:
    """Ku дифф. усилителя: Ku = R4/R1."""
    return r4_kohm / r1


def calc_uout_diff(u1: float, u2: float,
                   r4_kohm: float, r1: float = R1_DEFAULT) -> float:
    """Uвых дифф. усилителя = (R4/R1)*(U2 - U1)."""
    return (r4_kohm / r1) * (u2 - u1)


def calc_ku_inv(r4_kohm: float, r1: float = R1_DEFAULT) -> float:
    """Ku инв. усилителя: Ku = -R4/R1."""
    return -(r4_kohm / r1)


def calc_uout_inv(uin: float, r4_kohm: float,
                  r1: float = R1_DEFAULT) -> float:
    """Uвых инв. усилителя = -(R4/R1)*Uвх."""
    return -(r4_kohm / r1) * uin


def calc_error_percent(calc: float, exp: float) -> float:
    if calc == 0:
        return 0.0
    return abs(exp - calc) / abs(calc) * 100.0