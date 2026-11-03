<!-- ERC-2027-CoG Part B2: Part II of the Scientific Proposal | max 7 pages, references excluded (IfA p. 28)
Content: detailed implementation — methodology, work plan, risk assessment and mitigation, further background not in Part I.
Must NOT repeat Part I; must be consistent with the Part A Resources section (budget table prevails).
Step 2 questions answered here: methodology and working arrangements appropriate? timescales and resources adequate and justified?
Header on every page: Serbe-Kamp | HOVER | Part B2 -->

# HOVER: Part II of the Scientific Proposal

## 1. Preliminary results and further background

*(Only what Part I does not already say. About ¾ page, with Fig. B1: MESH contact map + EM; Tier-1 traces.)*

**P1 MESH, a connectome-scale search for electrical synapses.** MESH finds all appositions (≤ 100 nm)
between selected FlyWire/FAFB neurons using a k-d tree over mesh vertices. It groups them into sites,
keeps only sites where the two segmentations are truly adjacent, subtracts annotated chemical synapses,
and serves EM stacks for expert proofreading. For the 26-neuron LPTC–motor-neuron set it found 619
contact sites. Of these, 49 motor-neuron–LPTC sites survived validation (2,895 EM images, public
viewer), including the best-characterised candidate, MOT_R ↔ HSN_R [14].

**P2 A gap-junction visuomotor pathway.** Neurobiotin fills show RMN MOS coupled to VS and HS cells,
and RMN MOT coupled to HS cells only. Two-photon imaging shows that RMN preferred directions are
predicted by gap-junction connectivity alone, giving a vectorial efference copy [14].

**P3 Tier-1 model.** A Hodgkin–Huxley model of the right-eye circuit, with electrical and chemical
coupling, runs inside MESH. It reproduces sustained RMN spiking and the eye-displacement direction
seen after optogenetic MOT/MOS activation (unpublished).

**P4 Differentiable detectors and controversial stimuli (ALIstim).** A PyTorch bank of
Hassenstein–Reichardt and Barlow–Levick detectors with ON/OFF pathways, motion opponency [26] and LPTC
integration, used to optimise stimuli by gradient descent. An open NumPy reimplementation with
gap-junction-coupled LPTC → RMN networks for *Drosophila* and for male and female *Eristalis* already
computes stimuli that separate competing male-circuit hypotheses (proof of principle, placeholder
parameters).

**P5 Comparative anatomy.** Micro-CT of retinal muscles across Diptera, including male and female
*Eristalis*: MOS and MOT in both sexes, plus the male-only third muscle (MOI) [2].

**P6 Teaching and outreach.** [fill: SpikerBot workshops, participants, citizen-science projects,
IU courses from 2026/27, with numbers]

## 2. Methodology and work plan

Five work packages share one modelling ladder and one stimulus engine (Fig. B2: dependency diagram).
"→ H" marks the hypothesis a task tests. D = deliverable, M = project month.

### WP1 Connectome → spiking circuit, including electrical synapses (M1–36; Postdoc 1, PhD 1, PI) → H1

- **T1.1 Scale MESH.** Extend the neuron set to all LPTCs, RMNs and optic-flow descending neurons in
  both hemispheres (FlyWire cell types).
  - *Gap-junction classifier:* a 3D CNN on EM cutouts around appositions. Positives are
    expert-validated appositions without a chemical synapse; negatives are rejected sites.
  - *Proofreading:* uncertainty-ranked queues feed expert and community proofreading (T5.3).
  - *Validation:* held-out expert labels (precision/recall) and agreement with the neurobiotin
    coupling data (P2).
  - **D1.1 (M18):** open gap-junction candidate atlas of the fly visuomotor system.
- **T1.2 Tier 1, biophysical.** Morphologically reduced multi-compartment HS/VS cells (from FlyWire
  skeletons), active RMN spike generation, and GJ conductances proportional to validated apposition
  area. Fitted to RMN imaging (P2) and published HS/VS physiology [11,31,32].
- **T1.3 Tier 2, reduced.** LIF/AdEx point neurons with linear GJ coupling. Effective coupling
  conductances come from Tier-1 transfer impedances; AdEx parameters are fitted to Tier-1 f–I curves.
  We report error bounds on RMN tuning and latency.
  **D1.2 (M24):** reduced model plus the reduction method as a reusable tool.
