# HOVER: ERC Consolidator Grant 2027 application workspace

**HOVER: Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits:
from a sexually dimorphic eye to active machine vision**

| | |
|---|---|
| PI | Prof. Dr. Étienne Serbe-Kamp (ORCID 0000-0002-7097-6274), Professor of Computer Vision |
| Host | IU Internationale Hochschule, Germany (eligible; GEP and PIC still to be confirmed) |
| Partners | MPI for Biological Intelligence (Fenk lab: a HOVER **postdoc**, hoverfly physiology) and LMU (Merrill lab: a HOVER **PhD student**, origin and genetics of the male-only third retinal muscle), as additional beneficiaries |
| Call | **ERC-2027-COG**, deadline **Tue 12 Jan 2027**; plan to submit **Thu 7 Jan** |
| Eligibility | PhD 2016, inside the CoG-2027 window (PhD defended 1 Jan 2012 – 31 Dec 2021) |
| Panel | LS5 primary, PE6 secondary |
| Budget | €1,997,500 / 60 months (placeholder rates) |
| Backup | DFG Sachbeihilfe **only if** the ERC fails → [`docs/dfg_backup_strategy.md`](docs/dfg_backup_strategy.md) |
| Status | **Science Draft 3 (12 Nov 2026)**: rebuilt around the question "what is the third muscle for?"; two bowl stimuli, closed-loop search and event-camera simulation as preliminary results; all figures redrawn as vector graphics; admin items unchanged |

## The project in one paragraph

Seeing is active: eyes move, and how they should move depends on the task. Event cameras, which are
blind to a static scene unless the sensor moves, bring the same question to machine vision. Male
*Eristalis* hoverflies chase mates in aerial pursuits; females do not. Males have a dorso-frontal
"bright zone", a narrowed wide-field motion cell (HSN) and, as we discovered, **a male-only third
retinal muscle (M. interocularis, MIO)**. Nobody knows what it is for.

HOVER will **find out what the third eye muscle is for, explain why the male's task demands it, and
test whether the answer is a design principle for machine vision**. It will:

1. build connectome-constrained spiking models of the fly gaze loop, including the electrical synapses
   we found with MESH, in the female *and* the new male *Drosophila* connectome, at three levels:
   biophysical, reduced (Kolmogorov–Arnold reduction to equations), trainable;
2. let the model design two stimuli for one bowl-shaped display, a matched one (male and female
   retinae move alike) and a love-spot one (they do not), test them in *Eristalis* with retinal
   tracking, a stimulus search steered by the tracked retina, EMG and section of the muscle, and
   trace where the muscle comes from and which genes make it male;
3. ask whether a third effector emerges when the model is trained for pursuit;
4. transfer the principles to active event-based vision: a wide-angle and a telephoto event camera
   on micro-movement stages, spiking networks on neuromorphic chips, pre-registered benchmarks
   against deep networks, and closed-loop hovering and pursuit on an indoor quadrotor;
5. validate everything at scale with students and citizens on low-cost camera robots, community
   proofreading of electrical synapses, and a "hoverfly watch".

**Scope.** Binocular coordination of the retinae and depth perception are the Fenk laboratory's
topic and are deliberately not part of HOVER (B2, section 6).

## Repository map

