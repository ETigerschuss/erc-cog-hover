"""Machine-vision side: an event camera that moves its sensor (simulation behind hypothesis H4a).

An event camera reports only changes of log intensity. On a hovering platform it therefore sees a
moving target but not the static scene it must hold position against. A micro-movement of the
sensor makes the scene visible, and at the same time fills the image with events that can hide the
target. This module measures both effects on the same events, as a function of the size of the
sensor movement:

  scene task    register the static scene between two glances, i.e. measure how far the platform
                has drifted (stabilisation, the task of both sexes)
  target task   find a small dark target that moves across the scene (pursuit, the male's task)

Model. Scene: log intensity of a dead-leaves image (occluding discs, radii ∝ r⁻³, a standard model
of natural-image statistics) plus 1/f texture, blurred by the lens (Gaussian, σ = 0.6 px). Sensor:
N × N pixels; each pixel emits an ON (OFF) event whenever its log intensity has risen (fallen) by
its contrast threshold since its last event (C = 0.2 ± 0.03 between pixels), plus Poisson noise
events. One glance: the sensor sweeps `amp` pixels in a random direction while the target moves
`target_move` pixels in another random direction. All lengths are in pixels, so the results scale
with the pixel pitch (fine pixels in an acute zone, coarse pixels elsewhere).

    python -m hover.eventcam --out hover/eventcam_result.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates, maximum_filter

HERE = pathlib.Path(__file__).resolve().parent
OS = 4                       # oversampling of the scene relative to the pixel grid
N = 128                      # sensor pixels per side
PAD = 40                     # scene margin around the sensor [px]
C_THR, C_SD = 0.20, 0.03     # contrast threshold (log units) and its pixel-to-pixel s.d.
NOISE = 0.03                 # noise events per pixel and glance
PSF = 0.6                    # lens blur, s.d. [px]
AMPS = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0])


# ----------------------------------------------------------------------------- scenes
def dead_leaves(rng, size, rmin=3.0, rmax=80.0, sd=0.4, density=2.5):
    """Log-intensity dead-leaves image (size × size oversampled pixels; radii in sensor pixels)."""
    img = np.zeros((size, size))
    n = int(density * (size / OS) ** 2 / 100)
    u = rng.random(n)
    r = (rmin ** -2 + u * (rmax ** -2 - rmin ** -2)) ** -0.5 * OS       # pdf ∝ r⁻³
    cx, cy = rng.random(n) * size, rng.random(n) * size
    val = rng.normal(0.0, sd, n)
    yy, xx = np.mgrid[0:size, 0:size]
    for i in np.argsort(-r):                                              # large first, small on top
        x0, x1 = int(max(cx[i] - r[i], 0)), int(min(cx[i] + r[i] + 1, size))
        y0, y1 = int(max(cy[i] - r[i], 0)), int(min(cy[i] + r[i] + 1, size))
        m = (xx[y0:y1, x0:x1] - cx[i]) ** 2 + (yy[y0:y1, x0:x1] - cy[i]) ** 2 <= r[i] ** 2
        img[y0:y1, x0:x1][m] = val[i]
    return img


def pink(rng, size, sd=0.15):
    f = np.fft.fftfreq(size)
    k = np.hypot(*np.meshgrid(f, f)); k[0, 0] = 1.0
    x = np.fft.ifft2(np.fft.fft2(rng.normal(size=(size, size))) / k).real
    return x / x.std() * sd


def make_scene(rng, rmin=3.0):
    """Log intensity of the scene as the lens images it (oversampled). The lens blurs intensity;
    the pixel responds to its logarithm."""
    size = (N + 2 * PAD) * OS
    s = dead_leaves(rng, size, rmin=rmin) + pink(rng, size)
    return np.log(gaussian_filter(np.exp(s), PSF * OS, mode="wrap"))


def target_profile(diameter, r):
    """Blurred profile of a disc of the given diameter at radial distance r [px]: the fraction of a
    pixel's light that the target intercepts (disc ⊗ lens blur, evaluated numerically)."""
    g = np.linspace(-6, 6, 241)
    X, Y = np.meshgrid(g, g)
    d = (np.hypot(X, Y) <= 0.5 * diameter).astype(float)
    b = gaussian_filter(d, PSF / (g[1] - g[0]))
    prof = b[120, 120:]                                                   # radial cut, r = 0 … 6 px
    return np.interp(r, g[120:], prof, right=0.0)