- **T1.4 Tier 3, trainable.** A connectome-masked SNN with sign constraints, trained with surrogate
  gradients. Its front end is the differentiable detector bank (P4).
- **T1.5 Motor readout.** Muscle activation → force (Hill-type model) → retinal displacement via
  measured muscle base vectors [7]. Validated against retinal tracking in WP2.

### WP2 The dimorphic gaze circuit of *Eristalis* (M6–48; PhD 2 at MPI-BI, PhD 4 at LMU, PI) → H2, H2b

- **T2.1 Model families.** Male and female circuits are built by homology (HSN, HSE, HSS, HSNE, VS;
  RMN MOT/MOS/MOI), constrained by the CT atlas (P5), fills (T2.3) and published *Eristalis*
  LPTC/descending-neuron physiology [1,15,23].
  Four male hypotheses: **M-H2** (HSN → MOI), **M-HSNE** (HSNE → MOI), **M-HS** (pooled HS → MOI),
  **M-VS** (VS → MOI).
- **T2.2 Controversial stimuli.** For every model pair, optimise stimuli that maximise the predicted
  difference in retinal trajectory or MOI activity. Stimuli stay within display limits (luminance,
  contrast, spatio-temporal frequency) and under a naturalness prior. The expected evidence per trial
  sets the number of animals, i.e. the **power analysis is done in silico before any experiment**.
  **D2.1 (M24):** the stimulus set.
- **T2.3 Experiments (MPI for Biological Intelligence, Fenk lab; PhD 2).** Tethered male and female *Eristalis*:
  - retinal tracking through the cornea (IR high-speed video, deep-red illumination [7]);
  - EMG of MOT, MOS and MOI;
  - neurobiotin fills of HSN and HSNE to test coupling to the RMNs;
  - stimulation on the open insect stimulation platform [22]; animals reared year-round [19].

  Analysis: hierarchical Bayesian model comparison across animals [35].
- **T2.4 Free-flight retinal tracking (high risk, high gain).** Pursuit of artificial targets [21]
  in an arena with head-mounted ultralight markers. Started only if T2.3 succeeds; the other WPs do
  not depend on it.
- **T2.5 Developmental and genetic origin of the third muscle (LMU, R. Merrill; PhD 4) → H2b.**
  The third muscle exists only in males. Where does it come from, and what makes it male?
  - *Origin:* a developmental time series of male and female pupae (micro-CT and phalloidin confocal
    imaging) identifies the anlage the muscle forms from. The comparative data suggest that retinal
    muscles were repurposed from antennal muscles [2].
  - *Genes:* sex- and stage-resolved RNA-seq of the anlage region, and of the motor-neuron cell bodies
    once identified, finds male-biased muscle-identity genes and sex-determination factors
    (*doublesex*, *fruitless*). Candidates are localised by in situ HCR in the muscle and in RMN MOI.
  - *H2b, the motor neuron specifies the muscle:* in *Drosophila*, the male-specific Muscle of Lawrence
    forms only when its motor neurons carry the male *fruitless* program [42,43]. We predict the same
    logic in *Eristalis*: a male-specific identity of RMN MOI induces the third muscle. Development would
    then mirror the circuit hypothesis H2, with one dedicated neuron for one dedicated muscle.
  - *Comparison:* syrphid species from the CT survey with and without a male third muscle test whether
    candidate changes track the trait, using public genome assemblies where they exist [44].
  - *Exploratory, high risk:* RNAi knock-down of candidates in pupae.

### WP3 Theory: why is vision dimorphic? (M12–54; Postdoc 1, PI) → H3

- **T3.1 Embodied simulator.** Compound-eye sampling (including the male bright-zone resolution
  [15]), retinal actuators, simplified flight dynamics. GPU-based and open.
- **T3.2 Task optimisation.**
  - Tier-3 networks are trained on *pursuit* (small fast targets in clutter [16,21]) or on
    *stabilisation* (hovering against optic flow; feeding approach [18]).
  - Both conditions share the same wiring prior and the same spike-count energy penalty, and both
    are offered a third actuator.
  - Readouts: receptive-field width and position of HSN-like units, actuator recruitment, and the
    performance–energy trade-off.
  - Controls: shuffled wiring prior, a range of energy penalties, ≥ 10 seeds.
