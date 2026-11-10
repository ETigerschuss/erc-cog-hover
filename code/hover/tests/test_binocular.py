"""Tests for the two-eye model (hover.binocular) and the chain coupling."""
import numpy as np

from hover.binocular import BinocularModel, expansion, rotation
from hover.tier1_hh import DT, build_circuit, simulate


def test_chain_coupling_spreads_along_hs_cells():
    circ = build_circuit("eristalis_male", "HSN", g_lptc_mn=0.5, lptc_leak_scale=50.0, w_vs_mos=2.0, w_mio=3.0, gj_tau_ms=15.0)
    names, _, P, _ = circ
    n = len(names); i = names.index("HSS")
    leak = P[i, 3] + 1.0 / P[i, 0]
    _, V = simulate(circ, lambda tm: np.eye(n)[i] * (10.0 * leak if tm > 150 else 0.0), 400.0, pre_roll_ms=300.0)
    a, b = slice(int(100 / DT), int(150 / DT)), slice(int(300 / DT), int(400 / DT))
    dv = {nm: V[b, names.index(nm)].mean() - V[a, names.index(nm)].mean() for nm in ("HSS", "HSE", "HSN")}
    assert 0.15 < dv["HSE"] / dv["HSS"] < 0.5            # the neighbour follows
    assert 0.03 < dv["HSN"] / dv["HSS"] < dv["HSE"] / dv["HSS"]   # the next cell follows less


def test_rotation_is_conjugate_and_expansion_is_symmetric():
    male = BinocularModel("eristalis", "male")
    female = BinocularModel("eristalis", "female")
    assert "MIO" in male.motor_neurons and not any(n.startswith("MIO") for n in female.motor_neurons)
    rot = male.run(*rotation(male))
    exp_m = male.run(*expansion(male))
    exp_f = female.run(*expansion(female))
    assert rot["version"] > 0.1 and abs(exp_m["version"]) < 0.01          # rotation: conjugate; expansion: none
    assert exp_m["medial"] > exp_f["medial"] > 0.1                         # both retinae toward the midline, more in the male
    assert exp_m["d_rate"]["MIO"] > 1.5 * rot["d_rate"]["MIO"]             # one command prefers symmetric motion
    assert abs(exp_m["shift"]["R"][0] - exp_m["shift"]["L"][0]) < 0.01     # mirror symmetry


if __name__ == "__main__":
    for f in (test_chain_coupling_spreads_along_hs_cells, test_rotation_is_conjugate_and_expansion_is_symmetric):
        f(); print("ok", f.__name__)
