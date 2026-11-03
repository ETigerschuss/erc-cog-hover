<!-- ERC-2027-CoG Part B1: Part I of the Scientific Proposal | max 5 pages, excluding cover page and references
Must contain: (1) current state of knowledge, (2) scientific question and objectives, (3) overall approach (IfA p. 28).
Read at Step 1 by panel members acting as GENERALISTS: keep jargon low. Header on every page: Serbe-Kamp | HOVER | Part B1 -->

# HOVER: Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits

**PI:** Étienne Serbe-Kamp · **Host:** IU Internationale Hochschule (Germany) · **Duration:** 60 months · **Panel:** LS5 (secondary PE6)

## 1. The problem: one body plan, two visual machines

Animal visual systems are not general-purpose cameras. They are tuned to the tasks an animal must solve.
Usually we cannot tell *which* features of a circuit exist *because of* a task, since
species differ in too many ways at once. Sexual dimorphism removes that confound: males
and females of the same species share genome, development and most of their circuitry,
yet differ in the visual tasks evolution has optimised them for.

Male hoverflies (*Eristalis tenax*) chase conspecifics in fast aerial pursuits.
Females mainly hover, feed and lay eggs. The male visual system differs from the female one at every level we have examined:
a dorso-frontal "bright zone" with higher acuity and contrast sensitivity [15]; a
**sexually dimorphic HS cell (HSN)** whose receptive field is narrowed to that zone [1];
dimorphic velocity coding in optic-flow descending neurons [23]; and, as our comparative
micro-CT survey across Diptera revealed, **a male-only third retinal muscle**, the
only sexually dimorphic eye muscle known in insects [2]. Flies move their retinae
beneath stationary lenses to stabilise and refresh the image [7]. Male *Eristalis* has therefore
evolved not only different sensors but a different **active-vision effector**.

Computer vision faces the same design question with less success. Engineers either build one
general architecture and train it on everything, or hand-design task pipelines.
Event cameras and spiking neural networks (SNNs) promise fly-like efficiency, but
current SNNs are mostly deep networks translated into spikes. **They do not reflect the
circuit motifs that make biological vision fast, sparse and robust.**

**HOVER asks: which circuit motifs make a visual system task-specific, and do those motifs
carry over to engineered spiking vision?** We answer this by building connectome-constrained
spiking models of the fly motion-vision and gaze pathway, testing their dimorphic
predictions in *Eristalis*, extracting the minimal motifs mathematically, and deploying
them in event-based computer vision and in robots used by students and the public.

## 2. State of the art and the gap

**Connectomes have outpaced models.** The FlyWire whole-brain connectome [12,13] and
derived optic-lobe datasets (accessible through Codex and platforms such as coda.science)
give synapse-level wiring for the entire *Drosophila* visual system. Connectome-constrained
network models predict neural tuning of the motion pathway well. However, they (i) use
**chemical synapses only**, because **gap junctions are not annotated** in any whole-brain EM
connectome; (ii) stop at the visual neurons and do not reach motor output; and (iii) exist for one
sex of one species.

**Electrical synapses are the missing link to motor output.** We showed that
lobula-plate tangential cells (LPTCs) drive the retinal motor neurons (RMNs) **through gap
junctions**, and that the RMN preferred directions are predicted from gap-junction
connectivity alone [14; Falt, Ammer *et al.*, bioRxiv 2026, doi:10.64898/2026.08.11.744090].
To find these synapses at connectome scale, I developed **MESH**, a pipeline that detects
neuron–neuron appositions in FlyWire, validates them against the segmentation and serves
the EM for expert proofreading. MESH has already yielded 49 validated motor-neuron–LPTC contact
sites (619 candidates in total) and the best-characterised putative gap junction in the fly
visual-motor pathway (MOT_R ↔ HSN_R).

**Active vision is the missing link to behaviour, and to engineering.** Retinal
micro-movements in flies improve acuity and prevent adaptation [6,7]. Event cameras go
silent without relative motion, the same problem as an adapting photoreceptor. No
connectome-grounded model of an active-vision loop exists in any animal. The *Eristalis*
third muscle offers a unique test of whether such an effector is
**task-specific** or general.

**Comparing models needs better stimuli.** Standard gratings cannot tell competing
circuit models apart. Optimised **controversial stimuli** [30] can. My group already
built a differentiable framework of Hassenstein–Reichardt and Barlow–Levick detectors
with ON/OFF pathways, motion opponency [26] and LPTC integration, with which we optimise
stimuli by gradient descent (ALIstim, preliminary result P3).

