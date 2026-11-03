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
| Status | **Science Draft 2 (3 Nov 2026)**: abstract, B1 Part I, CV, B2, budget, references and figures rewritten; admin items unchanged |

## The project in one paragraph

Flies solve, with ~10⁵ neurons and a few milliwatts, visual problems that computer vision still finds
hard: ego-motion estimation, small-target pursuit in clutter and gaze stabilisation. Male *Eristalis*
hoverflies add a twist. Their visual system is sexually dimorphic, with a dorso-frontal "bright zone",
a narrowed HSN receptive field and an extra HS cell (HSNE), and, as we discovered, **a male-only third
retinal muscle (M. interocularis, MIO)**. The same body plan therefore carries two visual
"architectures" tuned to different tasks.

HOVER asks **which circuit motifs make a visual system task-specific, and whether they are design
principles that engineered spiking vision can use**. It will:

1. build connectome-constrained spiking models of the fly gaze loop, including the electrical synapses
   we found with MESH, in the female *and* the new male *Drosophila* connectome, at three levels:
   biophysical, reduced (Kolmogorov–Arnold reduction to equations), trainable;
2. test the dimorphic predictions in *Eristalis* with controversial stimuli, retinal tracking and EMG
   of the three muscles, and trace where the MIO comes from and which genes make it male;
3. ask whether the male features emerge as task-optimal solutions;
4. transfer the motifs to active event-based vision: an event camera on a micro-movement stage, motif
   SNNs on neuromorphic chips, pre-registered benchmarks against deep networks, and closed-loop
   hovering and pursuit on an indoor quadrotor;
5. validate everything at scale with students and citizens on low-cost camera robots, community
   proofreading of electrical synapses, and a "hoverfly watch".

## Repository map

| Path | ERC part | Limit |
|---|---|---|
| [`proposal/B1_cover_page.md`](proposal/B1_cover_page.md) | B1 cover: title, acronym, abstract, panels, cross-panel justification | not counted |
| [`proposal/B1_PartI_synopsis.md`](proposal/B1_PartI_synopsis.md) | **B1 Part I of the Scientific Proposal** (read at Step 1), with Fig. A | **5 pp** |
| [`proposal/B1_CV_track_record.md`](proposal/B1_CV_track_record.md) | **B1 CV and Track Record** (read at Step 1) | **4 pp** |
| [`proposal/B2_PartII.md`](proposal/B2_PartII.md) | **B2 Part II of the Scientific Proposal** + Funding ID, with Figs. B1–B3 | **7 pp** |
| [`proposal/abstract.md`](proposal/abstract.md) | Part A abstract and keywords | 2000 chars |
| [`proposal/PartA_budget_resources.md`](proposal/PartA_budget_resources.md) | Part A budget table + Resources text | 8000 chars |
| [`proposal/figures/`](proposal/figures/) | Fig. A overview, Fig. B1 preliminary results (assembled from the DFG material + the new MIO controversial-stimulus panel), Fig. B2 work plan, Fig. B3 Gantt (SVG/PNG/PDF; sources in `figures/src/`) | — |
| [`proposal/gantt.md`](proposal/gantt.md), [`proposal/references.md`](proposal/references.md) | Timeline; bibliography (108 entries, [verify] marks where a source could not be checked) | — |
| [`admin/host_support_letter.md`](admin/host_support_letter.md) | Mandatory host letter (official 2027 wording, IU filled in) | annex |
| [`admin/ethics_security_self_assessment.md`](admin/ethics_security_self_assessment.md) | Ethics and security tables, drafted | Part A |
| [`docs/ERC_CoG_call_requirements.md`](docs/ERC_CoG_call_requirements.md) | The 2027 rules with page references | — |
| [`docs/eligibility_and_host_checklist.md`](docs/eligibility_and_host_checklist.md) | What's settled, what IU and you must do, open decisions | — |
| [`docs/submission_plan.md`](docs/submission_plan.md) | Week-by-week plan to 12 Jan 2027 | — |
| [`docs/coi_backyard_brains.md`](docs/coi_backyard_brains.md) | Conflict-of-interest plan (Backyard Brains / SpikerBot) | — |
| [`docs/dfg_backup_strategy.md`](docs/dfg_backup_strategy.md) | Sequential DFG backup, timing | — |
| [`docs/positioning_from_DFG.md`](docs/positioning_from_DFG.md) | What changes from the DFG *Eristalis* proposal | — |
| [`teaching/`](teaching/), [`outreach/`](outreach/) | Course integration; citizen-science design | B2 WP5 |
| [`code/`](code/), [`prior_work/`](prior_work/) | `hover` package: EMD front end, Tier-2 gap-junction SNN, **Tier-1 HH model ported from MESH** (`tier1_hh.py`), **MIO controversial-stimulus search** (`mio_search.py`, Fig. B1g); ALIstim notebook | preliminary results |
| [`tools/`](tools/) | `check_limits.py` (abstract, word counts, Resources, budget cap) · `render_pdf.py` (ERC-format PDFs with **real page counts**) · `render_figures.py`, `make_gantt_svg.py`, `make_fig_B1.py` · `export_docx.sh` | — |

## Quick start

```bash
python3 tools/check_limits.py            # abstract, word-count estimates, Resources length, budget cap
python3 tools/render_pdf.py              # build/*.pdf in ERC format (A4, 11 pt, 2 cm margins, headers) + page counts
python3 tools/make_gantt_svg.py && python3 tools/render_figures.py   # figures -> PNG/PDF
cd code && python3 -m hover.demo         # EMD -> LPTC -> RMN SNN + one controversial-stimulus search
python3 -m hover.tests.test_models       # unit tests (NumPy only)
bash tools/export_docx.sh                # .docx for pasting into the official ERC templates (needs pandoc)
```

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
1. Fig. B1 is assembled; replace panel (d) with a cleaner export of the Tier-1 traces from MESH if
   you have one, and re-run `python -m hover.mio_search` once WP2-style receptive fields or
   conductances are updated (the panel and `mio_search_result.json` regenerate).
2. Post the Kviatko *et al.* manuscript on bioRxiv before 12 Jan and add the DOI to references [2].
3. Fill the `[fill]` / `[verify]` marks in the CV (defence date, roles in co-authored papers, grants).
4. Ask three readers to test Part I (an ERC grantee, a non-fly neuroscientist, a computer-vision
   colleague); see `docs/submission_plan.md`.

Admin (to be handled separately): IU PIC, GEP, support letter, cost rates, doctoral route; PhD
defence-date document; MPG and LMU consent, PICs and budget sections; consent from Fenk and Merrill
and the written scope agreement with the Fenk lab's ERC project; DFG eligibility of IU staff.
