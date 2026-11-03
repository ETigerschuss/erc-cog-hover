# HOVER: ERC Consolidator Grant 2027 application workspace

**HOVER: Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits:
from sexually dimorphic connectomes to bio-inspired computer vision**

| | |
|---|---|
| PI | Prof. Dr. Étienne Serbe-Kamp (ORCID 0000-0002-7097-6274), Professor of Computer Vision |
| Host | IU Internationale Hochschule, Germany (eligible; GEP and PIC still to be confirmed) |
| Call | **ERC-2027-COG**, deadline **Tue 12 Jan 2027**; plan to submit **Thu 7 Jan** |
| Eligibility | PhD 2016, inside the CoG-2027 window (PhD defended 1 Jan 2012 – 31 Dec 2021) |
| Panel | LS5 primary, PE6 secondary |
| Budget | €2.0 M / 60 months (placeholder figures) |
| Backup | DFG Sachbeihilfe **only if** the ERC fails → [`docs/dfg_backup_strategy.md`](docs/dfg_backup_strategy.md) |
| Status | **Draft 1**: aligned with the 2027 *Information for Applicants* (v11.0, 22 Jul 2026) |

## The project in one paragraph

Flies solve, with ~10⁵ neurons and a few milliwatts, visual problems that computer vision still finds
hard: ego-motion estimation, small-target pursuit in clutter and gaze stabilisation. Male
*Eristalis* hoverflies add a twist. Their visual system is sexually dimorphic, with a dorso-frontal
"bright zone", a narrowed HSN receptive field and an extra HS cell (HSNE), and they have **a male-only
third retinal muscle**. The same body plan therefore carries two visual "architectures" tuned to
different tasks.

HOVER asks **which circuit motifs make a visual system task-specific, and whether they carry over to
engineered spiking vision**. It will:

1. build connectome-constrained spiking models of the fly gaze pathway, including gap junctions
   found with MESH, at three levels: biophysical, mathematically reduced, trainable;
2. test the dimorphic predictions in *Eristalis* with controversial stimuli;
3. ask whether the male features emerge as task-optimal solutions;
4. transfer the motifs to event-camera vision with active micro-movements;
5. run everything on SpikerBots in IU computer-vision courses and a citizen-science "robot zoo".

## Repository map

| Path | ERC part | Limit |
|---|---|---|
| [`proposal/B1_cover_page.md`](proposal/B1_cover_page.md) | B1 cover: title, acronym, abstract, panels, cross-panel justification | not counted |
| [`proposal/B1_PartI_synopsis.md`](proposal/B1_PartI_synopsis.md) | **B1 Part I of the Scientific Proposal** (read at Step 1) | **5 pp** |
| [`proposal/B1_CV_track_record.md`](proposal/B1_CV_track_record.md) | **B1 CV and Track Record** (read at Step 1) | **4 pp** |
| [`proposal/B2_PartII.md`](proposal/B2_PartII.md) | **B2 Part II of the Scientific Proposal** + Funding ID | **7 pp** |
| [`proposal/abstract.md`](proposal/abstract.md) | Part A abstract (≈ ½ page) | 2000 chars |
| [`proposal/PartA_budget_resources.md`](proposal/PartA_budget_resources.md) | Part A budget table + Resources text | 8000 chars |
| [`proposal/gantt.md`](proposal/gantt.md), [`proposal/references.md`](proposal/references.md) | Timeline; bibliography | — |
| [`admin/host_support_letter.md`](admin/host_support_letter.md) | Mandatory host letter (official 2027 wording, IU filled in) | annex |
| [`admin/ethics_security_self_assessment.md`](admin/ethics_security_self_assessment.md) | Ethics and security tables, drafted | Part A |
| [`docs/ERC_CoG_call_requirements.md`](docs/ERC_CoG_call_requirements.md) | The 2027 rules with page references | — |
| [`docs/eligibility_and_host_checklist.md`](docs/eligibility_and_host_checklist.md) | What's settled, what IU and you must do, open decisions | — |
| [`docs/submission_plan.md`](docs/submission_plan.md) | Week-by-week plan to 12 Jan 2027 | — |
| [`docs/coi_backyard_brains.md`](docs/coi_backyard_brains.md) | Conflict-of-interest plan (Backyard Brains / SpikerBot) | — |
| [`docs/dfg_backup_strategy.md`](docs/dfg_backup_strategy.md) | Sequential DFG backup, timing, the pending 2026 DFG proposal | — |
| [`docs/positioning_from_DFG.md`](docs/positioning_from_DFG.md) | What changes from the DFG *Eristalis* proposal | — |
| [`teaching/`](teaching/), [`outreach/`](outreach/) | Course integration; citizen-science design | B2 WP5 |
| [`code/`](code/), [`prior_work/`](prior_work/) | `hover` package (EMD, gap-junction SNN, controversial stimuli); ALIstim notebook | preliminary results |
| [`tools/`](tools/) | `check_limits.py` (abstract, pages, Resources, budget cap); `export_docx.sh` | — |

## Quick start

```bash
python3 tools/check_limits.py            # abstract, page estimates, Resources length, budget cap
cd code && python3 -m hover.demo         # EMD → LPTC → RMN SNN + one controversial-stimulus search
python3 -m hover.tests.test_models       # unit tests (NumPy only)
```

```bash
bash tools/export_docx.sh                # .docx for pasting into the official ERC templates (needs pandoc)
```

## Important before submission

- **These are drafts.** The ERC allows AI help in preparing a proposal, but the PI keeps full
  authorship responsibility, and every proposal is screened for plagiarism (IfA p. 8, 18). Rewrite
  in your own voice, and check every claim and every `[fill]` / `[verify]`.
- **Author lists must be exactly as published**, with joint authorships marked (IfA p. 28).
- **No support letters.** The ERC disregards them. Instead, obtain **written consent** from every
  researcher named in the proposal before the deadline (IfA p. 26, 33).
- Use the **official B1/B2 templates** from the submission system, with a header on every page:
  `Serbe-Kamp | HOVER | Part B1/B2`.

## Open items (details in the checklist)

1. IU: PIC, GEP, signed support letter, cost rates, doctoral route.
2. PhD defence-date document.
3. Status of the 2026 DFG proposal (Funding ID).
4. DFG eligibility of IU staff (for the backup).
5. Where the experiments happen.
6. What coda.science provides. The site could not be reached from this environment; cite it correctly.
