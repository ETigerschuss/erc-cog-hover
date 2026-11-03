"""Differentiable (autograd) version of the front end for pixel-level stimulus optimisation
(the ALIstim "ExperimentTwo" idea: gradient descent on the stimulus movie through the detector
bank, here through eye map → lamina → T4/T5 → local opponency circuits → LPTC conductances →
rate surrogate → retinal-shift vectors). Same maths as hover.hrbl / hover.lptc, written without
in-place updates so that `autograd` can differentiate it. PyTorch is not available in the
development container; the code is backend-agnostic in structure and ports to torch line by line.
"""
from __future__ import annotations

import autograd.numpy as anp
import numpy as np
from autograd import grad

from .hrbl import CircuitParams
from .species import Model


def _lowpass(x, tau, dt):
    a = float(np.exp(-dt / tau))
    ys = [x[0]]
    for t in range(1, x.shape[0]):
        ys.append(a * ys[-1] + (1.0 - a) * x[t])
    return anp.stack(ys)


def _rect(x, thr=0.0):
    return anp.maximum(x - thr, 0.0)


def _lamina(x, p: CircuitParams):
    interim = (x - _lowpass(x, p.tau_hp, p.dt)) + 0.1 * x
    return _lowpass(x, p.tau_lp, p.dt), _rect(interim), _lowpass(1.0 - x, p.tau_lp, p.dt), _rect(-(interim - 0.05))


def _detectors(samples, axis, p):
    on_lp_m, _, off_lp_m, _ = _lamina(samples[axis + "-"], p)
    _, on_hp_c, _, off_hp_c = _lamina(samples["c"], p)
    on_lp_p, _, off_lp_p, _ = _lamina(samples[axis + "+"], p)
    out = []
    for A, B, C in ((on_lp_m, on_hp_c, on_lp_p), (off_lp_m, off_hp_c, off_lp_p)):
        out += [_rect(A * B / (p.DC + C), p.DC), _rect(C * B / (p.DC + A), p.DC)]
    return out


def _circuits(inp_plus, inp_minus, p):
    M = p.connM()
    T, K = inp_plus.shape
    k = p.dt / p.tau_net
    Vm = anp.zeros((6, K))
    out = [Vm]
    for t in range(1, T):
        Vinp = anp.concatenate([inp_plus[t - 1][None], inp_minus[t - 1][None], anp.zeros((4, K))], 0)
        total = M @ _rect(Vm) + Vinp
        Vm = Vm + k * (total - Vm)
        out.append(Vm)
    return anp.stack(out)


