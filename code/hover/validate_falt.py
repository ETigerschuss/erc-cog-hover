"""Validate the Drosophila female model against Falt et al. 2026 and draw the validation figure.

Targets (holder frame, 0° = back-to-front, 90° = dorsal):
  MOS RMN PD 212 ± 2°, MOT RMN PD 141 ± 2° (divergence ≈ 72°); MOT PD within 8° of the HS
  population PD; MOS PD within 6.4° of the 4/7·VS1-4 + 3/7·HS linear sum; OKR: inverted
  retinal-shift direction = stimulus direction (R² 0.994, slope 1.01, mean error 7.07°).
The holder frame is rotated by β relative to the anatomical eye frame (head pitch in the holder);
β is the only fitted parameter of the comparison.
"""
from __future__ import annotations

import json
import time

import numpy as np

from .eye import grating_movie
from .oculomotor import angle_between, direction, model_to_falt, preferred_direction, pull_model
from .species import Model

TARGET = {"MOS": 212.0, "MOT": 141.0}


def direction_tuning(model: Model, dirs=tuple(range(0, 360, 30)), speed=30.0, wavelength=30.0,
                     duration=1.25, onset=0.25, verbose=True):
    rows = []
    t0 = time.time()
    for d in dirs:
        mov = grating_movie(model.az_grid, model.el_grid, d, speed, wavelength, duration, model.dt_frame, onset=onset)
        r = model.run(mov, onset_s=onset)
        rows.append(dict(dir=float(d), d_rate=r["d_rate"], baseline=r["baseline"], lptc_dv=r["lptc_dv"], ammer_dv=r["ammer_dv"]))
        if verbose:
            print(f"  dir {d:3d}°  ΔHz " + " ".join(f"{k}:{v:+6.1f}" for k, v in r["d_rate"].items())
                  + "  ΔV " + " ".join(f"{k}:{v:+5.1f}" for k, v in r["lptc_dv"].items()), flush=True)
    if verbose:
        print(f"  ({time.time() - t0:.1f} s)")
    return rows


def shift_vectors(rows, pull):
    vecs = []
    for r in rows:
        v = np.zeros(2)
        for nm, th in pull.items():
            if nm in r["d_rate"]:
                v += r["d_rate"][nm] / max(r["baseline"][nm], 1e-6) * np.array([np.cos(np.deg2rad(th)), np.sin(np.deg2rad(th))])
        vecs.append(v)
    return np.array(vecs)


def okr_error(rows, beta):
    dirs = np.array([r["dir"] for r in rows])
    vecs = shift_vectors(rows, pull_model(None, beta))
    inv = np.array([(direction(v) + 180.0) % 360 for v in vecs])
    err = np.array([angle_between(a, b) for a, b in zip(inv, dirs)])
    return inv, err, np.linalg.norm(vecs, axis=1)


