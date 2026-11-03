<!-- ERC CoG Part B2 | max 14 pages | Sections: (a) State of the art and objectives, (b) Methodology, (c) Resources -->

# HOVER: Part B2, Scientific Proposal

## Section a. State of the art and objectives

### a.1 Task-specific vision: an open question in neuroscience and computer vision

*(Expand B1a §1 to ~1 page. Key points: task-specific vs. general visual architectures;
why sexual dimorphism is the cleanest natural experiment available; the parallel problem in CV:
foundation models vs. efficient task-specific perception for drones and robots.)*

### a.2 Motion vision and gaze control in flies

- Motion detection: Hassenstein–Reichardt and Barlow–Levick mechanisms implemented by T4/T5
  with ON/OFF pathways [25,26]; motion opponency at multiple levels [26]; dynamic signal
  compression for robustness (Drews *et al.* 2020).
- LPTCs: HS/VS cells, gap-junction-coupled networks, matched filters for self-motion [11,31,32].
- Retinal muscles: MOT/MOS in *Musca*, *Calliphora* and *Drosophila* [4,5,9,10]. In *Drosophila*
  they produce OKR and saccades and enhance acuity [7]. Retinal movements evolved stepwise
  in Diptera: spontaneous movements preceded the OKR, and Syrphidae are the first family with
  MOT and the only one with a male-specific third muscle [2].
- Visuomotor pathway through gap junctions: LPTC → RMN via electrical synapses, with RMN tuning
  predicted from connectivity [14], which also provides a vectorial efference copy (Falt, Ammer *et al.* 2026).

### a.3 Hoverfly sexual dimorphism

Bright zone [15]; dimorphic HSN, isomorphic HSNE [1]; dimorphic descending neurons [23];
pursuit behaviour and target-selective descending neurons [18,20,21]; small-target
detection in clutter (STMDs) [16]; male-only third retinal muscle [2].

### a.4 Connectome-constrained models and their limits

FlyWire/FAFB [12,13]; optic-lobe connectome-constrained models; Codex and coda.science as
access platforms *(verify the datasets available on coda.science and cite them)*. Gaps:
no electrical synapses, no motor readout, single sex.

### a.5 Spiking and event-based computer vision

Event cameras; SNN training with surrogate gradients; neuromorphic hardware; active
vision and fixational eye movements in machines [5,6]. Gap: SNNs inherit deep-network
architectures. No connectome-derived active-vision SNN exists.

### a.6 Objectives and hypotheses (as B1a §3, with falsification criteria)

| Hyp. | Prediction | Falsified if | Value if falsified |
|---|---|---|---|
| H1 | Tier-2 SNN with EM-derived GJ + chemical weights reproduces RMN preferred directions (±15°) and eye-movement direction, with Tier-1 → Tier-2 error < 10 % | Connectivity-only models miss ≥ 2 RMN tunings | Shows unannotated or neuromodulatory inputs matter; MESH search widened |
| H2 | Male third muscle is activated by HSN-preferred motion confined to the dorso-frontal field; activity is absent or different in female-equivalent stimuli | Third-muscle EMG tracks MOT or VS-type motion | Shows the muscle is a general range extension. Model-selection result still decisive |
| H3 | Narrowed dorso-frontal integration + extra effector emerge only under the pursuit objective | Features emerge under both objectives, or neither | Points to developmental or genetic constraint rather than task optimality |
| H4 | Motif-SNN + active micro-movement beats matched baselines on ≥ 2 of 3 benchmarks in accuracy-per-energy | No advantage | A rigorous negative result for "bio-inspired" claims, which the field needs |

## Section b. Methodology

### b.1 Overview

Diagram (to draw): WP1 → WP2/WP3 → WP4, with WP5 running throughout, and the shared
**stimulus engine** and **modelling ladder**.

### b.2 WP1 Connectome to multi-tier spiking circuit (M1–36; lead: PI, PhD1, Postdoc1)

**Task 1.1 Scaling MESH.** Extend from the 26-neuron publication set to all LPTCs, RMNs and
optic-flow descending neurons in both hemispheres. Train a gap-junction classifier on the
expert-validated EM sites (2,895 images; positives = validated appositions without annotated
chemical synapse). Use a 3D CNN on EM cutouts, with uncertainty-ranked queues for
proofreading (WP5.3). *Deliverable D1.1:* open GJ candidate atlas.

