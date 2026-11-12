# `hover`: model code for HOVER

## Integrated model (Nov 2026) — `docs/model_design.md`

stimulus movie → eye map on the sphere → Ammer 2023 detectors and local opponency circuits →
LPTC receptive fields and conductances → MESH Tier-1 electrical network with HH retinal motor
neurons → retinal movement. Three circuits: *Drosophila* ♀ (ground truth, Falt et al. 2026),
*Eristalis* ♀, *Eristalis* ♂ (with the third muscle; its drive and pull direction are options).

| Module | Content |
|---|---|
| `eye.py` | ommatidia on the sphere (Δφ fields), local +h/+v axes (Zhao et al. 2025), virtual-neighbour sampling, patches |
| `hrbl.py` | Ammer et al. 2023 Figure-7 model: lamina, three-arm T4/T5 detectors, six-unit recurrent local circuit with LPi opponency, blocking conditions, conductance membrane |
| `lptc.py` | receptive fields (Nordström 2008 HSN ♀/♂, HSNE, HS/VS of *Drosophila*), RF-weighted g_exc/g_inh |
| `tier1_hh.py` | MESH Tier-1 port (HH motor neurons, graded LPTCs, filtered gap junctions) + conductance drive, LPTC leak scale, VS→MOS weight |
| `oculomotor.py` | holder-frame ↔ model-frame conversion, muscle pulls, vector-sum retinal shift |
| `species.py` | `Model(species, sex, mio_from, mio_pull, …)`: one eye; builds everything, calibrates the tonic rate, `run(movie)` |
| `binocular.py` | `BinocularModel`: both eyes, bilateral Tier-1 network, third muscle with one motor neuron per side or one for both |
| `validate_falt.py` | RMN/LPTC direction tuning against Falt et al., frame-rotation fit, optokinetic reflex |
| **`bowl.py`** | **the two-stimulus design**: bowl display, square-wave gratings in apertures, matched and love-spot stimuli, position map, alternative drives of the muscle, closed-loop search, `--collect` |
| **`eventcam.py`** | **event-camera simulation**: scene registration against small-target detection as a function of the sensor movement |
| `tests/` | `test_tier1`, `test_pipeline`, `test_models`, `test_binocular`, `test_bowl`, `test_eventcam` |

Result files read by the figures and quoted in the proposal: `bowl_result.json` (merged from
`results_raw/` by `python -m hover.bowl --collect`), `eventcam_result.json`,
`results_raw/validate_falt.json`.

```bash
pip install -r requirements.txt      # numpy, numba, scipy, matplotlib, autograd
for t in tier1 pipeline models binocular bowl eventcam; do python -m hover.tests.test_$t; done

# recompute everything (about 40 min on four cores)
R=hover/results_raw
python -m hover.validate_falt --wvs 2 --out $R/validate_falt.json
python -m hover.bowl --scan --map --map-dir 90 --out $R/bowl_main.json
python -m hover.bowl --apertures --out $R/bowl_apertures.json
for v in HSNE HS VS; do python -m hover.bowl --scan --mio-from $v --out $R/bowl_alt_$v.json; done
python -m hover.bowl --closed-loop displaced --noise 0.02 --out $R/cl_displaced_noise0.02.json
for s in 0 1 2; do python -m hover.bowl --closed-loop displaced --noise 0.05 --seed $s --out $R/cl_displaced_noise0.05_seed$s.json; done
python -m hover.bowl --closed-loop naive --noise 0.02 --out $R/cl_naive_noise0.02.json
python -m hover.bowl --collect
python -m hover.eventcam --n 150 --out hover/eventcam_result.json
```

Parameters marked [verify] in the code (hoverfly Δφ, love-spot aperture, display size, HSNE field,
hoverfly pull directions) are placeholders to be replaced by WP1/WP2 measurements. The fitted
quantities of the *Drosophila* validation (holder-frame rotation β, VS→MOS junction weight) are
documented in `docs/model_design.md` §3.

## Archived analyses

`adversarial.py`, `adversarial_pixel.py`, `frontend_ad.py` (controversial stimuli for the pull
direction of the muscle, one eye; pixel-level gradient descent through the front end), `mio_ring.py`
(twelve pull directions) and `binocular_search.py` (male-versus-female stimulus search with one
median motor command, including dichoptic stimuli). Their results, computed before the eye-map
correction of 11 November, are in `results_archive/` and are not used in the proposal
(`docs/model_design.md` §3g).

## First-generation code (kept for the record)

NumPy-only reduced models (Tier 2) used for the first preliminary results:

- `emd.py`: ON/OFF band-pass + Hassenstein–Reichardt detectors (T4/T5-like), drifting gratings. A port of the HRBL front end in `prior_work/ALIstimAXET_Final3_1.ipynb`.
- `snn.py`: graded LPTCs (HS/VS, + HSNE in *Eristalis*) coupled **only by gap junctions** to LIF retinal motor neurons (MOT, MOS, male MIO, M. interocularis). `eristalis(sex, mio_from=...)` builds the competing H2 model family.
- `controversial.py`: evolution-strategy search for stimuli that maximise the disagreement between two circuit hypotheses (Golan et al. 2020).
- `demo.py`: RMN tuning for all three circuits + one H2-vs-alternative search.
- `tier1_hh.py`: **Tier-1 biophysical model ported from MESH** (Hodgkin–Huxley motor neurons, graded LPTCs, low-pass-filtered gap junctions; MESH calibrated preset), with the male *Eristalis* extension (HSNE, MIO).
- `mio_search.py`: visual front end for the Tier-1 model and the first controversial-stimulus search for the pull direction of the third muscle (superseded; result in `results_archive/`).

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
