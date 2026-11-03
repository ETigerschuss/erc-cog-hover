"""Controversial stimuli for the male *Eristalis* MIO, computed with the Tier-1 biophysical model.

Pipeline:  stimulus (T, 16, 32 field)  ->  T4/T5 motion maps (hover.emd)  ->  receptive-field pooling
           ->  LPTC input currents  ->  Tier-1 HH circuit (hover.tier1_hh, ported from MESH)
           ->  motor-neuron rates  ->  retinal displacement by the vector-sum oculomotor model
              (Falt et al. 2026) under alternative MIO pull-direction hypotheses.

Question answered here: which visual stimulus makes the *predicted retinal trajectories* under two
hypotheses about the MIO's pull direction diverge most, i.e. which stimulus is worth presenting to
a tethered male? The search (a (1+lambda) evolution strategy over a two-region stimulus) maximises the
angle between the predicted displacement directions, which requires the MIO to be driven while the
shared MOT/MOS channel is nulled. All receptive fields and pull directions are stated below and are
placeholders to be replaced by WP2 measurements.

Usage:  python -m hover.mio_search [--quick]   ->  prints the stimulus and writes
        ../proposal/figures/fig_B1e_mio_controversial.png  and  mio_search_result.json
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

from .emd import t4t5_layer
from .tier1_hh import DT, build_circuit, displacement, simulate, spike_rate

FIELD = (16, 32)          # rows: 0 dorsal ... 15 ventral; cols: 0 frontal midline ... 31 lateral/back
FRAME_DT = 1.0 / 120.0    # stimulus frame rate (s)
PRE_MS, STIM_MS, POST_MS = 200.0, 500.0, 200.0

# Pull directions (retinal displacement, degrees; 0 = front, 90 = up), Falt et al. 2026 for MOS/MOT.
PULL = {"MOS": 51.0, "MOT": 320.0}
MIO_HYPOTHESES = {"MIO frontal (0°)": 0.0, "MIO dorsal (90°)": 90.0}


def _rf(rows, cols):
    m = np.zeros(FIELD)
    m[rows[0]:rows[1], cols[0]:cols[1]] = 1.0
    return m


# Receptive fields (male Eristalis, placeholders from Nordström et al. 2008 and Drosophila VS/HS layout).
# channel: 'h' (+ = front-to-back) or 'v' (+ = downward). HS cells prefer front-to-back, VS prefer downward.
RFS = {
    "HSN":  (_rf((0, 5), (0, 10)), "h", +1.0),    # dimorphic: narrow dorso-frontal field in males
    "HSNE": (_rf((0, 8), (0, 16)), "h", +1.0),    # dorso-frontal, isomorphic
    "HSE":  (_rf((5, 11), (0, 32)), "h", +1.0),
    "HSS":  (_rf((10, 16), (0, 32)), "h", +1.0),
    "VS1":  (_rf((0, 16), (0, 8)), "v", +1.0),
    "VS2":  (_rf((0, 16), (8, 16)), "v", +1.0),
    "VS3":  (_rf((0, 16), (16, 24)), "v", +1.0),
    "VS4":  (_rf((0, 16), (24, 32)), "v", +1.0),
}

BOUNDS = {  # two-region stimulus: a disc patch A on a background B
    "row": (1.0, 7.0), "col": (1.0, 14.0), "radius": (2.0, 7.0),
    "dir_a": (0.0, 360.0), "vel_a": (4.0, 40.0),
    "dir_b": (0.0, 360.0), "vel_b": (0.0, 40.0), "contrast_b": (0.0, 1.0),
}


def render(p: dict, duration=STIM_MS / 1000.0, dt=FRAME_DT, wavelength=8.0) -> np.ndarray:
    T = int(round(duration / dt))
    H, W = FIELD
    rr, cc = np.mgrid[0:H, 0:W].astype(float)
    t = np.arange(T)[:, None, None] * dt

    def grat(direction, velocity, contrast):
        th = np.deg2rad(direction)
        proj = cc * np.cos(th) + rr * np.sin(th)
        return 0.5 + 0.5 * contrast * np.sin(2 * np.pi * (proj[None] - velocity * t) / wavelength)

    a = grat(p["dir_a"], p["vel_a"], 1.0)
    b = grat(p["dir_b"], p["vel_b"], p["contrast_b"])
    mask = ((rr - p["row"]) ** 2 + (cc - p["col"]) ** 2) <= p["radius"] ** 2
    return np.where(mask[None], a, b)


I_POS, I_NEG = 15.0, 7.0   # saturation of the LPTC drive (MESH stimulus units): HS cells depolarise
                            # by ~10 mV for preferred motion and hyperpolarise less for null motion


def lptc_currents(stim: np.ndarray, gain: float) -> dict[str, np.ndarray]:
    """Per-frame input current for each LPTC from T4/T5 maps pooled over its receptive field,
    passed through an asymmetric saturating nonlinearity (tanh), as in graded LPTC responses."""
    maps = t4t5_layer(stim, FRAME_DT)
    out = {}
    for nm, (rf, ch, sign) in RFS.items():
        m = maps[ch]
        r = rf[:, :-1] if ch == "h" else rf[:-1, :]
        x = gain * sign * (m * r).sum(axis=(1, 2)) / max(r.sum(), 1.0)
        out[nm] = np.where(x >= 0, I_POS * np.tanh(x / I_POS), I_NEG * np.tanh(x / I_NEG))
    return out


def calibrate_coupling(target_dhz: float = 20.0, candidates=(0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5)) -> float:
    """Smallest LPTC<->MN gap-junction conductance for which +I_POS into all HS cells raises the MOT
    rate by at least `target_dhz` Hz: the RMN tuning in Falt et al. 2026 spans tens of Hz."""
    for g in candidates:
        c = build_circuit("eristalis_male", "HSN", g_lptc_mn=g)
        names = c[0]
        hs = [names.index(n) for n in names if n.startswith("HS")]

        def inj(tm):
            I = np.zeros(len(names))
            if 200 <= tm < 700:
                I[hs] = I_POS
            return I

        t, V = simulate(c, inj, 900.0, noise=0.0)
        r = spike_rate(V[:, names.index("MOT")])
        d = r[int(300 / DT):int(690 / DT)].mean() - r[int(60 / DT):int(190 / DT)].mean()
        if d >= target_dhz:
            return g
    return candidates[-1]


def calibrate_gain(target_current: float = 10.0) -> float:
    """Gain such that a full-field front-to-back grating drives HSE with `target_current`
    (the MESH default stimulus amplitude; about +15 mV in the HS model)."""
    p = dict(row=8, col=16, radius=0.1, dir_a=0, vel_a=16, dir_b=0, vel_b=16, contrast_b=1.0)
    maps = t4t5_layer(render(p), FRAME_DT)
    rf = RFS["HSE"][0][:, :-1]
    x = (maps["h"] * rf).sum(axis=(1, 2)) / rf.sum()
    steady = x[len(x) // 3:].mean()
    return 1.5 * target_current / steady   # 1.5x so that a strong stimulus sits in the saturating range


def run_model(circuit, p: dict, gain: float, noise: float = 0.0, seed: int = 0):
    names = circuit[0]
    cur = lptc_currents(render(p), gain)
    n_frames = next(iter(cur.values())).shape[0]
    total = PRE_MS + STIM_MS + POST_MS

    def I_ext(t_ms):
        I = np.zeros(len(names))
        if PRE_MS <= t_ms < PRE_MS + STIM_MS:
            k = min(int((t_ms - PRE_MS) / 1000.0 / FRAME_DT), n_frames - 1)
            for nm, c in cur.items():
                if nm in names:
                    I[names.index(nm)] = c[k]
        return I

    t, V = simulate(circuit, I_ext, total, pre_roll_ms=500.0, noise=noise, seed=seed)
    rates = {nm: spike_rate(V[:, names.index(nm)]) for nm in ("MOT", "MOS", "MIO") if nm in names}
    base_sl = slice(int(50 / DT), int((PRE_MS - 20) / DT))
    baseline = {nm: float(r[base_sl].mean()) for nm, r in rates.items()}
    return t, V, rates, baseline


def predicted_directions(rates, baseline, mio_deg: float | None):
    """Mean displacement direction (deg) and magnitude during the stimulus window."""
    pull = dict(PULL)
    if mio_deg is not None and "MIO" in rates:
        pull["MIO"] = mio_deg
    sl = slice(int((PRE_MS + 80) / DT), int((PRE_MS + STIM_MS) / DT))
    vec = np.zeros(2)
    for nm, th in pull.items():
        w = ((rates[nm] - baseline[nm]) / max(baseline[nm], 1e-6))[sl].mean()
        vec += w * np.array([np.cos(np.deg2rad(th)), np.sin(np.deg2rad(th))])
    return float(np.rad2deg(np.arctan2(vec[1], vec[0])) % 360), float(np.linalg.norm(vec))


def objective(circuit, p: dict, gain: float, hyp=MIO_HYPOTHESES, min_mio_hz: float = 10.0):
    """Angle (deg) between the predicted displacement directions under the two MIO hypotheses,
    scaled down when the MIO itself is barely driven (|delta rate| < min_mio_hz)."""
    t, V, rates, baseline = run_model(circuit, p, gain)
    dirs = [predicted_directions(rates, baseline, th)[0] for th in hyp.values()]
    d = abs((dirs[0] - dirs[1] + 180) % 360 - 180)
    sl = slice(int((PRE_MS + 80) / DT), int((PRE_MS + STIM_MS) / DT))
    dmio = abs(rates["MIO"][sl].mean() - baseline["MIO"])
    return d * min(1.0, dmio / min_mio_hz), dict(angle=d, d_mio=dmio, rates=rates, baseline=baseline, t=t, V=V)


def search(circuit, gain, generations=14, lam=6, seed=1, log=print):
    rng = np.random.default_rng(seed)
    keys = list(BOUNDS)
    lo = np.array([BOUNDS[k][0] for k in keys]); hi = np.array([BOUNDS[k][1] for k in keys])
    to_p = lambda x: dict(zip(keys, [float(v) for v in x]))
    # seeded start: patch on the HSN field moving front-to-back, background grey
    x = np.array([2.5, 4.0, 4.0, 0.0, 16.0, 180.0, 16.0, 0.0])
    best, info = objective(circuit, to_p(x), gain)
    sigma = 0.25 * (hi - lo)
    hist = [best]
    for g in range(generations):
        cands = np.clip(x + sigma * rng.standard_normal((lam, len(keys))), lo, hi)
        scores = []
        for c in cands:
            s, _ = objective(circuit, to_p(c), gain)
            scores.append(s)
        i = int(np.argmax(scores))
        if scores[i] > best:
            x, best = cands[i], scores[i]; sigma *= 1.2
        else:
            sigma *= 0.85
        hist.append(best)
        log(f"gen {g+1:2d}: best objective {best:6.1f}")
    best, info = objective(circuit, to_p(x), gain)
    return to_p(x), best, hist, info


def main(quick=False, replot=False):
    here = pathlib.Path(__file__).resolve()
    figdir = here.parents[2] / "proposal" / "figures"
    result_file = here.parent / "mio_search_result.json"
    if replot and result_file.exists():
        prev = json.loads(result_file.read_text())
        gain, g_mn = prev["gain"], prev["g_lptc_mn"]
    else:
        gain = calibrate_gain()
        g_mn = calibrate_coupling()
    print(f"front-end gain = {gain:.3g}; LPTC<->MN gap-junction conductance = {g_mn}")
    male = build_circuit("eristalis_male", "HSN", g_lptc_mn=g_mn)
    female = build_circuit("eristalis_female", g_lptc_mn=g_mn)
    if replot and result_file.exists():
        p = prev["stimulus"]; hist = prev["history"]
        score, info = objective(male, p, gain)
    else:
        p, score, hist, info = search(male, gain, generations=4 if quick else 14, lam=4 if quick else 6)
    print("best stimulus:", {k: round(v, 2) for k, v in p.items()})
    print(f"angle between predicted directions: {info['angle']:.1f} deg; MIO delta rate {info['d_mio']:.1f} Hz")
    # reference: female circuit (no MIO) on the same stimulus
    tf, Vf, rf, bf = run_model(female, p, gain)
    res = {
        "stimulus": p, "objective": score, "history": hist, "gain": gain, "g_lptc_mn": g_mn,
        "pull_directions": PULL, "mio_hypotheses": MIO_HYPOTHESES,
        "male": {h: predicted_directions(info["rates"], info["baseline"], th) for h, th in MIO_HYPOTHESES.items()},
        "female": predicted_directions(rf, bf, None),
        "baseline_rates": info["baseline"],
        "stim_rates": {nm: float(r[int((PRE_MS + 80) / DT):int((PRE_MS + STIM_MS) / DT)].mean()) for nm, r in info["rates"].items()},
    }
    result_file.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ("history",)}, indent=1))
    try:
        make_panel(p, gain, info, (rf, bf), figdir / "fig_B1e_mio_controversial.png", male[0])
    except Exception as e:  # pragma: no cover
        print("panel not drawn:", e)


def make_panel(p, gain, info, female, out_png, names):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Rectangle

    V, t = info["V"], info["t"]
    rates = {nm: spike_rate(V[:, names.index(nm)], kernel="gauss", win_ms=25.0) for nm in ("MOT", "MOS", "MIO")}
    baseline = info["baseline"]
    cur = lptc_currents(render(p), gain)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), dpi=300, gridspec_kw=dict(width_ratios=[1.0, 1.35, 1.0]))
    # (1) stimulus map with receptive fields
    ax = axes[0]
    H, W = FIELD
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.set_aspect("equal")
    ax.set_title("controversial stimulus", fontsize=9)
    for nm, col in (("HSE", "#c2185b"), ("HSS", "#c2185b"), ("HSNE", "#ad1457"), ("HSN", "#2F5597")):
        rf = RFS[nm][0]; rows = np.where(rf.any(1))[0]; cols = np.where(rf.any(0))[0]
        ax.add_patch(Rectangle((cols[0], rows[0]), cols[-1] - cols[0] + 1, rows[-1] - rows[0] + 1,
                               fill=False, ec=col, lw=1.0 if nm != "HSN" else 2.0, ls="--" if nm != "HSN" else "-"))
        ax.text(cols[0] + 0.3, rows[0] + 1.3, nm, fontsize=6, color=col)
    ax.add_patch(Circle((p["col"], p["row"]), p["radius"], fc="#FFE27A", ec="#8A6D00", alpha=0.6))
    for (x0, y0, d, v, lab) in ((p["col"], p["row"], p["dir_a"], p["vel_a"], "A: patch"),
                                (W * 0.7, H * 0.72, p["dir_b"], p["vel_b"] * p["contrast_b"], "B: background")):
        L = 0.12 * v + 0.6
        ax.annotate("", xy=(x0 + L * np.cos(np.deg2rad(d)), y0 + L * np.sin(np.deg2rad(d))), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", lw=1.6, color="k"))
        ax.text(x0, y0 + 2.2 if lab.startswith("A") else y0 - 1.1, lab, fontsize=6, ha="center")
    ax.text(0.3, H - 0.6, f"A: {p['dir_a']:.0f}°, {p['vel_a']:.0f} px/s · B: {p['dir_b']:.0f}°, contrast {p['contrast_b']:.2f}",
            fontsize=5.5, color="#444")
    ax.set_xlabel("azimuth (front → back)", fontsize=7); ax.set_ylabel("elevation (dorsal → ventral)", fontsize=7)
    ax.tick_params(labelsize=6)
    # (2) LPTC drive (top) and motor-neuron rates (bottom)
    ax = axes[1]
    ax.set_title("Tier-1 model: LPTC drive and motor-neuron rates", fontsize=9)
    ax.axis("off")
    inner = ax.inset_axes([0.0, 0.58, 1.0, 0.42]); lower = ax.inset_axes([0.0, 0.0, 1.0, 0.50])
    tf = PRE_MS / 1000.0 + np.arange(next(iter(cur.values())).shape[0]) * FRAME_DT
    for nm, col, ls in (("HSN", "#2F5597", "-"), ("HSNE", "#ad1457", "-"), ("HSE", "#c2185b", "--"), ("HSS", "#c2185b", ":")):
        inner.plot(tf, cur[nm], color=col, lw=1.0, ls=ls, label=nm)
    vs = np.mean([cur[f"VS{k}"] for k in range(1, 5)], axis=0)
    inner.plot(tf, vs, color="#ef6c00", lw=1.0, label="VS1–4 mean")
    inner.axhline(0, color="#999", lw=0.5)
    inner.set_xlim(0, (PRE_MS + STIM_MS + POST_MS) / 1000.0); inner.set_ylabel("LPTC input", fontsize=6)
    inner.legend(fontsize=5, frameon=False, ncol=3, loc="upper right"); inner.tick_params(labelsize=5)
    tt = t / 1000.0
    sl = slice(int(60 / DT), int((PRE_MS + STIM_MS + POST_MS - 80) / DT))
    lower.plot(tt[sl], rates["MOT"][sl], color="#6a1b9a", lw=2.4, label="MOT")
    lower.plot(tt[sl], rates["MOS"][sl], color="#2e7d32", lw=1.6, ls="--", label="MOS")
    lower.plot(tt[sl], rates["MIO"][sl], color="#c62828", lw=1.0, ls=":", label="MIO")
    lower.axvspan(PRE_MS / 1000, (PRE_MS + STIM_MS) / 1000, color="#FFE27A", alpha=0.35, lw=0)
    lower.set_xlim(0, (PRE_MS + STIM_MS + POST_MS) / 1000.0)
    lower.set_xlabel("time (s)", fontsize=7); lower.set_ylabel("rate (Hz)", fontsize=6)
    lower.legend(fontsize=5.5, frameon=False, ncol=3, loc="lower right"); lower.tick_params(labelsize=5)
    lower.text(0.01, 0.95, "the three motor neurons co-vary: the stimulus drives HS cells only",
               transform=lower.transAxes, fontsize=5, va="top", color="#444")
    # (3) predicted retinal displacement directions
    ax = axes[2]
    ax.set_aspect("equal"); ax.set_title("predicted retinal shift", fontsize=9)
    ax.axhline(0, color="#ccc", lw=0.6); ax.axvline(0, color="#ccc", lw=0.6)
    handles = []
    for lab, th, col, lw in ((list(MIO_HYPOTHESES)[0], list(MIO_HYPOTHESES.values())[0], "#c62828", 2.4),
                             (list(MIO_HYPOTHESES)[1], list(MIO_HYPOTHESES.values())[1], "#ef6c00", 2.4)):
        d, m = predicted_directions(rates, baseline, th)
        ax.annotate("", xy=(m * np.cos(np.deg2rad(d)), m * np.sin(np.deg2rad(d))), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", lw=lw, color=col))
        handles.append(Line2D([0], [0], color=col, lw=lw, label=f"♂ {lab}: {d:.0f}°"))
    rf, bf = female
    rfs = {nm: spike_rate(rf_v, kernel="gauss", win_ms=25.0) if False else rf_v for nm, rf_v in rf.items()}
    d, m = predicted_directions(rfs, bf, None)
    ax.annotate("", xy=(m * np.cos(np.deg2rad(d)), m * np.sin(np.deg2rad(d))), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#555", ls="--"))
    handles.append(Line2D([0], [0], color="#555", lw=1.4, ls="--", label=f"♀ circuit (no MIO): {d:.0f}°"))
    lim = max(0.05, 1.4 * max(predicted_directions(rates, baseline, th)[1] for th in MIO_HYPOTHESES.values()))
    ax.set_xlim(-lim * 0.3, lim); ax.set_ylim(-lim * 0.3, lim)
    ax.legend(handles=handles, fontsize=6, frameon=False, loc="upper left")
    ax.set_xlabel("← back    front →", fontsize=7); ax.set_ylabel("← down    up →", fontsize=7); ax.tick_params(labelsize=6)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=300)
    print("wrote", out_png)


if __name__ == "__main__":
    main(quick="--quick" in sys.argv, replot="--replot" in sys.argv)
