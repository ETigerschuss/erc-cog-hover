# `hover`: preliminary-results code for HOVER

NumPy-only reduced models (Tier 2) for the proposal's preliminary results:

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