## 3. Objectives and hypotheses

**O1. Build a multi-tier, connectome-constrained SNN of the fly gaze pathway**, from
photoreceptors to retinal displacement, *including electrical synapses*.
→ **H1 (Sufficiency):** chemical + gap-junction connectivity from EM is sufficient to
predict RMN tuning, eye-movement direction and latency, and a mathematically reduced
SNN with ≥10× fewer state variables preserves these predictions.

**O2. Test the dimorphic gaze circuit of *Eristalis*.**
→ **H2 (Dedicated channel):** in males, the dimorphic HSN drives a dedicated motor
neuron (RMN MOI) of the third muscle, forming a pursuit-specific active-vision channel.
HSN/HSNE also feed the shared stabilisation channel (MOT/MOS) in both sexes.
→ **H2b (Origin):** the male muscle is specified by its motor neuron, just as the male-specific
Muscle of Lawrence of *Drosophila* forms only under *fruitless*-expressing motor neurons [42,43].

**O3. Explain the dimorphism as a task-optimal solution.**
→ **H3 (Task optimality):** when connectome-constrained SNNs are trained on male-typical
(small-fast-target pursuit) versus female-typical (hover stabilisation, feeding approach)
tasks under identical wiring and energy budgets, the male-specific features
(narrowed dorso-frontal integration, an extra effector) emerge *only* under the pursuit objective.

**O4. Transfer the motifs to computer vision.**
→ **H4 (Transfer):** event-based SNNs built from the extracted motifs, *with active
micro-movements of the sensor*, outperform size- and energy-matched deep-network
baselines on small-target detection in clutter and ego-motion estimation.

**O5. Make the loop public.** Every model in O1–O4 runs on low-cost spiking robots
(SpikerBot) and in IU computer-vision courses. Students and citizens test the models,
generate data and proofread gap junctions.

## 4. Approach

Five work packages are linked by one modelling ladder (Fig. A) and one stimulus engine.

**WP1 Connectome → spiking circuit (M1–36).** (a) Scale MESH from 26 neurons to the full
LPTC–motor and LPTC–descending-neuron network. Train a gap-junction detector on the
expert-validated sites (membrane apposition < 20 nm, pentalaminar profile,
mitochondrial enrichment) and confirm candidates by community proofreading (WP5).
(b) Build three model tiers: **Tier 1**, Hodgkin–Huxley / compartmental neurons (extending
the existing MESH model); **Tier 2**, LIF/AdEx point neurons with gap-junction coupling,
derived from Tier 1 by systematic reduction (passive cable → effective coupling
conductances, spike-threshold adaptation fits); **Tier 3**, trainable SNNs whose
connectivity is masked by the connectome, with surrogate-gradient training. (c) Readout:
muscle force → retinal displacement via measured muscle base vectors [7]. Validated
against *Drosophila* RMN calcium imaging and EMG (partner: Fenk lab, MPI-BI).

**WP2 Dimorphic *Eristalis* gaze circuit (M6–48).** No *Eristalis* connectome exists, so we
map the *Drosophila* circuit onto male and female *Eristalis* using homologous cell types
(HSN, HSE, HSS, VS1–n, RMNs) plus the hoverfly-specific HSNE, constrained by our CT
atlas, neurobiotin fills and published LPTC physiology [1,15,23]. This yields **competing
male models** (H2 vs. alternatives: shared drive, HSNE-driven MOI, VS-driven MOI). Using the
stimulus engine, we generate the stimuli where these models disagree most. We then
present them while tracking retinal movements through the cornea (deep-red illumination,
high-speed IR video; established in *Drosophila* [7]) in tethered males and females,
with EMG of all three muscles (at MPI for Biological Intelligence, Fenk lab).
*High-risk/high-gain:* retinal tracking during free flight, using head-mounted
ultralight markers in a pursuit arena. With R. Merrill (LMU), sex- and stage-resolved
transcriptomics and in situ mapping trace where the third muscle comes from and which
genes make it male (H2b).

**WP3 Theory: why dimorphic? (M12–54).** Using Tier-3 models and an embodied simulator
(fly-scale optics, compound-eye sampling, retinal muscles as actuators), we optimise
networks for pursuit and for stabilisation under the same wiring prior and a spike-count
energy penalty. We test whether male-specific features *emerge* (H3), and use
mathematical analysis (linearisation around the operating point, mean-field reduction
of gap-junction-coupled populations, information-theoretic receptive-field analysis) to
identify the **minimal motif set** that accounts for task performance.

