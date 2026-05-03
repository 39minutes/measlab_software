from utils.stand_controller import StandController
# lab5/controller_lab5.py
from lab5 import calculations_lab5 as calc


class Lab5Controller:
    def __init__(self):
        self.stand = StandController()

    def compute_k0(self, u_sat_p, u_sat_m, u1p, u1m):
        return calc.calc_k0(u_sat_p, u_sat_m, u1p, u1m)

    def compute_i_out(self, u_out_v, rn_kohm):
        return calc.calc_i_out(u_out_v, rn_kohm)

    def compute_u_sm(self, u_out_mv, r4_kohm):
        return calc.calc_u_sm(u_out_mv, r4_kohm)

    def compute_ku_repeater(self, u_out, u_in):
        return calc.calc_ku_exp(u_out, u_in)

    def compute_transfer_nu_row(self, u_in, u_out_exp, r4_kohm):
        return calc.calc_transfer_nu_row(u_in, u_out_exp, r4_kohm)

    def compute_transfer_iu_row(self, u_in, u_out_exp, r4_kohm):
        return calc.calc_transfer_iu_row(u_in, u_out_exp, r4_kohm)