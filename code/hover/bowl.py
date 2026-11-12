"""What is the third muscle for? Two stimuli on one bowl-shaped projector display.

The experiment has one display: a bowl-shaped projection screen in front of the tethered animal
(Prech, Groschner & Borst 2024; about 180° of azimuth and 125° of elevation [verify with the
set-up]). Both eyes see the same image, so every stimulus here is one head-centred movie.

The design uses two stimuli from one family (drifting square-wave gratings in an aperture):

  matched     the predicted retinal movement is large and THE SAME in males and females, although
              their HSN fields differ. It calibrates each animal (gain of the shared reflex, quality
              of the tracking) and tests the homology assumption: a sex difference here would
              falsify the shared part of the model.
  love spot   the predicted retinal movement DIFFERS between the sexes as much as possible, with
              the stimulus confined to the dorso-frontal bright zone. Cutting the third muscle in
              the model shows how much of the difference the muscle carries.

Neutral model of the third muscle (M. interocularis, MIO): each limb has its own motor neuron,
coupled to an LPTC of its own side (`mio_from`: HSN, HSNE, pooled HS or pooled VS), and pulls its
retina in the direction `mio_pull` (own-eye anatomical frame; 0° = anterior/medial is the reading
of the tomography). `scan` and `position_map` evaluate any of these variants; the pull direction is
applied after the simulation, so one run serves all pull directions.

    python -m hover.bowl --scan --map --out hover/bowl_result.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np

from .binocular import PSI, BinocularModel, split_eyes
from .oculomotor import PULL_FALT, unit

HERE = pathlib.Path(__file__).resolve().parent
BOWL_AZ = (-90.0, 90.0)          # head-centred azimuth covered by the screen [deg]
BOWL_EL = (-52.0, 73.0)          # elevation covered (125°, screen centre 10° above the horizon) [verify]
LOVE_SPOT = (0.0, 27.0, 17.0)    # centre azimuth, centre elevation, radius of the love-spot aperture [deg; verify with facet maps]
DURATION, ONSET = 1.0, 0.25
DIRS = np.arange(0.0, 360.0, 30.0)


# ----------------------------------------------------------------------------- stimuli
def square_grating(el_grid, direction_deg, speed, wavelength=20.0, contrast=1.0, duration=DURATION,
                   onset=ONSET, dt=1 / 120, edge=0.5):
    """Drifting square-wave grating in head coordinates (0° = toward the animal's right, 90° = up).
    Edges are linear ramps of ±`edge` degrees, so that sub-pixel drift is smooth on the 1° grid."""
    T = int(round(duration / dt))
    A, E = np.meshgrid(PSI, el_grid)
    th = np.deg2rad(direction_deg)
    proj = A * np.cos(th) + E * np.sin(th)
    t = np.arange(T) * dt
    phase = np.cumsum((t >= onset).astype(float)) * dt * speed
    s = np.sin(2 * np.pi * (proj[None] - phase[:, None, None]) / wavelength)
    return 0.5 + 0.5 * contrast * np.clip(s * wavelength / (2 * np.pi * edge), -1.0, 1.0)


def bowl_window(el_grid, soft=2.0):
    """Soft mask of the screen: 1 on the bowl, 0 outside (uniform, static mean luminance there)."""
    A, E = np.meshgrid(PSI, el_grid)
    f = lambda x, lo, hi: 1 / (1 + np.exp(-(x - lo) / soft)) / (1 + np.exp((x - hi) / soft))
    return f(A, *BOWL_AZ) * f(E, *BOWL_EL)


def disc(el_grid, az0, el0, ra, rb=None, soft=2.0):
    """Soft elliptical aperture with semi-axes ra (azimuth) and rb (elevation; default: a circle)."""
    rb = ra if rb is None else rb
    A, E = np.meshgrid(PSI, el_grid)
    rho = np.hypot((A - az0) / ra, (E - el0) / rb)            # 1 on the edge
    return 1.0 / (1.0 + np.exp((rho - 1.0) * min(ra, rb) / soft))


def bowl_stimulus(el_grid, direction_deg, speed=30.0, wavelength=20.0, contrast=1.0, aperture=None,
                  surround=False, dt=1 / 120):
    """One head-centred movie. aperture = (az0, el0, radius) or (az0, el0, ra, rb) confines the
    grating to a disc or an ellipse; surround=True shows the grating everywhere on the bowl EXCEPT there."""
    g = square_grating(el_grid, direction_deg, speed, wavelength, contrast, dt=dt)
    w = bowl_window(el_grid)
    if aperture is not None:
        d = disc(el_grid, *aperture)
        w = w * ((1.0 - d) if surround else d)
    return 0.5 + (g - 0.5) * w[None]


# ----------------------------------------------------------------------------- responses
def shifts(d_rate: dict, baseline: dict, mio_gain: float = 1.0, mio_pull: float = 0.0):
    """Retinal movement of both eyes from the motor-neuron rate changes: four numbers,
    (anterior, dorsal) for the right and for the left retina, each in its own anatomical frame."""
    out = []
    for side in ("R", "L"):
        v = np.zeros(2)
        for mus, th in PULL_FALT.items():
            nm = f"{mus}_{side}"
            v = v + d_rate[nm] / max(baseline[nm], 1e-6) * unit(th)
        nm = "MIO" if "MIO" in d_rate else f"MIO_{side}"
        if nm in d_rate:
            v = v + mio_gain * d_rate[nm] / max(baseline[nm], 1e-6) * unit(mio_pull)
        out.append(v)
    return np.concatenate(out)


def respond(model: BinocularModel, movie_head, mio_pull: float = 0.0) -> dict:
    mR, mL = split_eyes(movie_head)
    r = model.run(mR, mL, onset_s=ONSET)
    s = shifts(r["d_rate"], r["baseline"], 1.0, mio_pull)
    return dict(shift=s, shift_cut=shifts(r["d_rate"], r["baseline"], 0.0, mio_pull),
                d_rate=r["d_rate"], baseline=r["baseline"], lptc_dv=r["lptc_dv"])


def amplitude(v4):
    """Mean retinal movement of the two eyes (length of the 2-D shift, averaged over the eyes)."""
    v4 = np.asarray(v4)
    return float(0.5 * (np.hypot(v4[0], v4[1]) + np.hypot(v4[2], v4[3])))


def difference(a4, b4):
    """Mean length of the difference vectors of the two eyes."""
    d = np.asarray(a4) - np.asarray(b4)
    return float(0.5 * (np.hypot(d[0], d[1]) + np.hypot(d[2], d[3])))


def make_models(mio_from: str = "HSN", mio: str = "independent"):
    return dict(female=BinocularModel("eristalis", "female"),
                male=BinocularModel("eristalis", "male", mio=mio, mio_from=mio_from))


def male_with_hsn_field(az0, el0, saz=9.0, sel=16.0, **kw) -> BinocularModel:
    """A male whose HSN receptive field (and with it the drive of the third muscle) sits elsewhere
    than the model assumes: the 'animal' of the closed-loop simulations."""
    from .lptc import gaussian_rf
    m = BinocularModel("eristalis", "male", mio="independent", **kw)
    front = m.eye_model.front
    front.specs[0].rf = gaussian_rf(az0, el0, saz, sel)
    front.__post_init__()                                   # recompute the receptive-field weights
    return m


def compare(models: dict, movie_head, mio_pull: float = 0.0) -> dict:
    """Male, female and male with the third muscle cut, for one stimulus."""
    f = respond(models["female"], movie_head)
    m = respond(models["male"], movie_head, mio_pull)
    a_m, a_f, a_c = amplitude(m["shift"]), amplitude(f["shift"]), amplitude(m["shift_cut"])
    diff, diff_cut = difference(m["shift"], f["shift"]), difference(m["shift_cut"], f["shift"])
    return dict(male=m["shift"].tolist(), female=f["shift"].tolist(), male_cut=m["shift_cut"].tolist(),
                amp_male=a_m, amp_female=a_f, amp_male_cut=a_c, diff=diff, diff_cut=diff_cut,
                rate_male={k: float(v) for k, v in m["d_rate"].items()},
                rate_female={k: float(v) for k, v in f["d_rate"].items()})


# ----------------------------------------------------------------------------- scans
CONDITIONS = {"full bowl": dict(aperture=None, surround=False),
              "love spot only": dict(aperture=LOVE_SPOT, surround=False),
              "bowl without love spot": dict(aperture=LOVE_SPOT, surround=True)}


def aperture_conditions(radii=(12.0, 17.0, 22.0)):
    """The love-spot aperture at several radii, grating inside or outside."""
    c = {}
    for r in radii:
        c[f"inside r{r:g}"] = dict(aperture=(LOVE_SPOT[0], LOVE_SPOT[1], r), surround=False)
        c[f"outside r{r:g}"] = dict(aperture=(LOVE_SPOT[0], LOVE_SPOT[1], r), surround=True)
    return c


def scan(models: dict, speed=30.0, wavelength=20.0, dirs=DIRS, mio_pull=0.0, verbose=True, conditions=None) -> dict:
    """Direction tuning of the predicted retinal movement in the aperture conditions."""
    el = models["male"].el_grid
    res = {}
    for cname, kw in (conditions or CONDITIONS).items():
        rows = []
        for d in dirs:
            c = compare(models, bowl_stimulus(el, d, speed, wavelength, **kw), mio_pull)
            c["dir"] = float(d)
            rows.append(c)
            if verbose:
                print(f"{cname:24s} dir {d:5.0f}  male {c['amp_male']:.3f}  female {c['amp_female']:.3f}  "
                      f"cut {c['amp_male_cut']:.3f}  diff {c['diff']:.3f}  MIO {c['rate_male'].get('MIO_R', 0):+.1f}/{c['rate_male'].get('MIO_L', 0):+.1f}",
                      flush=True)
        res[cname] = rows
    return res


def pick(scan_res: dict) -> dict:
    """The two stimuli. matched: largest common movement with the smallest sex difference, among the
    wide-field conditions. love spot: largest sex difference among the love-spot gratings."""
    best_m, best_l = None, None
    for cname in ("full bowl", "bowl without love spot"):
        for r in scan_res[cname]:
            score = min(r["amp_male"], r["amp_female"]) - 3.0 * r["diff"]
            if best_m is None or score > best_m[0]:
                best_m = (score, cname, r)
    rows = scan_res["love spot only"]
    top = max(r["diff"] for r in rows)
    # among directions within 5 % of the largest difference, prefer a vertical drift: it is
    # mirror-symmetric for the two eyes, so the prediction does not depend on left-right details
    cand = [r for r in rows if r["diff"] >= 0.95 * top]
    r = min(cand, key=lambda q: min(abs(q["dir"] - 90.0), abs(q["dir"] - 270.0)))
    best_l = (r["diff"], "love spot only", r)
    out = {}
    for key, (score, cname, r) in (("matched", best_m), ("love_spot", best_l)):
        out[key] = dict(condition=cname, score=float(score), **r,
                        rel_diff=float(r["diff"] / max(0.5 * (r["amp_male"] + r["amp_female"]), 1e-9)),
                        muscle_share=float(1.0 - r["diff_cut"] / max(r["diff"], 1e-9)))
    return out


def position_map(models: dict, direction, radius=12.0, speed=30.0, wavelength=20.0,
                 az=np.arange(-75.0, 75.1, 15.0), els=np.arange(-45.0, 60.1, 15.0), mio_pull=0.0, verbose=True) -> dict:
    """A small grating patch at every position of the bowl: predicted sex difference in retinal
    movement, the male's third-muscle rate, and the same difference with the muscle cut."""
    el = models["male"].el_grid
    D = np.zeros((len(els), len(az))); Dc = np.zeros_like(D); M = np.zeros_like(D)
    AM = np.zeros_like(D); AF = np.zeros_like(D)
    for i, e0 in enumerate(els):
        for j, a0 in enumerate(az):
            c = compare(models, bowl_stimulus(el, direction, speed, wavelength, aperture=(a0, e0, radius)), mio_pull)
            D[i, j], Dc[i, j] = c["diff"], c["diff_cut"]
            M[i, j] = 0.5 * (abs(c["rate_male"].get("MIO_R", 0.0)) + abs(c["rate_male"].get("MIO_L", 0.0)))
            AM[i, j], AF[i, j] = c["amp_male"], c["amp_female"]
        if verbose:
            print(f"el {e0:5.0f}  diff {np.round(D[i], 3)}  MIO {np.round(M[i], 1)}", flush=True)
    return dict(az=az.tolist(), el=els.tolist(), direction=float(direction), radius=float(radius),
                diff=D.tolist(), diff_cut=Dc.tolist(), mio_rate=M.tolist(), amp_male=AM.tolist(), amp_female=AF.tolist())


# ----------------------------------------------------------------------------- closed loop
CL_BOUNDS = {"az": (-60.0, 60.0), "el": (-20.0, 60.0), "rad": (8.0, 30.0), "dir": (0.0, 360.0),
             "speed": (10.0, 80.0), "wl": (10.0, 40.0)}
CL_SIGMA = {"az": 15.0, "el": 12.0, "rad": 5.0, "dir": 40.0, "speed": 12.0, "wl": 6.0}
CL_KEYS = tuple(CL_BOUNDS)


def cl_clip(p):
    q = {}
    for k in CL_KEYS:
        lo, hi = CL_BOUNDS[k]
        q[k] = float(p[k] % 360.0) if k == "dir" else float(np.clip(p[k], lo, hi))
    return q


def cl_movie(el_grid, p):
    return bowl_stimulus(el_grid, p["dir"], p["speed"], p["wl"], aperture=(p["az"], p["el"], p["rad"]))


def closed_loop(animal: BinocularModel, shared: BinocularModel, start: dict, animal_pull: float = 0.0,
                noise: float = 0.02, generations: int = 20, lam: int = 8, mu: int = 3, seed: int = 0,
                log=None, verbose=True) -> dict:
    """Stimulus search with the animal in the loop (in silico).

    Every trial shows one grating patch on the bowl and reads the retinal movement of both eyes
    from the tracker: here the `animal` model plus Gaussian noise of s.d. `noise` on each of the four
    components. The objective is the part of that movement that the shared reflex does not explain:
    the distance to the prediction of `shared` (the model without the third muscle). A (μ, λ)
    evolution strategy proposes the next stimuli; no gradient and no model of the muscle are used.
    The hidden properties of `animal` (which cell drives the muscle, where it pulls) may differ from
    those assumed when `start` was designed.

    Returned per generation: the search mean, its measured objective and its true objective
    (noise-free; available only in simulation)."""
    rng = np.random.default_rng(seed)
    el = animal.el_grid
    cache = {}

    def predicted(p):
        return respond(shared, cl_movie(el, p))["shift_cut"]

    def true_shift(p):
        return respond(animal, cl_movie(el, p), animal_pull)["shift"]

    def trial(p):
        key = tuple(round(p[k], 3) for k in CL_KEYS)
        if key not in cache:
            cache[key] = (true_shift(p), predicted(p))
        s, f = cache[key]
        return difference(s + rng.normal(0.0, noise, 4), f), difference(s, f)

    mean = cl_clip(start)
    sigma = dict(CL_SIGMA)
    hist = []
    j_meas, j_true = trial(mean)
    hist.append(dict(gen=0, trials=1, mean=dict(mean), measured=j_meas, true=j_true))
    n_trials = 1
    for g in range(1, generations + 1):
        kids = []
        for _ in range(lam):
            q = cl_clip({k: mean[k] + rng.normal(0.0, sigma[k]) for k in CL_KEYS})
            kids.append((trial(q)[0], q))
        n_trials += lam
        kids.sort(key=lambda x: -x[0])
        best = [q for _, q in kids[:mu]]
        new = {k: float(np.mean([q[k] for q in best])) for k in CL_KEYS}
        ang = np.deg2rad([q["dir"] for q in best])                       # circular mean of the direction
        new["dir"] = float(np.rad2deg(np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())) % 360.0)
        mean = cl_clip(new)
        sigma = {k: v * 0.93 for k, v in sigma.items()}
        j_meas, j_true = trial(mean)
        n_trials += 1
        hist.append(dict(gen=g, trials=n_trials, mean=dict(mean), measured=j_meas, true=j_true))
        if verbose:
            print(f"gen {g:2d} trials {n_trials:3d}  true {j_true:.3f}  measured {j_meas:.3f}  "
                  + " ".join(f"{k} {mean[k]:.0f}" for k in CL_KEYS), flush=True)
        if log:
            pathlib.Path(log).write_text(json.dumps(hist, indent=1))
    return dict(history=hist, noise=noise, lam=lam, mu=mu, generations=generations, seed=seed, start=cl_clip(start))