- **T3.3 Analysis.** Linear-response and mean-field theory of GJ-coupled populations;
  information-theoretic receptive-field analysis; ablations to find the minimal motif set.
  **D3.2 (M48):** the motif catalogue.

### WP4 Bio-inspired active computer vision (M18–60; Postdoc 2, PhD 3, PI) → H4

- **T4.1 Active event camera.** An event camera on a piezo/galvo stage replays recorded fly retinal
  trajectories (WP2) and synthetic micro-movements. We measure event yield and acuity on static scenes.
- **T4.2 Motif SNNs.** The catalogue motifs (D3.2) become event-driven SNNs, deployed on neuromorphic
  hardware through European access programmes.
- **T4.3 Benchmarks (civil tasks).** Three tasks:
  - small-target detection in clutter;
  - closed-loop target tracking on a ground robot;
  - ego-motion and velocity estimation, against the `deepfly` CNN [38].

  Baselines are matched in parameters and synaptic operations. Metrics: accuracy, latency, synaptic
  operations and measured energy. **D4.3 (M54):** open benchmark.
- **T4.4 Controversial stimuli for machines.** The WP2 engine is applied to CNN-vs-SNN pairs as a
  robustness diagnostic.

### WP5 Teaching, citizen science, open science (M1–60; PI, student assistants, IU courses)

- **T5.1 Course integration.** HOVER modules in IU computer-vision courses every semester (see the
  teaching plan); student projects deliver benchmark entries and robot data.
- **T5.2 Robot zoo.** Schools and makerspaces run *Drosophila*-, female- and male-type circuits on
  standard pursuit and stabilisation tasks. Logs go to an open database and are analysed with
  mixed-effects models.
- **T5.3 MESH community proofreading** of candidate sites, feeding T1.1.
- **T5.4 Open releases.** Code under MIT, data under CC-BY, teacher kits. Firmware is hardware-neutral,
  with SpikerBot as the reference platform plus one open platform.
- **T5.5 Evaluation.** Learning outcomes measured before and after; IU ethics approval.

*Conflict of interest:* the PI holds a role at Backyard Brains, the SpikerBot manufacturer. IU
procurement buys hardware without the PI's involvement, and all code runs on open hardware.

## 3. Timeline, milestones and decision points

*(Fig. B3: Gantt chart from `gantt.md`.)*

| MS | Month | Milestone | Decision |
|---|---|---|---|
| MS1 | 12 | GJ atlas v1; Tier-2 *Drosophila* model | Tier-2 error vs Tier 1 < 10 %? If not, keep Tier 1 for WP2 |
| MS2 | 24 | Male/female model families; controversial stimuli designed in silico | Stimuli separate the model families with the planned number of animals? If not, refine models before experiments |
| MS3 | 30 | Active event camera running; robot zoo launched | — |
| MS4 | 36 | H1 decided; tethered *Eristalis* data complete | Fixes the constraints for WP3; go/no-go for T2.4 |
| MS5 | 48 | H3 and H2b decided; motif catalogue | Motifs passed to WP4 |
| MS6 | 60 | H4 decided; benchmark, models and kits released | — |

## 4. Hypotheses: tests and what each outcome teaches

