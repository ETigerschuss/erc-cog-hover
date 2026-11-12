"""Tests for the two-stimulus design on one bowl display (hover.bowl)."""
import json

import numpy as np

from hover import bowl
from hover.binocular import PSI
from hover.eye import grid


def test_stimuli_stay_on_the_display_and_in_their_apertures():
    el = grid()[1]
    A, E = np.meshgrid(PSI, el)
    inside = np.hypot(A - bowl.LOVE_SPOT[0], E - bowl.LOVE_SPOT[1]) < bowl.LOVE_SPOT[2] - 6
    far = np.hypot(A - bowl.LOVE_SPOT[0], E - bowl.LOVE_SPOT[1]) > bowl.LOVE_SPOT[2] + 8
    off = (np.abs(A) > bowl.BOWL_AZ[1] + 8) | (E > bowl.BOWL_EL[1] + 8) | (E < bowl.BOWL_EL[0] - 8)
    full = bowl.bowl_stimulus(el, 270.0)
    matched = bowl.bowl_stimulus(el, bowl.MATCHED[1], aperture=bowl.LOVE_SPOT, surround=True)
    love = bowl.bowl_stimulus(el, bowl.LOVE[1], aperture=bowl.LOVE_SPOT)
    for mv in (full, matched, love):
        assert mv.min() >= 0.0 and mv.max() <= 1.0
        assert np.allclose(mv[:, off], 0.5, atol=0.02)                     # nothing outside the screen
    assert np.allclose(matched[:, inside], 0.5, atol=0.06)                 # the love spot is spared
    assert np.allclose(love[:, far], 0.5, atol=0.03)                       # and nothing but the love spot is shown
    assert love[:, inside].std() > 0.3 and matched[:, far & ~off].std() > 0.3
    assert np.abs(full[40] - full[20]).mean() > 0.05                       # the grating drifts after motion onset
    assert np.abs(full[10] - full[5]).mean() < 1e-9                        # and is still before


def test_two_stimuli_single_out_the_third_muscle():
    models = bowl.make_models()
    el = models["male"].el_grid
    m = bowl.compare(models, bowl.bowl_stimulus(el, bowl.MATCHED[1], aperture=bowl.LOVE_SPOT, surround=True))
    l = bowl.compare(models, bowl.bowl_stimulus(el, bowl.LOVE[1], aperture=bowl.LOVE_SPOT))
    assert abs(m["amp_male"] / m["amp_female"] - 1.0) < 0.10               # matched: the sexes move alike
    assert m["diff"] < 0.1 * m["amp_female"]
    assert l["amp_male"] / l["amp_female"] > 2.0                           # love spot: the male moves much more
    assert l["amp_male_cut"] / l["amp_female"] < 1.4                       # ... because of the muscle
    assert l["rate_male"]["MIO_R"] > 5.0 and l["rate_male"]["MIO_L"] > 5.0
    assert abs(m["rate_male"]["MIO_R"]) < 4.0
    # the collected results that the figures and the proposal read are these numbers
    res = json.loads((bowl.HERE / "bowl_result.json").read_text())["two_stimuli"]
    assert abs(res["matched"]["amp_male"] - m["amp_male"]) < 0.01 * m["amp_male"]
    assert abs(res["love_spot"]["ratio"] - l["amp_male"] / l["amp_female"]) < 0.03


def test_closed_loop_bookkeeping():
    models = bowl.make_models()
    start = dict(az=0.0, el=27.0, rad=17.0, dir=90.0, speed=30.0, wl=20.0)
    r = bowl.closed_loop(models["male"], models["male"], start, noise=0.02, generations=1, lam=2, mu=1, verbose=False)
    h = r["history"]
    assert [x["trials"] for x in h] == [1, 4] and h[0]["true"] > 0.08       # the designed stimulus engages the muscle
    assert all(bowl.CL_BOUNDS[k][0] <= h[-1]["mean"][k] <= bowl.CL_BOUNDS[k][1] for k in ("az", "el", "rad", "speed", "wl"))


if __name__ == "__main__":
    for f in (test_stimuli_stay_on_the_display_and_in_their_apertures, test_two_stimuli_single_out_the_third_muscle,
              test_closed_loop_bookkeeping):
        f(); print("ok", f.__name__)