# ----------------------------------------------------------------------------- collected results
MATCHED = ("bowl without love spot", 270.0)      # the grating everywhere but in the love spot, drifting downward
LOVE = ("love spot only", 90.0)                  # the grating only in the love spot, drifting upward


def _row(scan_res, cond, d):
    return [x for x in scan_res[cond] if x["dir"] == d][0]


def _summary(r):
    return dict(amp_female=r["amp_female"], amp_male=r["amp_male"], amp_male_cut=r["amp_male_cut"], diff=r["diff"],
                diff_cut=r["diff_cut"], rel_diff=r["diff"] / (0.5 * (r["amp_male"] + r["amp_female"])),
                ratio=r["amp_male"] / r["amp_female"], ratio_cut=r["amp_male_cut"] / r["amp_female"],
                muscle_share=1.0 - r["diff_cut"] / r["diff"],
                mio_rate=[r["rate_male"].get("MIO_R", 0.0), r["rate_male"].get("MIO_L", 0.0)])


def collect(raw=HERE / "results_raw", out=HERE / "bowl_result.json"):
    """Merge the raw runs into the one file that figures, tests and the proposal read.

    raw/bowl_main.json        python -m hover.bowl --scan --map --map-dir 90
    raw/bowl_apertures.json   python -m hover.bowl --apertures
    raw/bowl_alt_<X>.json     python -m hover.bowl --scan --mio-from <X>      (X = HSNE, HS, VS)
    raw/cl_*.json             python -m hover.bowl --closed-loop <scenario> --noise <s> --seed <k>
    """
    raw = pathlib.Path(raw)
    main_ = json.loads((raw / "bowl_main.json").read_text())
    res = dict(settings=main_["settings"], scan=main_["scan"], map=main_["map"])
    res["two_stimuli"] = {"matched": dict(condition=MATCHED[0], dir=MATCHED[1], **_summary(_row(main_["scan"], *MATCHED))),
                          "love_spot": dict(condition=LOVE[0], dir=LOVE[1], **_summary(_row(main_["scan"], *LOVE)))}
    apf = raw / "bowl_apertures.json"
    if apf.exists():
        ap = json.loads(apf.read_text())["apertures"]
        res["apertures"] = {c: {f"{int(r['dir'])}": _summary(r) for r in rows} for c, rows in ap.items()}
    alts = {"HSN": dict(matched=_summary(_row(main_["scan"], *MATCHED)), love_spot=_summary(_row(main_["scan"], *LOVE)),
                        full_horizontal=_summary(_row(main_["scan"], "full bowl", 0.0)))}
    for v in ("HSNE", "HS", "VS"):
        f = raw / f"bowl_alt_{v}.json"
        if f.exists():
            sc = json.loads(f.read_text())["scan"]
            alts[v] = dict(matched=_summary(_row(sc, *MATCHED)), love_spot=_summary(_row(sc, *LOVE)),
                           full_horizontal=_summary(_row(sc, "full bowl", 0.0)))
    # no visual drive: the male's muscle does not follow the stimulus, so the male moves as the male with the muscle cut
    m, l = alts["HSN"]["matched"], alts["HSN"]["love_spot"]
    alts["none"] = dict(matched=dict(ratio=m["ratio_cut"]), love_spot=dict(ratio=l["ratio_cut"]))
    res["alternatives"] = alts
    cl = {}
    for f in sorted(raw.glob("cl_*.json")):
        d = json.loads(f.read_text())
        if isinstance(d, dict) and "closed_loop" in d:
            cl.update(d["closed_loop"])
    res["closed_loop"] = cl
    pathlib.Path(out).write_text(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true"); ap.add_argument("--map", action="store_true")
    ap.add_argument("--apertures", action="store_true", help="scan the love-spot aperture radius, grating inside or outside")
    ap.add_argument("--mio-from", default="HSN"); ap.add_argument("--mio", default="independent")
    ap.add_argument("--speed", type=float, default=30.0); ap.add_argument("--wavelength", type=float, default=20.0)
    ap.add_argument("--map-dir", type=float, default=None); ap.add_argument("--map-step", type=float, default=10.0)
    ap.add_argument("--closed-loop", default=None, help="scenario: naive | displaced | wrong_cell")
    ap.add_argument("--noise", type=float, default=0.02); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--generations", type=int, default=20)
    ap.add_argument("--out", default=str(HERE / "bowl_result.json"))
    ap.add_argument("--collect", action="store_true", help="merge results_raw/ into bowl_result.json and stop")
    a = ap.parse_args()
    if a.collect:
        r = collect()
        for k, v in r["two_stimuli"].items():
            print(k, v["condition"], v["dir"], "male/female", round(v["ratio"], 2), "rel. diff", round(v["rel_diff"], 3), "muscle share", round(v["muscle_share"], 2))
        print({k: (round(v["matched"]["ratio"], 2), round(v["love_spot"]["ratio"], 2)) for k, v in r["alternatives"].items()})
        return
    out = pathlib.Path(a.out)
    res = json.loads(out.read_text()) if out.exists() else {}
    res["settings"] = dict(mio_from=a.mio_from, mio=a.mio, speed=a.speed, wavelength=a.wavelength,
                           bowl_az=BOWL_AZ, bowl_el=BOWL_EL, love_spot=LOVE_SPOT)
    models = make_models(a.mio_from, a.mio)
    t0 = time.time()
    if a.scan:
        res["scan"] = scan(models, a.speed, a.wavelength)
        res["pick"] = pick(res["scan"])
        for k, v in res["pick"].items():
            print(k, v["condition"], "dir", v["dir"], "male", round(v["amp_male"], 3), "female", round(v["amp_female"], 3),
                  "rel diff", round(v["rel_diff"], 3), "muscle share", round(v["muscle_share"], 2))
        out.write_text(json.dumps(res, indent=1))
    if a.apertures:
        res["apertures"] = scan(models, a.speed, a.wavelength, dirs=(0.0, 60.0, 90.0, 120.0, 240.0, 270.0, 300.0), conditions=aperture_conditions())
        out.write_text(json.dumps(res, indent=1))
    if a.map:
        d = a.map_dir if a.map_dir is not None else (res["pick"]["love_spot"]["dir"] if "pick" in res else 90.0)
        res["map"] = position_map(models, d, speed=a.speed, wavelength=a.wavelength,
                                  az=np.arange(-80.0, 80.1, a.map_step), els=np.arange(-45.0, 65.1, a.map_step))
        out.write_text(json.dumps(res, indent=1))
    if a.closed_loop:
        shared = models["male"]            # its `shift_cut` is the prediction for a male without the third muscle
        designed = dict(az=LOVE_SPOT[0], el=LOVE_SPOT[1], rad=LOVE_SPOT[2], dir=90.0, speed=a.speed, wl=a.wavelength)
        oracle = None
        if a.closed_loop == "naive":
            # the animal is as the model assumes; the search starts from an arbitrary stimulus
            animal, pull = models["male"], 0.0
            start = dict(az=40.0, el=0.0, rad=15.0, dir=200.0, speed=30.0, wl=20.0)
            oracle = designed
        elif a.closed_loop == "displaced":
            # the animal's love spot lies 20° higher than the model assumes and its muscle pulls at 330°;
            # the search starts from the stimulus designed with the model
            animal, pull = male_with_hsn_field(0.0, 45.0), 330.0
            start = designed
            oracle = dict(designed, el=45.0)
        elif a.closed_loop == "wrong_cell":
            # the animal's muscle is driven by HSNE, not HSN, and pulls at 330°
            animal, pull = BinocularModel("eristalis", "male", mio="independent", mio_from="HSNE"), 330.0
            start = designed
        else:
            raise SystemExit("unknown scenario")
        el = animal.el_grid
        J = lambda p: difference(respond(animal, cl_movie(el, p), pull)["shift"], respond(shared, cl_movie(el, p))["shift_cut"])
        r = closed_loop(animal, shared, start, pull, noise=a.noise, generations=a.generations, seed=a.seed,
                        log=str(out) + ".log.json")
        r["designed_stimulus_true"] = J(designed); r["scenario"] = a.closed_loop
        if oracle:
            r["oracle_true"] = J(oracle); r["oracle"] = oracle
        res.setdefault("closed_loop", {})[f"{a.closed_loop}_noise{a.noise:g}_seed{a.seed}"] = r
        out.write_text(json.dumps(res, indent=1))
    print(f"done in {time.time() - t0:.0f} s -> {out}")


if __name__ == "__main__":
    main()