class DifferentiableFrontEnd:
    """Stimulus parameters z (T_lr, H_lr, W_lr) → movie on the (el, az) grid (bilinear up-sampling in
    space, frame repetition in time) → LPTC Ammer-membrane ΔV → surrogate motor-neuron Δrates."""

    def __init__(self, model: Model, surrogate, T_lr=24, rep=4, H_lr=14, W_lr=18, fix_frames=24,
                 az_range=(-15.0, 150.0), el_range=(-65.0, 65.0)):
        self.model, self.sur = model, surrogate
        self.p = model.circuit_params
        self.T_lr, self.rep, self.fix = T_lr, rep, fix_frames
        s = model.sampler
        # up-sampling matrices (grid ← low-res control points)
        self.U_el = self._interp_matrix(model.el_grid, np.linspace(el_range[0], el_range[1], H_lr))
        self.U_az = self._interp_matrix(model.az_grid, np.linspace(az_range[0], az_range[1], W_lr))
        # blur matrices
        self.B_el = self._blur_matrix(len(model.el_grid), s.sig_px[0])
        self.B_az = self._blur_matrix(len(model.az_grid), s.sig_px[1])
        self.idx = s.idx
        self.M = model.front.M
        self.W = {nm: model.front.weights[nm] for nm in model.lptcs}

    @staticmethod
    def _interp_matrix(grid, ctrl):
        U = np.zeros((len(grid), len(ctrl)))
        for i, g in enumerate(grid):
            f = np.clip((g - ctrl[0]) / (ctrl[1] - ctrl[0]), 0, len(ctrl) - 1.001)
            j = int(np.floor(f)); w = f - j
            U[i, j] = 1 - w; U[i, j + 1] = w
        return U

    @staticmethod
    def _blur_matrix(n, sigma):
        if sigma < 0.3:
            return np.eye(n)
        i = np.arange(n)
        B = np.exp(-0.5 * ((i[:, None] - i[None, :]) / sigma) ** 2)
        return B / B.sum(1, keepdims=True)

    def movie(self, z):
        """z: (T_lr, H_lr, W_lr) unconstrained → movie (T, n_el, n_az) in [0, 1] (grey before fix)."""
        img = 0.5 + 0.5 * anp.tanh(z)                                   # contrast-bounded
        up = anp.matmul(anp.matmul(self.U_el[None], img), self.U_az.T[None])   # (T_lr, n_el, n_az)
        frames = anp.repeat(up, self.rep, axis=0)
        grey = anp.full((self.fix,) + frames.shape[1:], 0.5)
        return anp.concatenate([grey, frames], 0)

    def _sample(self, m, which):
        ia, ie, wa, we = self.idx[which]
        return ((1 - we) * (1 - wa))[None] * m[:, ie, ia] + (we * (1 - wa))[None] * m[:, ie + 1, ia] \
            + ((1 - we) * wa)[None] * m[:, ie, ia + 1] + (we * wa)[None] * m[:, ie + 1, ia + 1]

    def responses(self, z):
        mov = self.movie(z)
        blurred = anp.matmul(anp.matmul(self.B_el[None], mov), self.B_az.T[None])
        samples = {k: self._sample(blurred, k) for k in self.idx}
        T = mov.shape[0]
        fb, fr = slice(self.fix - 8, self.fix), slice(self.fix + 12, T)
        circuits = {}
        for axis in ("h", "v"):
            t4p, t4m, t5p, t5m = _detectors(samples, axis, self.p)
            circuits[axis] = _circuits(_rect(t4p + t5p) @ self.M.T, _rect(t4m + t5m) @ self.M.T, self.p)
        dv = {}
        for s in self.model.front.specs:
            Vm = circuits[s.axis]
            T_pd, LPi_nd = (Vm[:, 0], Vm[:, 3]) if s.pd_sign > 0 else (Vm[:, 1], Vm[:, 2])
            g_e = self.p.TV * (_rect(T_pd) @ self.W[s.name]); g_i = self.p.LV * (_rect(LPi_nd) @ self.W[s.name])
            V = (self.p.E_exc * g_e + self.p.E_inh * g_i) / (g_e + g_i + 1.0)
            dv[s.name] = anp.mean(V[fr]) - anp.mean(V[fb])
        return dv, mov

    def motor(self, dv):
        v = anp.stack([dv[n] for n in self.model.lptcs])
        return {mn: self.sur.slope[mn] * anp.dot(self.sur.W[mn], v) for mn in self.model.motor_neurons}


def make_objective(fe: DifferentiableFrontEnd, baseline: dict, theta_a: float, theta_b: float, min_mio_hz=10.0,
                   l_contrast=0.02):
    """Loss = −(1 − cos Δ) between the two hypotheses' shift vectors + soft MIO-drive and contrast terms.
    theta_a/b: MIO pull directions in the model frame."""
    pull = fe.model.pull

    def loss(z):
        dv, mov = fe.responses(z)
        d = fe.motor(dv)
        base = anp.zeros(2)
        for nm in ("MOT", "MOS"):
            if nm in d:
                base = base + d[nm] / baseline[nm] * anp.array([anp.cos(anp.deg2rad(pull[nm])), anp.sin(anp.deg2rad(pull[nm]))])
        w_mio = d["MIO"] / baseline["MIO"]
        va = base + w_mio * anp.array([np.cos(np.deg2rad(theta_a)), np.sin(np.deg2rad(theta_a))])
        vb = base + w_mio * anp.array([np.cos(np.deg2rad(theta_b)), np.sin(np.deg2rad(theta_b))])
        cos = anp.dot(va, vb) / (anp.sqrt(anp.dot(va, va) + 1e-6) * anp.sqrt(anp.dot(vb, vb) + 1e-6))
        drive = anp.minimum(1.0, anp.abs(d["MIO"]) / min_mio_hz)
        contrast = anp.mean(anp.abs(mov - 0.5)) * 2
        return -(1.0 - cos) * drive + l_contrast * contrast
    return loss, grad(loss)


def adam(loss_grad, z0, steps=60, lr=0.1, log=print, every=5):
    m = np.zeros_like(z0); v = np.zeros_like(z0); z = z0.copy()
    b1, b2, eps = 0.9, 0.999, 1e-8
    best = (np.inf, z.copy())
    for k in range(1, steps + 1):
        l, g = loss_grad(z)
        if l < best[0]:
            best = (l, z.copy())
        m = b1 * m + (1 - b1) * g; v = b2 * v + (1 - b2) * g * g
        z = z - lr * (m / (1 - b1 ** k)) / (np.sqrt(v / (1 - b2 ** k)) + eps)
        if k % every == 0 or k == 1:
            log(f"  step {k:3d}: loss {l:+.4f}")
    return best[1], best[0]
