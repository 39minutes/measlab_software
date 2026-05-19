# lab5/calculations_lab5.py
import numpy as np

R1_KOHM = 10.0   # R1 = 10 кОм (фиксировано для всех схем)
R5_OHM  = 200_000
RH1_OHM = 100


def calc_k0(u_sat_p: float, u_sat_m: float,
            u1p: float, u1m: float) -> tuple:
    uinp = u1p * RH1_OHM / R5_OHM
    uinm = u1m * RH1_OHM / R5_OHM
    delta_in = uinp - uinm
    if delta_in == 0:
        return 0.0, 0.0
    k0   = (abs(u_sat_p) + abs(u_sat_m)) / abs(delta_in)
    k0L  = 20 * np.log10(k0) if k0 > 0 else 0.0
    return round(k0, 2), round(k0L, 2)


def calc_i_out(u_out_v: float, rn_kohm) -> float:
    if rn_kohm is None or rn_kohm == 0:
        return 0.0
    return round(abs(u_out_v) / (rn_kohm * 1000) * 1000, 3)


def calc_u_sm(u_out_mv: float, r4_kohm: float) -> float:
    return round(u_out_mv / (1 + r4_kohm / R1_KOHM), 4)


def calc_ku_theor_nu(r4_kohm: float) -> float:
    return round(1 + r4_kohm / R1_KOHM, 4)


def calc_ku_theor_iu(r4_kohm: float) -> float:
    return round(-r4_kohm / R1_KOHM, 4)


def calc_ku_exp(u_out: float, u_in: float) -> float:
    if u_in == 0:
        return float('nan')
    return round(u_out / u_in, 4)


def calc_transfer_nu_row(u_in: float, u_out_exp: float,
                         r4_kohm: float) -> tuple:
    kt    = calc_ku_theor_nu(r4_kohm)
    u_th  = round(kt * u_in, 4)
    ku_e  = calc_ku_exp(u_out_exp, u_in)
    return u_th, ku_e


def calc_transfer_iu_row(u_in: float, u_out_exp: float,
                         r4_kohm: float) -> tuple:
    kt    = calc_ku_theor_iu(r4_kohm)
    u_th  = round(kt * u_in, 4)
    ku_e  = calc_ku_exp(u_out_exp, u_in)
    return u_th, ku_e