def summarise(rows, model: Model, beta=None):
    dirs = np.array([r["dir"] for r in rows])
    tun = {nm: np.array([r["d_rate"][nm] for r in rows]) for nm in model.motor_neurons}
    tun["HS"] = np.mean([[r["lptc_dv"][n] for n in ("HSN", "HSE", "HSS")] for r in rows], axis=1)
    tun["VS1-4"] = np.mean([[r["lptc_dv"][n] for n in ("VS1", "VS2", "VS3", "VS4")] for r in rows], axis=1)
    for nm in model.lptcs:
        tun[nm] = np.array([r["lptc_dv"][nm] for r in rows])
    pd_model = {k: preferred_direction(dirs, v - v.min()) for k, v in tun.items()}
    hs_n = (tun["HS"] - tun["HS"].min()) / max(np.ptp(tun["HS"]), 1e-9)
    vs_n = (tun["VS1-4"] - tun["VS1-4"].min()) / max(np.ptp(tun["VS1-4"]), 1e-9)
    pd_model["MOT (lin. sum HS)"] = preferred_direction(dirs, hs_n)
    pd_model["MOS (lin. sum 4/7 VS + 3/7 HS)"] = preferred_direction(dirs, 4 / 7 * vs_n + 3 / 7 * hs_n)
    # fit beta: PD errors of MOT and MOS plus the OKR error
    if beta is None:
        best = None
        for b in np.arange(-60, 60.1, 0.5):
            e_pd = np.mean([angle_between(model_to_falt(pd_model[k][0], b), TARGET[k]) for k in TARGET])
            e_okr = okr_error(rows, b)[1].mean()
            cost = e_pd + e_okr
            if best is None or cost < best[0]:
                best = (cost, b)
        beta = float(best[1])
    inv, err, mag = okr_error(rows, beta)
    out = dict(beta=beta, dirs_model=dirs.tolist(), tuning={k: v.tolist() for k, v in tun.items()},
               pd={k: dict(pd_falt=float(model_to_falt(v[0], beta)), pd_model=v[0], dsi=v[1]) for k, v in pd_model.items()},
               okr=dict(inverted_shift_dir=inv.tolist(), abs_error=err.tolist(), mean_abs_error=float(err.mean()),
                        shift_mag=mag.tolist()),
               baseline={nm: float(np.mean([r["baseline"][nm] for r in rows])) for nm in model.motor_neurons})
    out["errors"] = {k: angle_between(out["pd"][k]["pd_falt"], TARGET[k]) for k in TARGET}
    out["divergence_mos_mot"] = angle_between(out["pd"]["MOS"]["pd_falt"], out["pd"]["MOT"]["pd_falt"])
    out["mot_vs_hs"] = angle_between(out["pd"]["MOT"]["pd_falt"], out["pd"]["HS"]["pd_falt"])
    out["mos_vs_linsum"] = angle_between(out["pd"]["MOS"]["pd_falt"], out["pd"]["MOS (lin. sum 4/7 VS + 3/7 HS)"]["pd_falt"])
    return out


def report(s):
    print(f"\nHolder-frame rotation β = {s['beta']:.1f}°")
    print("Preferred directions (holder frame; Falt: MOS 212°, MOT 141°, MOS−MOT ≈ 72°, MOT ≈ HS within 8°):")
    for k, v in s["pd"].items():
        print(f"  {k:32s} PD {v['pd_falt']:6.1f}°   DSI {v['dsi']:.2f}")
    print(f"  errors vs Falt: MOS {s['errors']['MOS']:.1f}°, MOT {s['errors']['MOT']:.1f}°; MOS−MOT divergence {s['divergence_mos_mot']:.1f}°; "
          f"MOT−HS {s['mot_vs_hs']:.1f}°; MOS − linear sum {s['mos_vs_linsum']:.1f}°")
    o = s["okr"]
    print(f"OKR: mean |inverted shift − stimulus| = {o['mean_abs_error']:.1f}° (Falt 7.07°); per direction: "
          + " ".join(f"{e:.0f}" for e in o["abs_error"]))
    print("tonic rates:", {k: round(v) for k, v in s["baseline"].items()})