| Path | ERC part | Limit |
|---|---|---|
| [`proposal/B1_cover_page.md`](proposal/B1_cover_page.md) | B1 cover: title, acronym, abstract, panels, cross-panel justification | not counted |
| [`proposal/B1_PartI_synopsis.md`](proposal/B1_PartI_synopsis.md) | **B1 Part I of the Scientific Proposal** (read at Step 1), with Fig. 1 (concept) and Fig. 2 (preliminary results) | **5 pp** |
| [`proposal/B1_CV_track_record.md`](proposal/B1_CV_track_record.md) | **B1 CV and Track Record** (read at Step 1) | **4 pp** |
| [`proposal/B2_PartII.md`](proposal/B2_PartII.md) | **B2 Part II of the Scientific Proposal** + Funding ID, with Figs. B1–B3 | **7 pp** |
| [`proposal/abstract.md`](proposal/abstract.md) | Part A abstract and keywords | 2000 chars |
| [`proposal/PartA_budget_resources.md`](proposal/PartA_budget_resources.md) | Part A budget table + Resources text | 8000 chars |
| [`proposal/figures/`](proposal/figures/) | Fig. 1 concept, Fig. 2 results, Fig. B1 supporting evidence, Fig. B2 work plan, Fig. B3 Gantt chart: all drawn at print size by `tools/fig_*.py` (SVG for the PDFs, PDF, 600 dpi PNG for Word); image sources in `figures/src/` | — |
| [`proposal/gantt.md`](proposal/gantt.md), [`proposal/references.md`](proposal/references.md) | Timeline; bibliography (112 entries, [verify] marks where a source could not be checked) | — |
| [`admin/host_support_letter.md`](admin/host_support_letter.md) | Mandatory host letter (official 2027 wording, IU filled in) | annex |
| [`admin/ethics_security_self_assessment.md`](admin/ethics_security_self_assessment.md) | Ethics and security tables, drafted | Part A |
| [`docs/ERC_CoG_call_requirements.md`](docs/ERC_CoG_call_requirements.md) | The 2027 rules with page references | — |
| [`docs/eligibility_and_host_checklist.md`](docs/eligibility_and_host_checklist.md) | What's settled, what IU and you must do, open decisions | — |
| [`docs/submission_plan.md`](docs/submission_plan.md) | Week-by-week plan to 12 Jan 2027 | — |
| [`docs/coi_backyard_brains.md`](docs/coi_backyard_brains.md) | Conflict-of-interest plan (Backyard Brains / SpikerBot) | — |
| [`docs/dfg_backup_strategy.md`](docs/dfg_backup_strategy.md) | Sequential DFG backup, timing | — |
| [`docs/positioning_from_DFG.md`](docs/positioning_from_DFG.md) | What changes from the DFG *Eristalis* proposal | — |
| [`teaching/`](teaching/), [`outreach/`](outreach/) | Course integration; citizen-science design | B2 WP5 |
| [`code/`](code/), [`prior_work/`](prior_work/) | `hover` package: **integrated model** (sphere eye map with Zhao-2025 axes, Ammer-2023 detectors and local opponency circuits, LPTC receptive fields, **Tier-1 HH model ported from MESH**, Falt-2026 oculomotor model), **Falt validation** (`validate_falt.py`), **two stimuli on a bowl display, position map, alternative drives and closed-loop search** (`bowl.py`), **event-camera simulation** (`eventcam.py`); result files `bowl_result.json`, `eventcam_result.json`, `results_raw/`; earlier analyses in `results_archive/`; design notes in [`docs/model_design.md`](docs/model_design.md) | preliminary results |
| [`tools/`](tools/) | `render_pdf.py` (ERC-format PDFs with **real page counts**) · `check_limits.py` (abstract, rendered page counts, Resources, budget cap) · `fig_concept.py`, `fig_results.py`, `fig_support.py`, `fig_workplan.py` (figures; shared style in `figstyle.py`) · `export_docx.sh` | — |

## Quick start

```bash
python3 tools/render_pdf.py              # build/*.pdf in ERC format (A4, 11 pt, 2 cm margins, headers) + page counts
python3 tools/check_limits.py            # abstract, page counts of the rendered PDFs, Resources length, budget cap
for f in concept results support workplan; do python3 tools/fig_$f.py; done   # redraw the five figures
cd code
python3 -m hover.bowl --collect          # merge results_raw/ into bowl_result.json (the numbers of the proposal)
for t in tier1 pipeline models binocular bowl eventcam; do python3 -m hover.tests.test_$t; done
bash ../tools/export_docx.sh             # .docx with the figures, for pasting into the official ERC templates
```

To recompute the results from scratch (about 40 minutes on four cores), see the commands in
`code/README.md`.

## Important before submission

- **These are drafts.** The ERC allows AI help in preparing a proposal, but the PI keeps full
  authorship responsibility, and every proposal is screened for plagiarism (IfA p. 8, 18). Rewrite
  in your own voice, and check every claim and every `[fill]` / `[verify]`.
- **Author lists must be exactly as published**, with joint authorships marked (IfA p. 28).
  Falt *et al.* 2026 and Madariaga *et al.* 2024 were checked against the papers; the PsyArXiv
  eye-tracking preprint and the Kviatko manuscript still need their final author lists and DOIs.
- **No support letters.** The ERC disregards them. Instead, obtain **written consent** from every
  researcher named in the proposal before the deadline (IfA p. 26, 33).
- Use the **official B1/B2 templates** from the submission system, with a header on every page:
  `Serbe-Kamp | HOVER | Part B1/B2`.

## Open items

Science (this draft):
1. Check the questions at the end of `docs/model_design.md` (§7): the display at the MPI-BI, the
   location of the love spot, access to the third muscle, the muscle labels in the tomography image.
2. Tables and figure captions are set in 9.5 pt; the ERC asks for at least 11 pt. Decide whether to
   keep this (common practice) or to set them in 11 pt and cut about half a page of text in B2.
3. Panel: the proposal now leans further toward computer vision. LS5 with PE6 as secondary panel is
   kept; consider whether PE6 should be primary.
4. The active camera head now has two cameras and two piezo stages; check the €40,000 in the budget.
5. Post the Kviatko *et al.* manuscript on bioRxiv before 12 Jan and add the DOI to references [2].
6. Fill the `[fill]` / `[verify]` marks in the CV (defence date, roles in co-authored papers, grants).
7. Ask three readers to test Part I (an ERC grantee, a non-fly neuroscientist, a computer-vision
   colleague); see `docs/submission_plan.md`.

Admin (to be handled separately): IU PIC, GEP, support letter, cost rates, doctoral route; PhD
defence-date document; MPG and LMU consent, PICs and budget sections; consent from Fenk and Merrill
and the written scope agreement with the Fenk lab's ERC project; DFG eligibility of IU staff.
