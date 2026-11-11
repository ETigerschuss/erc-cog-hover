"""Stage 0: eye maps on the sphere. Ommatidial sampling, local lattice axes, virtual neighbours.

The compound eye samples visual space on a sheared hexagonal lattice whose inter-ommatidial angle
Δφ and whose axis orientation vary across the eye (Zhao et al. 2025, Nature 646:135). T4/T5 cells
correlate lattice neighbours, so their preferred directions are the *local* lattice axes: T4a/T5a
(→ HS cells) follow the local +h axis, T4d/T5d (→ VS cells) the local −v axis. Zhao et al. report
that the T4b (= −h) field is globally aligned with yaw rotation plus reverse thrust, i.e. the +h
field is a mixture of the yaw-rotation flow and the expansion flow of forward translation, which
tilts +h upward in the dorso-frontal eye and downward in the ventro-frontal eye.

This module builds, for a species and sex:
  * ommatidial viewing directions on the unit sphere (hexagonal lattice, relaxed to the local Δφ),
  * the local +h and +v unit axes in the tangent plane, expressed in (east = +azimuth, north = +elevation),
  * "virtual neighbours": the points one Δφ away along ±h and ±v, where the detector arms sample,
  * patches of ~25 ommatidia that host one local opponency circuit each (Ammer et al. 2023 model).

Conventions (right eye): azimuth 0° = straight ahead, positive toward the back of the right side;
elevation positive upward. Motion direction 0° = toward +azimuth (front-to-back), 90° = upward.
Values marked [verify] are placeholders to be replaced by measurements (Straw et al. 2006, WP2 µCT).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Field of view of one eye (ellipse in azimuth/elevation): centre, semi-axes [deg]
FOV = {"drosophila": ((72.0, 0.0), 84.0, 66.0), "eristalis": ((72.0, 0.0), 86.0, 72.0)}
GRID_AZ = (-20.0, 165.0)
GRID_EL = (-80.0, 80.0)


# ----------------------------------------------------------------------------- sampling density
def dphi_field(species: str, sex: str):
    """(az, el) -> local inter-ommatidial angle [deg]."""
    if species == "drosophila":
        centre, d0, d1 = (20.0, 0.0), 4.0, 6.2  # Zhao 2025: ≈4° frontal-equatorial, ≈6° lateral/dorsal

        def f(az, el):
            r = np.hypot(az - centre[0], el - centre[1])
            return d0 + (d1 - d0) * np.clip(r / 100.0, 0.0, 1.0)
        return f
    centre, d0, d1 = (15.0, 5.0), 1.6, 3.0  # Eristalis [verify, Straw 2006]

    def f(az, el):
        # The same sampling lattice in both sexes. The male's dorso-frontal region of enlarged facets
        # is a "bright zone": more light per ommatidium, hence faster and more contrast-sensitive
        # motion detection, "without substantially increased spatial resolution" (Straw, Warrant &
        # O'Carroll 2006). It is therefore not modelled as a finer lattice; its higher contrast
        # sensitivity and speed are a detector property to be added from measurements (WP2).
        r = np.hypot(az - centre[0], el - centre[1])
        return d0 + (d1 - d0) * np.clip(r / 100.0, 0.0, 1.0)
    return f


# ----------------------------------------------------------------------------- spherical helpers
def to_xyz(az_deg, el_deg):
    az, el = np.deg2rad(az_deg), np.deg2rad(el_deg)
    return np.stack([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)], axis=-1)


def to_azel(xyz):
    x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    return np.rad2deg(np.arctan2(y, x)), np.rad2deg(np.arcsin(np.clip(z, -1, 1)))


def east_north(xyz):
    """Local east (+az) and north (+el) unit vectors at points xyz (…, 3)."""
    az, el = np.deg2rad(to_azel(xyz)[0]), np.deg2rad(to_azel(xyz)[1])
    e = np.stack([-np.sin(az), np.cos(az), np.zeros_like(az)], -1)
    n = np.stack([-np.sin(el) * np.cos(az), -np.sin(el) * np.sin(az), np.cos(el)], -1)
    return e, n


def h_axis_field(xyz, yaw_fraction: float = 0.4):
    """Local +h axis (front-to-back lattice direction) as a tangent unit vector: a normalised mixture
    of the yaw-rotation flow (along lines of latitude, toward +azimuth) and the expansion flow of
    forward translation (away from the frontal pole). yaw_fraction = 1 gives pure horizontal rows;
    lower values tilt +h upward dorso-frontally and downward ventro-frontally (Zhao 2025, Fig. 4)."""
    e, n = east_north(xyz)
    f = np.array([1.0, 0.0, 0.0])
    exp = xyz * (xyz @ f)[:, None] - f            # tangent vector pointing away from the frontal pole
    nrm = np.linalg.norm(exp, axis=1, keepdims=True)
    exp = np.where(nrm > 1e-6, exp / np.maximum(nrm, 1e-9), e)
    v = yaw_fraction * e + (1.0 - yaw_fraction) * exp
    v -= xyz * (np.sum(v * xyz, axis=1, keepdims=True))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def shear_angle(az, el, amount: float = 12.0, centre=(40.0, 0.0)):
    """Angle α between +h and +v [deg]: < 90° fronto-dorsally and postero-ventrally, > 90° in the
    other quadrants (Zhao 2025 Fig. 3i; range ≈ 75–110°)."""
    dx, dy = np.asarray(az) - centre[0], np.asarray(el) - centre[1]
    return 90.0 + amount * np.tanh(dx * dy / 1500.0)


def rotate_in_tangent(xyz, t, angle_deg):
    """Rotate tangent vectors t about the local normals xyz by angle_deg (counter-clockwise seen
    from outside the sphere)."""
    a = np.deg2rad(angle_deg)[:, None] if np.ndim(angle_deg) else np.deg2rad(angle_deg)
    return np.cos(a) * t + np.sin(a) * np.cross(xyz, t)


def move_along(xyz, t, angle_deg):
    """Points reached by moving from xyz along tangent unit vectors t by angle_deg (great circle)."""
    a = np.deg2rad(angle_deg)[:, None]
    return np.cos(a) * xyz + np.sin(a) * t


# ----------------------------------------------------------------------------- the eye map
@dataclass
class EyeMap:
    species: str
    sex: str
    xyz: np.ndarray           # (N, 3) viewing directions
    az: np.ndarray            # (N,) deg
    el: np.ndarray            # (N,) deg
    dphi: np.ndarray          # (N,) local inter-ommatidial angle, deg
    h_axis: np.ndarray        # (N, 3) tangent unit vector, local +h (front-to-back)
    v_axis: np.ndarray        # (N, 3) tangent unit vector, local +v (upward)
    patch: np.ndarray         # (N,) patch index of the local opponency circuit
    uw: np.ndarray            # (N, 2) integer lattice coordinates of the initial hexagonal lattice

    @property
    def n(self):
        return len(self.az)

    @property
    def n_patch(self):
        return int(self.patch.max()) + 1

    def axis_angles(self):
        """Direction of +h and +v in the (east, north) frame, deg."""
        e, n = east_north(self.xyz)
        ah = np.rad2deg(np.arctan2(np.sum(self.h_axis * n, 1), np.sum(self.h_axis * e, 1)))
        av = np.rad2deg(np.arctan2(np.sum(self.v_axis * n, 1), np.sum(self.v_axis * e, 1)))
        return ah, av

    def inside(self, az_range, el_range):
        return (self.az >= az_range[0]) & (self.az <= az_range[1]) & (self.el >= el_range[0]) & (self.el <= el_range[1])

    def patch_matrix(self):
        """(n_patch, N) averaging matrix."""
        M = np.zeros((self.n_patch, self.n))
        M[self.patch, np.arange(self.n)] = 1.0
        return M / np.maximum(M.sum(1, keepdims=True), 1)


def _hex_lattice_init(species, sex, dphi, max_radius=130.0, n_theta=180, ds=0.1):
    """Hexagonal lattice in the azimuthal-equidistant chart around the acute zone. The radial map
    R(ρ, θ) is obtained by integrating dR/dρ = Δφ(R, θ) along n_theta rays (vectorised), so that the
    radial spacing equals the local Δφ; the relaxation step then equalises the tangential spacing."""
    centre = {"drosophila": (20.0, 0.0)}.get(species, (15.0, 5.0))
    c = to_xyz(*centre)
    e0, n0 = east_north(c[None])[0][0], east_north(c[None])[1][0]
    d_centre = float(dphi(*centre))
    rho_max = max_radius / d_centre * 1.6 + 2
    thetas = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    tdir = np.cos(thetas)[:, None] * e0 + np.sin(thetas)[:, None] * n0       # (n_theta, 3)
    n_s = int(np.ceil(rho_max / ds)) + 1
    R = np.zeros((n_theta, n_s))
    for k in range(1, n_s):
        q = move_along(np.repeat(c[None], n_theta, 0), tdir, R[:, k - 1])
        R[:, k] = R[:, k - 1] + ds * np.asarray(dphi(*to_azel(q)), dtype=float)
    a1 = np.array([1.0, 0.0]); a2 = np.array([0.5, np.sqrt(3) / 2])
    Rl = int(np.ceil(rho_max))
    u, w = np.meshgrid(np.arange(-Rl, Rl + 1), np.arange(-Rl, Rl + 1), indexing="ij")
    u, w = u.ravel(), w.ravel()
    P = u[:, None] * a1 + w[:, None] * a2
    rho = np.linalg.norm(P, axis=1)
    keep = rho <= rho_max
    u, w, P, rho = u[keep], w[keep], P[keep], rho[keep]
    th = np.arctan2(P[:, 1], P[:, 0]) % (2 * np.pi)
    # bilinear interpolation of R in (theta, s)
    ft = th / (2 * np.pi) * n_theta; it = np.floor(ft).astype(int) % n_theta; wt = ft - np.floor(ft)
    fs = np.clip(rho / ds, 0, n_s - 1.001); i_s = np.floor(fs).astype(int); ws = fs - i_s
    it1 = (it + 1) % n_theta
    Rang = ((1 - wt) * (1 - ws) * R[it, i_s] + wt * (1 - ws) * R[it1, i_s]
            + (1 - wt) * ws * R[it, i_s + 1] + wt * ws * R[it1, i_s + 1])
    keep = Rang <= max_radius
    u, w, th, Rang = u[keep], w[keep], th[keep], Rang[keep]
    tvec = np.cos(th)[:, None] * e0 + np.sin(th)[:, None] * n0
    pts = move_along(np.repeat(c[None], len(u), 0), tvec, Rang)
    return pts, np.stack([u, w], 1)


def _relax(xyz, keys, dphi, iters=120, eta=0.3):
    """Spring relaxation on the sphere with rest lengths = Δφ at the bond midpoint."""
    index = {tuple(k): i for i, k in enumerate(keys)}
    bonds = []
    for i, (u, w) in enumerate(keys):
        for du, dw in ((1, 0), (0, 1), (-1, 1)):
            j = index.get((u + du, w + dw))
            if j is not None:
                bonds.append((i, j))
    bonds = np.array(bonds)
    bi, bj = bonds[:, 0], bonds[:, 1]
    for _ in range(iters):
        d = xyz[bj] - xyz[bi]
        mid = xyz[bi] + 0.5 * d
        mid /= np.linalg.norm(mid, axis=1, keepdims=True)
        rest = np.deg2rad(dphi(*to_azel(mid)))
        L = np.linalg.norm(d, axis=1)
        f = ((L - rest) / np.maximum(L, 1e-9))[:, None] * d * eta
        F = np.zeros_like(xyz)
        np.add.at(F, bi, f); np.add.at(F, bj, -f)
        xyz = xyz + F
        xyz /= np.linalg.norm(xyz, axis=1, keepdims=True)
    return xyz


def build_eye(species: str = "drosophila", sex: str = "female", yaw_fraction: float = 0.4,
              patch_size: int = 5, relax_iters: int = 120) -> EyeMap:
    dphi = dphi_field(species, sex)
    key = species if species in FOV else "eristalis"
    (cx, cy), ra, rb = FOV[key]
    xyz, keys = _hex_lattice_init(species, sex, dphi)
    xyz = _relax(xyz, keys, dphi, iters=relax_iters)
    az, el = to_azel(xyz)
    keep = ((az - cx) / ra) ** 2 + ((el - cy) / rb) ** 2 <= 1.0
    xyz, keys, az, el = xyz[keep], keys[keep], az[keep], el[keep]
    d = np.asarray(dphi(az, el), dtype=float)
    h = h_axis_field(xyz, yaw_fraction)
    alpha = shear_angle(az, el)
    v = rotate_in_tangent(xyz, h, alpha)          # +v = +h rotated counter-clockwise by the shear angle
    # patches: blocks of the initial lattice in offset coordinates
    col = keys[:, 0] + keys[:, 1] // 2
    row = keys[:, 1]
    pid = (row // patch_size) * 10000 + (col // patch_size)
    _, patch = np.unique(pid, return_inverse=True)
    return EyeMap(species, sex, xyz, az, el, d, h, v, patch, keys)


# ----------------------------------------------------------------------------- stimulus sampling
class Sampler:
    """Samples a stimulus movie on a regular (az, el) grid at the ommatidia and at their virtual
    neighbours (±Δφ along ±h and ±v), after a Gaussian optical blur of σ = 0.5·Δφ (acceptance angle
    ≈ Δφ). Returns arrays of shape (T, N)."""

    def __init__(self, eye: EyeMap, az_grid: np.ndarray, el_grid: np.ndarray):
        self.eye = eye
        self.az_grid, self.el_grid = az_grid, el_grid
        self.daz = az_grid[1] - az_grid[0]; self.dele = el_grid[1] - el_grid[0]
        pts = {"c": eye.xyz,
               "h-": move_along(eye.xyz, -eye.h_axis, eye.dphi), "h+": move_along(eye.xyz, eye.h_axis, eye.dphi),
               "v-": move_along(eye.xyz, -eye.v_axis, eye.dphi), "v+": move_along(eye.xyz, eye.v_axis, eye.dphi)}
        self.idx = {k: self._index(*to_azel(p)) for k, p in pts.items()}
        sigma_deg = 0.5 * float(np.median(eye.dphi))
        self.sig_px = (sigma_deg / self.dele, sigma_deg / self.daz)

    def _index(self, az, el):
        fa = np.clip((az - self.az_grid[0]) / self.daz, 0, len(self.az_grid) - 1.001)
        fe = np.clip((el - self.el_grid[0]) / self.dele, 0, len(self.el_grid) - 1.001)
        ia = np.floor(fa).astype(int); ie = np.floor(fe).astype(int)
        return ia, ie, fa - ia, fe - ie

    @staticmethod
    def _blur1d(x, sigma, axis):
        if sigma < 0.3:
            return x
        r = int(np.ceil(3 * sigma)); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
        xp = np.moveaxis(x, axis, -1)
        xp = np.pad(xp, [(0, 0)] * (xp.ndim - 1) + [(r, r)], mode="edge")
        out = np.zeros(np.moveaxis(x, axis, -1).shape)
        for j, kv in enumerate(k):
            out += kv * xp[..., j:j + out.shape[-1]]
        return np.moveaxis(out, -1, axis)

    def blur(self, movie):
        return self._blur1d(self._blur1d(movie, self.sig_px[0], 1), self.sig_px[1], 2)

    def sample(self, m, which="c"):
        ia, ie, wa, we = self.idx[which]
        return ((1 - we) * (1 - wa))[None] * m[:, ie, ia] + (we * (1 - wa))[None] * m[:, ie + 1, ia] \
            + ((1 - we) * wa)[None] * m[:, ie, ia + 1] + (we * wa)[None] * m[:, ie + 1, ia + 1]

    def __call__(self, movie: np.ndarray) -> dict:
        """movie: (T, n_el, n_az) in [0, 1] -> {'c', 'h-', 'h+', 'v-', 'v+'}: (T, N)."""
        m = self.blur(movie)
        return {k: self.sample(m, k) for k in self.idx}


def grid(step=1.0):
    return np.arange(GRID_AZ[0], GRID_AZ[1] + 1e-9, step), np.arange(GRID_EL[0], GRID_EL[1] + 1e-9, step)


def grating_movie(az_grid, el_grid, direction_deg, speed_deg_s, wavelength_deg=30.0, duration=1.0,
                  dt=1 / 120, contrast=1.0, mask=None, onset=0.25):
    """Drifting sine grating (Falt et al. 2026 used λ = 30°, 30°/s, full contrast). direction 0 =
    toward +azimuth (front-to-back on the right eye), 90 = upward. `mask(az, el)` in [0, 1] restricts
    the grating (grey outside). The pattern is defined in the equirectangular chart; for the
    validation of the Drosophila model this mimics a cylindrical arena."""
    T = int(round(duration / dt))
    A, E = np.meshgrid(az_grid, el_grid)
    th = np.deg2rad(direction_deg)
    proj = A * np.cos(th) + E * np.sin(th)
    t = np.arange(T) * dt
    moving = (t >= onset).astype(float)
    phase = np.cumsum(moving) * dt * speed_deg_s
    stim = 0.5 + 0.5 * contrast * np.sin(2 * np.pi * (proj[None] - phase[:, None, None]) / wavelength_deg)
    if mask is not None:
        stim = 0.5 + (stim - 0.5) * mask(A, E)[None]
    return stim