# ----------------------------------------------------------------------------- the sensor
class Sensor:
    def __init__(self, rng):
        self.rng = rng
        self.thr = np.clip(rng.normal(C_THR, C_SD, (N, N)), 0.08, None)   # fixed-pattern threshold mismatch
        self.yy, self.xx = np.mgrid[0:N, 0:N].astype(float)

    def view(self, scene, off):
        """Log intensity at the pixels when the sensor is displaced by off = (dx, dy) px."""
        cx = (self.xx + off[0] + PAD + 0.5) * OS - 0.5
        cy = (self.yy + off[1] + PAD + 0.5) * OS - 0.5
        return map_coordinates(scene, [cy, cx], order=1, mode="wrap")

    def glance(self, scene, amp, direction, start=(0.0, 0.0), target=None, step=0.125):
        """One glance: the sensor sweeps `amp` px in `direction` [rad]. target = dict(pos, move,
        diameter, weber): a disc that darkens the scene by the factor (1 + weber) and moves by
        `move` = (dx, dy) px during the glance. Returns the event-count image (ON + OFF events)."""
        u = np.array([np.cos(direction), np.sin(direction)])
        tmove = np.hypot(*target["move"]) if target else 0.0
        n_steps = max(int(np.ceil(max(amp, tmove) / step)), 1)

        def L(k):
            off = np.asarray(start) + u * (amp * k / n_steps)
            v = self.view(scene, off)
            if target:
                p = np.asarray(target["pos"]) + np.asarray(target["move"]) * (k / n_steps) - off   # on the sensor
                r = np.hypot(self.xx - p[0], self.yy - p[1])
                v = v + np.log(1.0 + target["weber"] * target_profile(target["diameter"], r))
            return v
        ref = L(0)
        count = np.zeros((N, N))
        for k in range(1, n_steps + 1):
            d = L(k) - ref
            ev = np.floor(np.abs(d) / self.thr)
            if ev.any():
                ref += np.sign(d) * ev * self.thr
                count += ev
        return count + self.rng.poisson(NOISE, (N, N))


# ----------------------------------------------------------------------------- the two decoders
def target_filter(count, diameter, flank=5):
    """Size-tuned, end-stopped small-target detector: the local event count at the scale of the
    target minus the largest count among eight flanks. An isolated cluster passes; an edge or
    uniform texture is cancelled by the flanks that lie on it (lateral inhibition, as in insect
    small-target detectors)."""
    g = gaussian_filter(count, max(0.5 * diameter, 0.6))
    k = int(round(flank / np.sqrt(2)))
    shifts = ((flank, 0), (-flank, 0), (0, flank), (0, -flank), (k, k), (k, -k), (-k, k), (-k, -k))
    return g - np.max([np.roll(g, s, (0, 1)) for s in shifts], axis=0)


def target_rank(count, track, diameter, margin=12, top=5):
    """Rank of the target among the local maxima of the detector output (1 = the strongest response
    of the image); top + 1 if it is not among the first `top`. `track`: points on the sensor that
    the target passed during the glance."""
    r = target_filter(count, diameter)
    r[:margin] = r[-margin:] = -np.inf; r[:, :margin] = r[:, -margin:] = -np.inf
    iy, ix = np.nonzero((r == maximum_filter(r, size=7)) & np.isfinite(r))
    for rank, j in enumerate(np.argsort(-r[iy, ix])[:top], start=1):
        if min(np.hypot(ix[j] - p[0], iy[j] - p[1]) for p in track) <= diameter + 1.5:
            return rank
    return top + 1


def register(c1, c2, max_shift=10, smooth=1.0):
    """Shift of the scene between two event images: cross-correlation of the smoothed images with
    parabolic sub-pixel refinement."""
    a = gaussian_filter(c1, smooth); b = gaussian_filter(c2, smooth)
    a = a - a.mean(); b = b - b.mean()
    cc = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(a) * np.conj(np.fft.fft2(b))).real)
    c0 = N // 2
    win = cc[c0 - max_shift:c0 + max_shift + 1, c0 - max_shift:c0 + max_shift + 1]
    iy, ix = np.unravel_index(np.argmax(win), win.shape)

    def refine(v, i):
        if 0 < i < len(v) - 1:
            den = v[i - 1] - 2 * v[i] + v[i + 1]
            return i + (0.5 * (v[i - 1] - v[i + 1]) / den if den != 0 else 0.0)
        return float(i)
    return np.array([refine(win[iy], ix) - max_shift, refine(win[:, ix], iy) - max_shift])