def figure(model: Model, s, rows, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .eye import east_north
    dirs = np.array(s["dirs_model"])
    th = np.deg2rad(np.r_[dirs, dirs[0]])
    fig = plt.figure(figsize=(13, 3.6))
    # a) eye map with local +h axes and HS/VS fields
    ax = fig.add_subplot(1, 4, 1)
    e = model.eye
    ah, _ = e.axis_angles()
    w_hsn = model.front.specs[0].rf(e.az, e.el)
    sc = ax.scatter(e.az, e.el, c=e.dphi, s=4, cmap="viridis")
    step = 6
    ax.quiver(e.az[::step], e.el[::step], np.cos(np.deg2rad(ah[::step])), np.sin(np.deg2rad(ah[::step])),
              angles="xy", scale_units="xy", scale=0.12, width=0.004, color="k", alpha=0.6)
    ax.set_xlabel("azimuth (°)"); ax.set_ylabel("elevation (°)"); ax.set_aspect("equal")
    ax.set_title(f"a  eye map, {e.n} ommatidia, local +h axes", fontsize=9, loc="left")
    plt.colorbar(sc, ax=ax, fraction=0.04, label="Δφ (°)")
    # b) LPTC tuning
    ax = fig.add_subplot(1, 4, 2, projection="polar")
    for nm, c in (("HSN", "C3"), ("HSE", "C1"), ("HSS", "C8"), ("VS1", "C0"), ("VS2", "C9"), ("VS3", "C2"), ("VS4", "C4")):
        v = np.array(s["tuning"][nm]); v = v - v.min()
        ax.plot(th, np.r_[v, v[0]], color=c, lw=1.2, label=nm)
    ax.set_theta_zero_location("E"); ax.set_title("b  LPTC tuning (Tier-1 ΔV, model frame)", fontsize=9, loc="left")
    ax.legend(fontsize=6, loc="lower left", bbox_to_anchor=(-0.25, -0.2), ncol=2, frameon=False)
    # c) RMN tuning in holder frame with Falt PDs
    ax = fig.add_subplot(1, 4, 3, projection="polar")
    thf = np.deg2rad(model_to_falt(np.r_[dirs, dirs[0]], s["beta"]))
    for nm, c in (("MOT", "C3"), ("MOS", "C0")):
        v = np.array(s["tuning"][nm]); v = v - v.min()
        ax.plot(thf, np.r_[v, v[0]], color=c, lw=1.5, label=f"{nm} model PD {s['pd'][nm]['pd_falt']:.0f}°")
        ax.annotate("", xy=(np.deg2rad(TARGET[nm]), v.max()), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=c, lw=2, ls="--"))
    ax.set_theta_zero_location("E"); ax.set_theta_direction(1)
    ax.set_title(f"c  RMN tuning, holder frame (β = {s['beta']:.0f}°); dashed: Falt PDs", fontsize=9, loc="left")
    ax.legend(fontsize=6, loc="lower left", bbox_to_anchor=(-0.25, -0.2), frameon=False)
    # d) OKR
    ax = fig.add_subplot(1, 4, 4)
    inv = np.array(s["okr"]["inverted_shift_dir"])
    ax.plot([0, 360], [0, 360], "k--", lw=0.8)
    ax.scatter(dirs, inv, c="C3", s=25, zorder=3)
    ax.set_xlabel("stimulus direction (°)"); ax.set_ylabel("inverted retinal shift (°)")
    ax.set_xticks(range(0, 361, 90)); ax.set_yticks(range(0, 361, 90))
    ax.set_title(f"d  OKR: mean error {s['okr']['mean_abs_error']:.1f}° (Falt 7.1°)", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    print("figure:", out_png)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--g", type=float, default=0.5)
    ap.add_argument("--yaw", type=float, default=0.4)
    ap.add_argument("--leak", type=float, default=50.0)
    ap.add_argument("--beta", type=float, default=None)
    ap.add_argument("--wvs", type=float, default=1.0)
    ap.add_argument("--step", type=int, default=30)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fig", default=None)
    a = ap.parse_args(argv)
    m = Model("drosophila", "female", g_lptc_mn=a.g, yaw_fraction=a.yaw, lptc_leak_scale=a.leak, w_vs_mos=a.wvs)
    print(f"Drosophila female: {m.eye.n} ommatidia, {m.eye.n_patch} local circuits, cells {m.names}, bias "
          + str({nm: round(float(m.P[m.names.index(nm), 7]), 1) for nm in m.motor_neurons}))
    rows = direction_tuning(m, dirs=tuple(range(0, 360, a.step)))
    s = summarise(rows, m, beta=a.beta)
    report(s)
    if a.out:
        json.dump(dict(summary=s, rows=rows, params=vars(a)), open(a.out, "w"), indent=1, default=float)
    if a.fig:
        figure(m, s, rows, a.fig)
    return s


if __name__ == "__main__":
    main()
