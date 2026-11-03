"""Smoke tests for the Tier-1 HH port (fast with numba; ~5 s without)."""
import numpy as np

from hover.tier1_hh import DT, build_circuit, simulate, spike_rate


def _rate(V, i, a, b):
    return spike_rate(V[:, i])[int(a / DT):int(b / DT)].mean()


def test_tonic_rates_match_mesh_preset():
    c = build_circuit("drosophila")
    names = c[0]
    t, V = simulate(c, lambda tm: np.zeros(len(names)), 400.0, noise=0.0)
    for nm in ("MOT", "MOS"):
        r = _rate(V, names.index(nm), 50, 390)
        assert 80 < r < 130, (nm, r)


def test_hs_hyperpolarisation_lowers_mot_rate():
    c = build_circuit("eristalis_male", "HSN", g_lptc_mn=0.75)
    names = c[0]
    hs = [names.index(n) for n in names if n.startswith("HS")]

    def inj(tm):
        I = np.zeros(len(names))
        if 150 <= tm < 450:
            I[hs] = -7.0
        return I

    t, V = simulate(c, inj, 500.0, noise=0.0)
    i = names.index("MOT")
    assert _rate(V, i, 250, 440) < _rate(V, i, 30, 140) - 5
    assert "MIO" in names


if __name__ == "__main__":
    for f in (test_tonic_rates_match_mesh_preset, test_hs_hyperpolarisation_lowers_mot_rate):
        f(); print("ok", f.__name__)