**Task 1.2 Tier 1, biophysical.** Extend the MESH HH model: morphology-reduced compartments for
HS/VS cells, RMN spike generation, GJ conductances scaled by apposition area.
Fit to *Drosophila* RMN calcium imaging and RMN/EMG recordings (partner).

**Task 1.3 Tier 2, reduced LIF/AdEx with gap junctions.** Mathematical reduction: (i)
effective coupling from cable-theory transfer impedances, (ii) AdEx fits to Tier-1 f–I curves,
(iii) GJ as linear conductances between compartments. Provide error bounds versus Tier 1.
*Preliminary code:* `code/hover/snn.py`.

**Task 1.4 Tier 3, trainable connectome-masked SNN.** Surrogate-gradient training with weights
constrained to the EM sign and connectivity mask. Front end: the differentiable HR/BL
detector bank from ALIstim (`code/hover/emd.py`).

**Task 1.5 Motor readout.** Muscle activation → force → retinal displacement via base vectors [7].

### b.3 WP2 Dimorphic *Eristalis* gaze circuit (M6–48; PhD2, partner labs)

**Task 2.1 Homology mapping.** Build male and female *Eristalis* circuit hypotheses from
*Drosophila* (Task 1.3) + CT atlas [2] + published *Eristalis* LPTC/DN physiology [1,15,23].
Male model family: M-H2 (HSN → MOI), M-alt1 (HSNE → MOI), M-alt2 (shared HS → MOI), M-alt3 (VS → MOI).

**Task 2.2 Controversial stimuli.** For each model pair, optimise stimuli that maximise the
divergence of predicted retinal trajectories, with constraints on contrast, spatial
frequency and naturalness (`code/hover/controversial.py`). Model-discrimination power
is estimated in silico before any experiment.

**Task 2.3 Experiments (with partners).** Tethered male and female *Eristalis*: retinal
tracking through the cornea with an IR high-speed camera; EMG of MOT/MOS/third
muscle; neurobiotin fills HSN/HSNE → RMN (partner). Stimulus display: open insect
stimulation platform [22]. *Rearing:* established protocol [19].

**Task 2.4 (high-risk/high-gain) Free-flight retinal tracking during pursuit.** Ultralight
markers, multi-camera arena, artificial targets [21].

### b.4 WP3 Theory: why dimorphic? (M12–54; Postdoc1)

**Task 3.1 Embodied simulator.** Compound-eye sampling (hexagonal ommatidia, acceptance
angles, male bright-zone resolution), retinal muscle actuators, simplified flight dynamics.
Built in-house on GPU and released open.

