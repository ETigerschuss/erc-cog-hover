import numpy as np

from hover.emd import grating, t4t5_layer
from hover.snn import FIELD, drosophila, eristalis, rmn_rates

DT = 1 / 120


def test_emd_direction_selective():
    right = t4t5_layer(grating(0, FIELD, 0.5, DT), DT)["h"][30:].mean()
    left = t4t5_layer(grating(180, FIELD, 0.5, DT), DT)["h"][30:].mean()
    down = t4t5_layer(grating(90, FIELD, 0.5, DT), DT)["v"][30:].mean()
    assert right > 0 > left
    assert down > 0


def test_mot_prefers_horizontal_mos_vertical():
    c = drosophila()
    r = {d: rmn_rates(c, grating(d, FIELD, 0.5, DT), DT) for d in (0, 90, 180, 270)}
    mot_h = abs(r[0]["MOT"] - r[180]["MOT"])
    mot_v = abs(r[90]["MOT"] - r[270]["MOT"])
    mos_v = abs(r[90]["MOS"] - r[270]["MOS"])
    assert mot_h > mot_v
    assert mos_v > 0


def test_male_has_moi_female_not():
    s = grating(180, FIELD, 0.3, DT)
    assert "MOI" in rmn_rates(eristalis("male"), s, DT)
    assert "MOI" not in rmn_rates(eristalis("female"), s, DT)


def test_gap_junction_matrix_symmetric():
    G = eristalis("male").G()
    assert np.allclose(G, G.T)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
