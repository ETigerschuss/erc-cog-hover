# HOVER — ERC Consolidator Grant application workspace

**HOVER: Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits —
from sexually dimorphic connectomes to bio-inspired computer vision**

PI: Prof. Dr. Étienne Serbe-Kamp (ORCID 0000-0002-7097-6274), Professorship for Computer Vision, IU
Call: ERC Consolidator Grant (CoG), next call — see [`docs/ERC_CoG_call_requirements.md`](docs/ERC_CoG_call_requirements.md)
Status: **Draft 0** (scaffold built from the DFG *Eristalis* proposal, the ALIstim notebook,
the Kviatko et al. Diptera manuscript and the MESH / Falt, Ammer et al. preprint)

---

## The project in one paragraph

Flies solve, with ~10⁵ neurons and a few milliwatts, the visual problems computer
vision still finds hard: ego-motion estimation, small-target pursuit in clutter and
gaze stabilisation, in real time, from sparse, noisy photoreceptor signals. Male
*Eristalis* hoverflies add a twist: a sexually dimorphic visual system (a male
"bright zone", a narrowed dorso-frontal HSN receptive field, an extra HS cell, HSNE)
**and a male-only third retinal muscle**, so the same body plan carries two visual
"architectures" tuned to different tasks. HOVER uses that natural experiment to ask
**which circuit motifs make a visual system task-specific, and whether they carry
over to engineered spiking vision**. We (1) build connectome-constrained,
biophysical *and* mathematically reduced spiking neural network (SNN) models of the
*Drosophila* motion-vision → LPTC → retinal-motor-neuron pathway (FlyWire/Codex,
MESH gap-junction maps); (2) map them onto male and female *Eristalis* and test the
dimorphic predictions with model-discriminating ("controversial") stimuli; (3) turn
the validated motifs into event-camera SNN vision with active retinal micro-movements,
benchmarked against deep networks; and (4) run the whole loop as citizen science and
teaching on SpikerBot robots in IU computer-vision courses.

## Repository map

| Path | What it holds | ERC part |
|---|---|---|
| [`proposal/B1a_extended_synopsis.md`](proposal/B1a_extended_synopsis.md) | Extended synopsis (≤5 p.) | Part B1 |
| [`proposal/B1b_CV_track_record.md`](proposal/B1b_CV_track_record.md) | CV and track record template, pre-filled where known | Part B1 |
| [`proposal/B2_scientific_proposal.md`](proposal/B2_scientific_proposal.md) | Full scientific proposal (≤14 p.): state of the art, objectives, methods, WPs, risks, resources | Part B2 |
| [`proposal/abstract.md`](proposal/abstract.md) | Abstract (≤2000 characters, checked by script) | Part A |
| [`proposal/budget.md`](proposal/budget.md) | Budget skeleton, 60 months, ≤ €2.0 M | Part A / B2 §d |
| [`proposal/gantt.md`](proposal/gantt.md) | Timeline and milestones (Mermaid) | B2 |
| [`proposal/references.md`](proposal/references.md) | Bibliography | B1/B2 |
| [`docs/ERC_CoG_call_requirements.md`](docs/ERC_CoG_call_requirements.md) | Rules, page limits, evaluation criteria — **all to be verified** against the current Work Programme | — |
| [`docs/eligibility_and_host_checklist.md`](docs/eligibility_and_host_checklist.md) | Open blockers: PhD date, host institution, conflict of interest, panel | — |
| [`docs/positioning_from_DFG.md`](docs/positioning_from_DFG.md) | What changes from the DFG *Eristalis* proposal and why | — |
| [`teaching/cv_course_integration.md`](teaching/cv_course_integration.md) | How HOVER runs inside IU computer-vision courses | B2 WP5 |
| [`outreach/citizen_science_spikerbot.md`](outreach/citizen_science_spikerbot.md) | Citizen-science design with SpikerBot | B2 WP5 |
| [`code/`](code/) | `hover` Python package: elementary motion detectors, gap-junction-coupled LIF network (LPTC → RMN), controversial-stimulus search. NumPy only. | Preliminary results |
| [`prior_work/`](prior_work/) | ALIstim notebook (differentiable HR/BL detectors + stimulus optimisation) | Preliminary results |
| [`admin/`](admin/) | Host-institution letter template, ethics self-assessment | Part A / annexes |

## Quick start for the code

```bash
cd code
python -m hover.demo          # runs EMD → LPTC → RMN SNN, prints RMN tuning
python -m hover.tests.test_models   # or: python -m pytest -q hover/tests
python ../tools/check_limits.py   # checks abstract length and rough page counts
```

## Next steps

1. Resolve the four blockers in [`docs/eligibility_and_host_checklist.md`](docs/eligibility_and_host_checklist.md). Host and PhD date decide whether this can be submitted at all.
2. Fill in bibliometrics and the list of 10 key outputs in the CV.
3. Make the panel decision (LS5 vs PE6) and rewrite B1a's first page for that panel.
4. Write letters of commitment from experimental partners (Fenk lab / MPI-BI; an *Eristalis* electrophysiology lab).
5. Run a mock panel and interview with colleagues, about 8 weeks before the deadline.
