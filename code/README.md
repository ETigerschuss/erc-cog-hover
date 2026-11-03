# `hover`: model code for HOVER

## Integrated model v0 (Nov 2026) — `docs/model_design.md`

stimulus movie → eye map on the sphere → Ammer 2023 detectors and local opponency circuits →
LPTC receptive fields and conductances → MESH Tier-1 electrical network with HH retinal motor
neurons → retinal-shift vector. Three circuits: *Drosophila* ♀ (ground truth, Falt et al. 2026),
*Eristalis* ♀, *Eristalis* ♂ (+ MIO with a free pull direction).

| Module | Content |
|---|---|
| `eye.py` | ommatidia on the sphere (Δφ fields, bright zone), local +h/+v axes (Zhao et al. 2025), virtual-neighbour sampling, patches |
| `hrbl.py` | Ammer et al. 2023 Figure-7 model: lamina, three-arm T4/T5 detectors, six-unit recurrent local circuit with LPi opponency, blocking conditions, conductance membrane |
| `lptc.py` | receptive fields (Nordström 2008 HSN ♀/♂, HSNE, HS/VS of *Drosophila*), RF-weighted g_exc/g_inh |
| `tier1_hh.py` | MESH Tier-1 port (HH motor neurons, graded LPTCs, filtered gap junctions) + conductance drive, LPTC leak scale, VS→MOS weight |
| `oculomotor.py` | holder-frame ↔ model-frame conversion, muscle pulls, vector-sum retinal shift |
| `species.py` | `Model(species, sex, mio_from, mio_pull, …)`: builds everything, calibrates the tonic rate, `run(movie)` |
| `validate_falt.py` | `python -m hover.validate_falt --wvs 2 --fig out.png`: RMN/LPTC direction tuning vs Falt et al., frame-rotation fit, OKR check |
| `adversarial.py` | `python -m hover.adversarial --out r.json --fig panel.png`: controversial stimulus for the MIO pull direction (ES on a rate surrogate, Tier-1 verification, female prediction) |
| `frontend_ad.py` | autograd version of the front end for pixel-level gradient descent on the stimulus (ALIstim-style) |
| `tests/` | `python -m hover.tests.test_tier1`, `python -m hover.tests.test_pipeline` |

```bash
pip install -r requirements.txt      # numpy, numba, scipy, matplotlib, autograd
python -m hover.tests.test_pipeline
python -m hover.validate_falt --wvs 2 --fig validation.png
python -m hover.adversarial --gens 25 --out adv.json --fig fig_B1e_mio_controversial.png
```

Parameters marked [verify] in the code (hoverfly Δφ, bright zone, HSNE field, hoverfly pull
directions) are placeholders to be replaced by WP1/WP2 measurements. The fitted quantities of the
*Drosophila* validation (holder-frame rotation β, VS→MOS junction weight) are documented in
`docs/model_design.md` §3.

## First-generation code (kept for the record)

NumPy-only reduced models (Tier 2) used for the first preliminary results:

- `emd.py`: ON/OFF band-pass + Hassenstein–Reichardt detectors (T4/T5-like), drifting gratings. A port of the HRBL front end in `prior_work/ALIstimAXET_Final3_1.ipynb`.
- `snn.py`: graded LPTCs (HS/VS, + HSNE in *Eristalis*) coupled **only by gap junctions** to LIF retinal motor neurons (MOT, MOS, male MIO, M. interocularis). `eristalis(sex, mio_from=...)` builds the competing H2 model family.
- `controversial.py`: evolution-strategy search for stimuli that maximise the disagreement between two circuit hypotheses (Golan et al. 2020).
- `demo.py`: RMN tuning for all three circuits + one H2-vs-alternative search.
- `tier1_hh.py`: **Tier-1 biophysical model ported from MESH** (Hodgkin–Huxley motor neurons, graded LPTCs, low-pass-filtered gap junctions; MESH calibrated preset), with the male *Eristalis* extension (HSNE, MIO).
- `mio_search.py`: visual front end for the Tier-1 model and the **controversial-stimulus search for the MIO pull direction** (Fig. B1g). `python -m hover.mio_search` writes `proposal/figures/fig_B1e_mio_controversial.png` and `mio_search_result.json` (about 1 min with numba).

```bash
pip install -r requirements.txt
python -m hover.demo
python -m hover.tests.test_models
```

Parameters (receptive fields, conductances) are **illustrative placeholders**. In WP1 they
will be replaced by MESH apposition areas and fits to physiology. The Tier-1 equations and the
calibrated preset are those of the MESH development build (github.com/ETigerschuss/MESH); the
LPTC–motor-neuron coupling is re-calibrated in `mio_search.calibrate_coupling` so that a strong
stimulus modulates motor-neuron rate by about 20 Hz, the range of the RMN tuning in Falt et al. 2026.