**WP4 Bio-inspired active computer vision (M18–60).** We implement the minimal motifs as
event-driven SNNs operating on event-camera input (DVS) mounted on a piezo/galvo
micro-movement stage that reproduces fly retinal movements. Benchmarks: small-target
detection in clutter (cf. STMD neurons [16]), closed-loop target tracking on mobile robots,
ego-motion estimation and gaze stabilisation on public event-camera datasets and our own
hoverfly-perspective recordings. All applications are civil. Baselines: CNN/transformer models of matched parameter count (including the
`deepfly` velocity-estimation CNN [Drews *et al.* 2020]) and standard SNN conversions.
Metrics: accuracy, latency, synaptic operations and energy on neuromorphic hardware
(e.g., SpiNNaker2 or Loihi-class chips through European access programmes).

**WP5 SpikerBot citizen science and teaching (M1–60).** All Tier-2/3 models compile to
SpikerBot (camera + spiking-neuron firmware) and to open hardware. (a) **Course
integration:** each semester, IU computer-vision students implement, test and extend
one HOVER motif (see `teaching/`). (b) **Robot zoo:** a distributed citizen-science
experiment in which schools and makerspaces run male-type vs. female-type circuits on
standardised pursuit/stabilisation tasks and upload behaviour logs, which gives thousands of
embodied model evaluations under real-world optics and noise. (c) **Gap-junction
proofreading** in the MESH web viewer, with expert consensus as gold standard. This builds on
my open-citizen-science framework [36].

## 5. Why now, why me

*Why now:* whole-brain connectomes, a validated gap-junction proofreading pipeline,
affordable event cameras, surrogate-gradient SNN training and mass-market spiking robots have
matured only in the last three years. *Why me:* I bring the rare combination this project
needs. I have done physiology and circuit discovery in fly motion vision (motion
opponency, *Nat Neurosci* 2023 [26]; elementary motion detection in the Borst lab), discovered
the gap-junction visuomotor pathway [14] and the stepwise evolution of retinal
muscles [2], built MESH, developed differentiable models for stimulus optimisation, and led
open citizen-science programmes and SpikerBot-based outreach. My professorship in
computer vision provides the students, the teaching platform and the engineering
setting in which WP4–5 become core activities rather than add-ons. HOVER is a new
programme that I lead with my own group. It does not continue my postdoctoral projects:
it moves from describing one circuit to asking *why* circuits differ between the sexes,
and what that difference teaches machines.

## 6. Expected outcomes

(1) The first connectome-constrained gaze circuit including electrical synapses, from photon to eye movement.
(2) A mechanistic and normative explanation of a visual sexual dimorphism.
(3) A tested set of fly-derived motifs for active event-based vision, released as open-source models.
(4) A citizen-science infrastructure that turns connectomics into something students can build, test and contribute to.
Beyond flies: HOVER provides a template for asking *why* a circuit is wired the way it is,
by pitting models of different "task hypotheses" against each other in animals and machines.

## References (abbreviated; full list in `references.md`)

[1] Nordström *et al.* 2008 Curr Biol · [2] **Kviatko, …, Serbe-Kamp, …, Fenk** 2026 (Diptera eye-movement evolution) · [6] Viollet 2014 · [7] Fenk *et al.* 2022 Nature · [12] Dorkenwald *et al.* 2024 Nature · [13] Zheng *et al.* 2018 Cell · [14] **Falt, Ammer *et al.*** 2026 bioRxiv doi:10.64898/2026.08.11.744090 · [15] Straw *et al.* 2006 · [16] Nordström *et al.* 2006 · [23] Nicholas *et al.* 2025 · [26] **Ammer, Serbe-Kamp *et al.*** 2023 Nat Neurosci · [30] Golan *et al.* 2020 PNAS · [36] **Serbe-Kamp *et al.*** 2023 RIO · [38] Drews *et al.* 2020 Curr Biol · [42] Lawrence & Johnston 1986 Cell · [43] Usui-Aoki *et al.* 2000 Nat Cell Biol

<!-- FIGURE A (to draw): modelling ladder. Left: EM/MESH gap junction → Tier 1 HH → Tier 2 LIF+GJ → Tier 3 trainable SNN → (WP3 task optimisation) → minimal motifs → WP4 event camera + micro-movement stage → WP5 SpikerBot. Centre: male vs female Eristalis circuits with HSN/HSNE/MOI highlighted. Right: controversial stimulus engine feeding experiments (WP2) and benchmarks (WP4). Reuse panels from DFG Fig. 1d,f and Fig. 2c. -->