| Hyp. | Supported if | Falsified if | Value if falsified |
|---|---|---|---|
| H1 | The Tier-2 SNN with EM-derived weights predicts RMN preferred directions (± 15°) and eye-movement direction | Connectivity-only models miss ≥ 2 RMN tunings | Shows unannotated or neuromodulatory inputs matter; widens the MESH search |
| H2 | Third-muscle activity follows HSN-preferred motion confined to the dorso-frontal field | Third-muscle EMG tracks MOT-type or VS-type motion | The muscle is a general range extension. The model comparison is still decisive. |
| H2b | *fruitless*/*doublesex* are expressed male-specifically in RMN MOI and the MOI anlage; the muscle forms from a defined anlage only in males | No sex-biased expression in the motor neuron; muscle specification is cell-autonomous | Points to a muscle-intrinsic program. Still the first developmental account of a sexually dimorphic eye muscle |
| H3 | Narrowed dorso-frontal integration and an extra effector emerge only under the pursuit objective | They emerge under both objectives, or neither | Points to developmental or genetic constraint rather than task optimality |
| H4 | Motif SNN + active micro-movement beats matched baselines on ≥ 2 of 3 benchmarks in accuracy per energy | No advantage | A rigorous negative result for "bio-inspired" claims |

## 5. Risks and mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GJ classifier does not generalise beyond validated sites | Medium | Medium | Expert + community proofreading; GJ weights become free parameters bounded by apposition area |
| No *Eristalis* connectome, so the homology mapping is wrong | Medium | High | Competing model families instead of one model; stimuli built to discriminate them; fills as ground truth |
| Experiments at partner sites delayed | Medium | High | PhD 2 and PhD 4 are HOVER team members hosted at MPI-BI and LMU (additional beneficiaries), not favours; WP1, WP3 and WP4 do not wait for them; stimuli are designed in silico first |
| Developing muscle tissue too small for RNA-seq | Medium | Medium | Pooled samples; low-input or single-nucleus protocols; in situ HCR for candidates known from *Drosophila* as fallback |
| Free-flight tracking fails | High | Medium | Tethered and closed-loop virtual flight; no other WP depends on T2.4 |
| H3 null | Medium | Low | Interpretable negative result (constraint vs optimality) |
| SNNs lose to deep baselines (H4 null) | Medium | Medium | Report rigorously; hybrid motif front end + learned back end as a secondary result |
| Recruitment delays | Low | Medium | Posting on EURAXESS at signature; IU computer-vision students as the MSc → PhD pipeline |

## 6. Team, working arrangements and environment

- **PI (50 %, above the 40 % minimum):** scientific lead; WP1 and WP3 modelling; WP5 lead.
- **Team (one PI, three beneficiaries):**
  - at IU: Postdoc 1, computational neuroscience (48 months); Postdoc 2, neuromorphic computer vision
    (24 months, from M25); PhD 1, connectomics/ML; PhD 3, SNN vision; student assistants;
  - at MPI for Biological Intelligence (Active Sensing, L. Fenk): PhD 2, hoverfly physiology;
  - at LMU Munich (R. Merrill): PhD 4, evolutionary developmental genetics.

  The PI selects and supervises all team members. The partner-group leaders co-supervise locally and
  give access to their set-ups.
- **Doctoral route:** PhD students enrol at LMU (doctorate-granting), co-supervised by the PI
  [confirm the agreement and whether IU has doctoral rights].
- **Collaborators** (written consent obtained before submission; roles limited to what is stated):
  L. Fenk: physiology set-ups, *Drosophila* RMN data, micro-CT access; R. Merrill: genomics and
  developmental genetics; [neuromorphic hardware platform].
- **Working arrangements:** a monthly all-team meeting in Munich; quarterly WP reviews against the
  milestones; a shared code and data base with continuous integration; a data management plan by M6.
- **Environment:** the IU computer-vision group, students and GPU resources; physiology set-ups at
  MPI-BI; genomics infrastructure at LMU.

## 7. Ethics, civil focus, open science and data

- **Civil focus:** HOVER has an exclusive focus on civil applications. Insects only (no
  vertebrates). Human participants (students, citizens including school pupils) take part with
  informed and parental consent under IU ethics approval, with GDPR-compliant data handling.
- **AI:** HOVER develops AI-based vision models; no personal data are used for training.
- **Open science:** all code is released under MIT, data under CC-BY via DANDI/Zenodo, with immediate
  open access to publications. Details are in the ethics self-assessment.

---

## Funding ID (not counted in the page limit)

*Required: current research grants and their subject, and any ongoing application for work related to
this proposal (IfA p. 29).*

| Title | Funder | Amount | Period | Role | Status | Relation to HOVER |
|---|---|---|---|---|---|---|
| [IU start-up package] | IU | [€] | [ ] | PI | [current] | [what it pays for; no overlap with HOVER costs] |
| [other current grants] | | | | | | |

No applications for work related to HOVER are pending.

## References

See `references.md` (not counted in the page limit).
