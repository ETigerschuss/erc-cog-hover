"""Smoke tests for the integrated model (eye map → Ammer front end → Tier-1 → retinal shift)."""
import numpy as np

from hover.eye import build_eye, grating_movie
from hover.species import Model


def test_eye_maps():
    e = build_eye("drosophila", "female")
    assert 700 <= e.n <= 1000 and e.n_patch > 30
    ah, av = e.axis_angles()
    m = e.inside((70, 110), (-10, 10))
    assert abs(np.median(ah[m])) < 5 and abs(np.median(av[m]) - 90) < 5   # lateral: rows horizontal
    m = e.inside((-10, 20), (20, 50))
    assert np.median(ah[m]) > 20                                          # dorso-frontal: +h tilted up
    # the male bright zone gathers more light but is not sampled more finely (Straw et al. 2006):
    # both sexes share one lattice
    m2, f2 = build_eye("eristalis", "male"), build_eye("eristalis", "female")
    assert m2.n == f2.n and np.allclose(m2.dphi, f2.dphi)
    bz = m2.inside((-25, 15), (5, 55))
    assert 1.4 < np.median(m2.dphi[bz]) < 2.2


def test_drosophila_front_end_and_motor_neurons():
    m = Model("drosophila", "female", target_hz=0)   # skip bias calibration for speed
    mov = grating_movie(m.az_grid, m.el_grid, 0.0, 30.0, 30.0, 0.9, m.dt_frame)
    _, _, g = m.front_end(mov)
    fr, fb = slice(45, 108), slice(20, 30)
    hse = g["HSE"][2][fr].mean() - g["HSE"][2][fb].mean()
    assert 8.0 < hse < 25.0                                               # Ammer-scale PD response
    mov_nd = grating_movie(m.az_grid, m.el_grid, 180.0, 30.0, 30.0, 0.9, m.dt_frame)
    _, _, g2 = m.front_end(mov_nd)
    assert g2["HSE"][2][fr].mean() - g2["HSE"][2][fb].mean() < -4.0      # hyperpolarisation
    r = m.run(mov)
    assert r["d_rate"]["MOT"] > 5.0                                       # HS drive raises MOT rate


if __name__ == "__main__":
    for f in (test_eye_maps, test_drosophila_front_end_and_motor_neurons):
        f(); print("ok", f.__name__)
