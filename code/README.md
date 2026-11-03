# `hover`: preliminary-results code for HOVER

NumPy-only reduced models (Tier 2) for the proposal's preliminary results:

- `emd.py`: ON/OFF band-pass + Hassenstein–Reichardt detectors (T4/T5-like), drifting gratings. A port of the HRBL front end in `prior_work/ALIstimAXET_Final3_1.ipynb`.
- `snn.py`: graded LPTCs (HS/VS, + HSNE in *Eristalis*) coupled **only by gap junctions** to LIF retinal motor neurons (MOT, MOS, male MIO, M. interocularis). `eristalis(sex, mio_from=...)` builds the competing H2 model family.
- `controversial.py`: evolution-strategy search for stimuli that maximise the disagreement between two circuit hypotheses (Golan et al. 2020).
- `demo.py`: RMN tuning for all three circuits + one H2-vs-alternative search.

```bash
pip install -r requirements.txt
python -m hover.demo
python -m hover.tests.test_models
```

Parameters (receptive fields, conductances) are **illustrative placeholders**. In WP1 they
will be replaced by MESH apposition areas and fits to physiology. The full HH model is in
the MESH development build (github.com/ETigerschuss/MESH).