**Task 3.2 Task optimisation.** Train Tier-3 networks on pursuit (small fast targets in
clutter) and on stabilisation (hover against wind and optic flow; feeding approach [18]).
Matched energy penalty (spike count) and wiring prior. Measure emergence of HSN-like
narrowed RFs, recruitment of a third actuator (offered to both sexes' models), and dorso-frontal specialisation.

**Task 3.3 Mathematical analysis.** Linear-response and mean-field analysis of GJ-coupled
LPTC populations. Information-theoretic RF analysis. Ablation-based minimal motif extraction.
*Deliverable D3.2:* the "motif catalogue".

### b.5 WP4 Bio-inspired active computer vision (M18–60; PhD3, CV group)

**Task 4.1 Active event camera.** DVS on a piezo/galvo stage reproducing recorded fly retinal
trajectories (OKR, saccades, micro-movements). Test whether micro-movements stop event loss on static scenes.

**Task 4.2 Motif-SNNs.** Implement motif catalogue models as event-driven SNNs
(PyTorch/Norse/Lava; deployment on neuromorphic hardware).

**Task 4.3 Benchmarks.** (i) Small-target detection in clutter; (ii) drone/target pursuit
in closed loop; (iii) ego-motion/velocity estimation (cf. `deepfly` CNN). Baselines matched
in parameters and synaptic operations. Report accuracy, latency and energy.
*Deliverable D4.3:* public benchmark + leaderboard.

**Task 4.4 Controversial stimuli for machines.** Use the WP2 engine to find inputs on which
CNNs and motif-SNNs disagree, as a diagnostic for robustness.

### b.6 WP5 Citizen science, teaching and open science (M1–60; PI, outreach coordinator)

See `teaching/cv_course_integration.md` and `outreach/citizen_science_spikerbot.md`.
Tasks: 5.1 course integration (every semester); 5.2 robot zoo (distributed experiment,
from year 2); 5.3 MESH community proofreading; 5.4 open-source releases + teacher kits;
5.5 evaluation of learning outcomes (pre/post surveys, ethics approval for human-participant data).

### b.7 Timeline, milestones and deliverables

See `gantt.md`. Key milestones:

| MS | Month | Milestone | Verifies |
|---|---|---|---|
| MS1 | 12 | MESH GJ atlas v1 + Tier-2 Drosophila model | H1 (partial) |
| MS2 | 24 | Male/female *Eristalis* model families + controversial stimuli designed in silico | H2 ready |
| MS3 | 30 | Active event camera operational; robot zoo launched | H4 ready |
| MS4 | 36 | H1 decided; *Eristalis* tethered data complete | H1, H2 |
| MS5 | 48 | H3 decided; motif catalogue | H3 |
| MS6 | 60 | H4 decided; benchmark, models and teaching kits released | H4 |

### b.8 Risks and mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GJ classifier does not generalise beyond validated sites | Medium | Medium | Expert + community proofreading; GJ weights treated as free parameters bounded by apposition area |
| No *Eristalis* connectome → homology mapping wrong | Medium | High | Competing model families (not one model); controversial stimuli designed to discriminate them; fills as ground truth |
| Partner experiments delayed | Medium | High | Two independent partners; HOVER's own eye-tracking rig at IU (non-invasive, low ethics burden) |
| Free-flight tracking fails (high-risk) | High | Medium | Tethered + closed-loop flight simulator; result independent of other WPs |
| H3 null | Medium | Low | Interpretable negative result; developmental-constraint alternative |
| SNNs lose to deep baselines (H4 null) | Medium | Medium | Report rigorously; hybrid motif-front-end + learned back-end as a secondary result |
| Host infrastructure (fly lab, GPUs) | **to assess** | High | Host letter commitments; cloud/HPC budget; partner lab space |

### b.9 Ethics, open science, data

Invertebrates: no animal-experiment licence in DE/EU; follow 3R principles anyway. Human
participants (students, citizens): survey data → GDPR-compliant, IU ethics committee;
robot logs anonymised. All code MIT, data CC-BY, NWB/DANDI for physiology, Zenodo DOIs.

## Section c. Resources

### c.1 Team

| Role | FTE | Months | Profile |
|---|---|---|---|
| PI | 50 % | 60 | Overall lead, WP1/3/5 |
| Postdoc 1, computational neuroscience | 100 % | 48 | Tier 1–3 models, theory (WP1, WP3) |
| Postdoc 2, neuromorphic CV | 100 % | 36 | Active event camera, benchmarks (WP4) |
| PhD 1, connectomics/ML | 100 % | 48 | MESH scaling, GJ classifier (WP1) |
| PhD 2, hoverfly physiology/behaviour | 100 % | 48 | WP2 (co-supervised with partner lab) |
| PhD 3, SNN/CV | 100 % | 48 | WP4 |
| Outreach & citizen-science coordinator / research engineer | 50 % | 60 | WP5, robot firmware, kits |
| Student assistants (HiWi) | 2 × 10 h/wk | 60 | Proofreading, teaching kits |

### c.2 Budget justification

See `budget.md`. Major items: personnel (~70 %), event cameras + micro-movement stage,
high-speed IR cameras, GPU server, SpikerBot/open-robot fleet for courses and the zoo
(with procurement justification, see COI note), hoverfly rearing, travel to partner labs,
neuromorphic hardware access, open-access fees.

### c.3 Host commitment

Protected research time, lab space for fly rearing and the eye-tracking rig, PhD
supervision rights or co-supervision agreement, HPC access, matching for the outreach
coordinator. See `admin/host_support_letter_template.md`.