# ----------------------------------------------------------------------------- the experiment
def run(n_scenes=200, diameter=2.0, weber=-0.8, target_move=2.0, rmin=3.0, amps=AMPS, seed=0, verbose=True):
    rng = np.random.default_rng(seed)
    top1 = np.zeros(len(amps)); top5 = np.zeros(len(amps)); events = np.zeros(len(amps))
    err = [[] for _ in amps]
    for s in range(n_scenes):
        scene = make_scene(rng, rmin)
        sensor = Sensor(rng)
        pos = rng.uniform(30, N - 30, 2)
        w = rng.uniform(0, 2 * np.pi)
        tgt = dict(pos=pos, move=target_move * np.array([np.cos(w), np.sin(w)]), diameter=diameter, weber=weber)
        drift = rng.uniform(-6, 6, 2)                # platform drift between the two glances [px]
        direction = rng.uniform(0, 2 * np.pi)
        u = np.array([np.cos(direction), np.sin(direction)])
        for i, a in enumerate(amps):
            c1 = sensor.glance(scene, a, direction, target=tgt)
            track = [pos + tgt["move"] * f - u * a * f for f in np.linspace(0, 1, 9)]
            rank = target_rank(c1, track, diameter)
            top1[i] += rank == 1; top5[i] += rank <= 5
            c0 = sensor.glance(scene, a, direction)                     # scene task: no target
            c2 = sensor.glance(scene, a, direction, start=tuple(drift))
            err[i].append(float(np.hypot(*(register(c0, c2) - drift))))
            events[i] += c0.sum() / N ** 2
        if verbose and (s + 1) % 25 == 0:
            print(f"scene {s + 1}/{n_scenes}", flush=True)
    return dict(amps=list(map(float, amps)), n_scenes=n_scenes, diameter=diameter, weber=weber,
                target_move=target_move, rmin=rmin, events_per_pixel=(events / n_scenes).tolist(),
                target_top1=(top1 / n_scenes).tolist(), target_top5=(top5 / n_scenes).tolist(),
                reg_median=[float(np.median(e)) for e in err],
                reg_ok=[float(np.mean(np.asarray(e) < 0.25)) for e in err])


def example(seed=3, diameter=2.0, weber=-0.8, target_move=2.0, amps=(0.0, 1.0, 8.0)):
    """Event images of one scene for three sizes of the sensor movement (for the figure)."""
    rng = np.random.default_rng(seed)
    scene = make_scene(rng)
    sensor = Sensor(rng)
    pos = np.array([N * 0.62, N * 0.40])
    tgt = dict(pos=pos, move=np.array([target_move, 0.0]), diameter=diameter, weber=weber)
    img = sensor.view(scene, (0.0, 0.0)) + np.log(1.0 + weber * target_profile(diameter, np.hypot(sensor.xx - pos[0], sensor.yy - pos[1])))
    return dict(image=img, pos=pos, amps=list(amps),
                counts=[sensor.glance(scene, a, np.deg2rad(60.0), target=tgt) for a in amps])


CONDITIONS = {"default": {}, "target_1px": dict(diameter=1.0), "target_4px": dict(diameter=4.0),
              "low_contrast": dict(weber=-0.5), "sparse_clutter": dict(rmin=8.0), "fast_target": dict(target_move=4.0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--only", nargs="*", default=None, help="conditions to run: " + ", ".join(CONDITIONS))
    ap.add_argument("--out", default=str(HERE / "eventcam_result.json"))
    a = ap.parse_args()
    t0 = time.time()
    out = pathlib.Path(a.out)
    for name in (a.only or CONDITIONS):
        r = run(a.n, verbose=False, **CONDITIONS[name])
        res = json.loads(out.read_text()) if out.exists() else {}
        res[name] = r
        out.write_text(json.dumps(res, indent=1))
        print(name, "\n  amp      ", r["amps"], "\n  target   ", np.round(r["target_top1"], 2), "\n  top 5    ", np.round(r["target_top5"], 2),
              "\n  scene ok ", np.round(r["reg_ok"], 2), "\n  reg err  ", np.round(r["reg_median"], 2),
              "\n  events/px", np.round(r["events_per_pixel"], 2), flush=True)
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
