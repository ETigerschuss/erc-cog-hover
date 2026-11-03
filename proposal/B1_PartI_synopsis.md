<!-- ERC-2027-CoG Part B1: Part I of the Scientific Proposal | max 5 pages, excluding cover page and references
Must contain: (1) current state of knowledge, (2) scientific question and objectives, (3) overall approach (IfA p. 28).
Read at Step 1 by panel members acting as GENERALISTS: keep jargon low. Header on every page: Serbe-Kamp | HOVER | Part B1
Fig. A (proposal/figures/fig_A_overview.png) takes about one third of a page; the text below is sized for the rest.
[verify] = check against the source before submission -->

# HOVER: Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits

**PI:** Étienne Serbe-Kamp · **Host:** IU Internationale Hochschule (Germany) · **Partners:** MPI for Biological Intelligence, LMU Munich · **Duration:** 60 months · **Panel:** LS5 (secondary PE6)

## 1. The question

Every visual system is a compromise shaped by the tasks its owner must solve. Flies solve, with about
10⁵ neurons and a few milliwatts, problems that machine vision still finds hard: estimating self-motion
from optic flow, detecting and chasing a small target in clutter, and keeping the gaze stable. Which
features of their circuits exist *because of* a task? Comparing species cannot answer this: species
differ in too many ways at once. Evolution has run a cleaner experiment. In the hoverfly, males and
females share a genome, a development and a brain plan, yet the male eye is built for one extra task,
the high-speed aerial pursuit of mates. **HOVER asks which circuit motifs make a visual system
task-specific, and whether those motifs are design principles that engineered spiking vision can
use.** It answers in a loop (Fig. A): build a spiking model of the complete fly gaze circuit from the
connectome; test its sex-specific predictions in hoverflies; explain the dimorphism by training the
model for the male task; transfer the motifs to event-based vision on neuromorphic hardware and
flying robots; and validate the models at scale with students and citizens.

## 2. A natural experiment: one genome, two visual machines

Male hoverflies (*Eristalis tenax*) chase conspecifics in fast aerial pursuits with interception
courses [71,72]; females hover, feed and lay eggs. Male specialisations are known at every level.
The male eye has a dorso-frontal "bright zone" with larger facets, faster photoreceptors and higher
contrast sensitivity [15], the hoverfly version of the "love spot" of blowflies and houseflies, where
photoreceptor speed is matched to the demands of chasing [76] and male-specific lobula neurons
exist [74,75]. One of the three horizontal-system cells (HSN), a wide-field motion neuron, has its
receptive field narrowed to that zone in males, and males carry an additional cell, HSNE [1].
Optic-flow descending neurons are sexually dimorphic at high velocities, although optomotor flight
behaviour is not [23]. Hoverflies also have small-target motion detectors of remarkable sensitivity
[16,62], and the male pursuit itself has been quantified in the laboratory [21].

Our own recent work adds the missing level: the effector. Flies move their retinas beneath the
stationary lenses with small muscles, producing both an optokinetic reflex and spontaneous
saccade-like shifts [7]. In a comparative survey of 167 insect species by micro-CT and synchrotron
tomography, with behaviour in 59 of them, we found retinal movements only in Diptera, reconstructed
their stepwise evolution (spontaneous movements came before the stabilising reflex) and discovered in
hoverflies **a male-only third retinal muscle, the M. interocularis (MIO)**, lodged between the two
nearly fused male eyes and positioned to shift exactly the bright-zone region of the retina [2]. The
male hoverfly therefore has not only a different sensor and a different circuit but a different
*active-vision effector*: a complete pursuit channel that females lack. This is a natural knockout
experiment with an evolutionary rationale built in: the male features exist for pursuit. In
*Drosophila*, the sex-determination genes *fruitless* and *doublesex* are known to rewire visual
pathways for male courtship [77,78] and to specify a male-only muscle through its motor neuron
[42,43,79]. HOVER uses the hoverfly dimorphism three times: as a test of mechanism (which neurons
drive the MIO), as a test of optimality (do the male features emerge in a model trained for pursuit?)
and as a source of design principles for machines.

## 3. State of the art and three gaps

**Gap 1. Connectomes have outpaced models, and both miss electrical synapses.** Synapse-level wiring
diagrams now exist for the female *Drosophila* brain [12,47,48], for brain and nerve cord [49] and,
since September 2026, for the complete male central nervous system, with the first synapse-resolution
comparison of the sexes [39]. Connectome-constrained networks predict neural activity across the optic
lobe from wiring and a task [45], and a whole-brain integrate-and-fire model reproduces sensorimotor
processing [46]. All of them, however, (i) use chemical synapses only, because gap junctions are
invisible in these electron-microscopy volumes [50], (ii) stop before the motor output and (iii)
model one sex of one species in a passive setting. We have shown why this matters for gaze: the
motor neurons that move the *Drosophila* retina receive only 3 % of their chemical synapses from
visual neurons, yet they are coupled by gap junctions to the HS and VS cells, and this electrical
wiring alone predicts their direction tuning, the two-dimensional optokinetic reflex (R² = 0.99) and
an efference copy that flows back into the visual neurons during spontaneous eye movements [14].
The pathway from photoreceptor to retinal movement is now known cell by cell. To find electrical
synapses at connectome scale I built **MESH**, an open pipeline that detects membrane appositions
between neuron meshes, validates them in the electron-microscopy volume and serves them for
proofreading [41]. It defined the electrical wiring diagram in [14] and, for the 26-neuron
LPTC–motor-neuron set, yielded 49 validated contact sites out of 619 candidates.

**Gap 2. Active vision is missing from circuit models and from event-based machine vision.**
Retinal micro-movements refresh the image, defeat photoreceptor adaptation and sharpen acuity
[7,51,52]. Event cameras, the neuromorphic sensors that report only brightness changes, have the
mirror-image problem: they go blind on static scenes [53], although they now reach automotive
products [108]. Engineers have begun to add artificial microsaccades to event cameras with a rotating
prism [54], and spiking networks on neuromorphic chips now estimate optic flow and fly drones with a
few milliwatts [55,56]. But these movement policies are fixed and task-agnostic, and no model links a
sensor movement to the circuit that uses it. The hoverfly MIO is nature's answer to a question
engineers have not yet asked: should a pursuit system move its sensor differently from a stabilising
one?

**Gap 3. Comparing circuit models needs stimuli that tell them apart.** Standard gratings cannot
discriminate competing circuit hypotheses; stimuli optimised to maximise the disagreement between
models can [30]. We built a differentiable bank of Hassenstein–Reichardt and Barlow–Levick motion
detectors with ON and OFF pathways, motion opponency [26] and wide-field pooling, and we optimise
stimuli by gradient descent to separate models before an animal is used (preliminary result P4, B2).

**What machines need from this.** Most spiking vision networks are deep networks converted to spikes
[64]. They do not use the motifs that make fly vision fast, sparse and robust: linear electrical
coupling that pools and transmits signals without synaptic delay [14,92], push-pull opponent coding
[26], contrast normalisation that keeps velocity estimates stable in natural scenes [38,96], and
active sampling [7]. Whether such motifs transfer is an empirical question. It requires a model
grounded in a complete biological loop and a benchmark with matched baselines. HOVER provides both.

## 4. Objectives and hypotheses

**O1. Model.** Build a multi-tier, connectome-constrained spiking neural network (SNN) of the fly gaze
loop, from photoreceptors to retinal displacement, *including electrical synapses*, in the female
[12] and the male [39] *Drosophila* connectome.
→ **H1 (Sufficiency).** Chemical plus gap-junction connectivity from EM, with gap-junction weights set
by apposition area, predicts motor-neuron tuning (± 15°), eye-movement direction and latency; a
mathematically reduced SNN with ≥ 10× fewer state variables preserves these predictions. Corollary:
the *Drosophila* gaze circuit is monomorphic; the hoverfly's is not.

**O2. Test.** Map the model onto male and female *Eristalis* and test the dimorphic circuit.
→ **H2 (Dedicated channel).** In males the dimorphic HSN drives a dedicated motor neuron of the MIO,
forming a pursuit-specific active-vision channel; HSN and HSNE also feed the shared stabilisation
channel (MOT, MOS) in both sexes. → **H2b (Origin).** The MIO is specified by its motor neuron, as
the male-only Muscle of Lawrence of *Drosophila* forms only under *fruitless*-expressing motor
neurons [42,43,79].

**O3. Explain.** → **H3 (Task optimality).** When connectome-constrained SNNs are trained on the
male task (pursuit of small fast targets in clutter) or on the female task (hover stabilisation,
feeding approach) under identical wiring priors and energy budgets [80], the male features (narrowed
dorso-frontal integration, an extra effector) emerge only under the pursuit objective.

**O4. Transfer.** → **H4 (Transfer).** Event-based SNNs built from the extracted motifs, with
task-dependent micro-movements of the sensor, outperform parameter- and energy-matched deep-network
baselines on small-target detection in clutter and on ego-motion estimation, and achieve closed-loop
hovering and pursuit on an indoor quadrotor at a fraction of the energy.

*The computer-vision question behind H4.* Five predictions are specific enough to fail (H4a–f in
B2). (i) A sensor-movement policy tuned to the task improves small-target detection at the same event
rate: the male-type policy wins on pursuit, the stabilising policy on ego-motion, and a fixed rotation
[54] wins on neither. (ii) Feeding the motor command back into the motion units through the fly's
coupling motif, the efference copy of [14], removes self-generated events from the flow estimate
better than software compensation. (iii) Linear electrical pooling cuts the latency from first event
to motor command without loss of accuracy. (iv) Opponent push-pull coding with contrast normalisation
makes velocity estimates robust to contrast and clutter [38]. (v) Under one energy budget, two
task-specialised circuits with a shared front end, the dimorphic solution, beat one generalist.
Success is measured as accuracy per joule and as latency, against baselines matched in parameters
and synaptic operations, under protocols registered before the data exist.

**O5. Validate at scale and open everything.** Every model runs on low-cost spiking robots in IU
computer-vision courses and in a distributed public experiment; students and citizens produce
embodied robustness data, proofread electrical synapses and collect hoverfly pursuit statistics.

## 5. Approach

Five work packages are linked by one modelling ladder and one stimulus engine (Fig. A).

**WP1 Connectome → spiking circuit (M1–36).** (a) MESH is scaled from 26 neurons to all wide-field
motion neurons, retinal and neck motor neurons and optic-flow descending neurons, in the female and
the male connectome. A 3D convolutional classifier trained on the expert-validated sites ranks
candidates; community proofreading (WP5) confirms them. The male–female comparison in *Drosophila* is
the control for H1's corollary. (b) Three model tiers: **Tier 1**, morphologically reduced
biophysical neurons with electrical and chemical coupling, fitted by differentiable simulation [66];
**Tier 2**, integrate-and-fire point neurons with gap-junction coupling, derived from Tier 1 by
systematic reduction in which Kolmogorov–Arnold networks [93] learn the univariate transfer functions
between compartments and return closed-form expressions; **Tier 3**, trainable SNNs whose
connectivity is masked by the connectome, trained with surrogate gradients [64,65]. (c) A motor
readout maps muscle activation to retinal displacement through the measured pull directions [7,14].
Validation: retinal-motor-neuron imaging, eye tracking and the efference-copy recordings of [14].

**WP2 The dimorphic gaze circuit of *Eristalis* (M6–48).** No hoverfly connectome exists, so male and
female circuits are built by homology from the *Drosophila* model (HSN, HSE, HSS, VS cells, the
hoverfly-specific HSNE, and the motor neurons of MOT, MOS and MIO), constrained by our tomography
atlas [2], neurobiotin fills and published hoverfly physiology [1,15,23]. This gives **competing male
models** (H2 against shared drive, HSNE-driven MIO and VS-driven MIO). The stimulus engine generates
the stimuli on which these models disagree most. A HOVER postdoc in the Fenk laboratory (MPI for
Biological Intelligence), which holds the only established retinal-tracking and retinal-muscle
set-ups, presents them to tethered males and females while tracking the retina through the cornea
and recording the three muscles electromyographically. *High risk, high gain:* retinal tracking
during free-flight pursuit of artificial targets [21]. With R. Merrill (LMU), a HOVER PhD student
traces the developmental origin of the MIO (micro-CT and confocal time series of pupae) and its
genetic basis (sex- and stage-resolved transcriptomics, in situ hybridisation chain reaction, the
hoverfly genome [44]), testing H2b.

**WP3 Theory: why dimorphic? (M12–54).** In an embodied simulator with compound-eye optics and
retinal actuators, Tier-3 networks are optimised for pursuit and for stabilisation under the same
wiring prior and a spike-count energy penalty, both with the option of a third actuator [81,82]. We
test whether the male features emerge (H3) and extract the **minimal motif set** by ablation,
mean-field analysis of gap-junction-coupled populations and Kolmogorov–Arnold readouts that turn the
trained networks into equations.

**WP4 Active event-based machine vision (M13–60).** The motifs become event-driven SNNs on an event
camera mounted on a piezo micro-movement stage that replays fly retinal trajectories, with movement
policies that are fixed, fly-derived or learned. Networks are deployed on sensor-integrated and
large-scale neuromorphic hardware [67,68,70] through European access programmes. Three benchmarks
with pre-registered protocols: small-target detection and tracking in clutter against insect-inspired
[61] and deep [94] detectors; ego-motion estimation on public event-camera datasets [58,59] against
state-of-the-art artificial and spiking networks [55–57] and the fly-derived velocity-estimation CNN
[38]; and closed-loop hovering and target pursuit on an indoor event-camera quadrotor in a
motion-capture arena. Metrics: accuracy, latency, synaptic operations and measured energy. All
applications are civil, and all code, data and the benchmark leaderboard are open.

**WP5 Embodied validation at scale, teaching and open science (M1–60).** All Tier-2 and Tier-3
models compile to low-cost two-wheeled camera robots that run spiking neurons natively. (a) Each
semester, IU computer-vision students implement and test one HOVER motif; remote students receive a
kit by mail. (b) A distributed "robot zoo" experiment: schools, makerspaces and citizens run
fly-type, female-type and male-type circuits on standardised pursuit and stabilisation courses and
upload logs, yielding thousands of embodied trials under real-world optics and noise. (c) Community
proofreading of candidate gap junctions in the MESH viewer, following the EyeWire and FlyWire model
[12,85]. (d) "Hoverfly watch": smartphone slow-motion videos of male pursuits in gardens supply the
natural target statistics that define the WP3 tasks. WP5 builds on my open citizen-science framework
[36] and on a participatory project in which secondary-school pupils became first authors [88].

*Feasibility.* The pieces exist. MESH runs and has produced validated electrical synapses [14,41]. A
Hodgkin–Huxley model of the right-eye gaze circuit with electrical and chemical coupling already
reproduces motor-neuron spiking and the direction of optogenetically evoked eye movements. The
Tier-1 model, extended by the MIO, already returns a stimulus on which two hypotheses about the MIO's
pull direction predict retinal shifts 51° apart (B2, Fig. B1).
The tomography atlas of male and female hoverflies is in hand [2], hoverflies can be reared
year-round with a published protocol [19], and the hoverfly genome is public [44]. I have shipped TinyML pipelines
on classroom robots and teach computer vision to the cohorts that will run WP5. Hypothesis-critical
experiments are done by HOVER team members hosted at the partner sites, not by favours.

## 6. Why now, why me, why here

*Why now.* Whole-brain connectomes of both sexes, a validated pipeline for electrical synapses,
differentiable biophysics, mature surrogate-gradient training, affordable event cameras,
sensor-integrated neuromorphic chips and classroom spiking robots have all matured within the last
three years. Each piece exists; nobody has closed the loop.

*Why me.* My path runs through every level HOVER needs, and HOVER is the step that joins them. I spent
a decade recording from the fly motion-vision circuit, from the inputs of the elementary motion
detector [95] to opponency and real-world velocity coding [26,38,96]. I then moved from one circuit
to the whole wiring diagram, built MESH and performed the connectome analysis that revealed the
electrical gaze pathway [14,41], and helped trace the evolution of insect eye movements and discover
the MIO [2]. In parallel I became an applied computer-vision scientist: segmentation and object
recognition in terabyte electron-microscopy volumes, video-based event detection and TinyML
classifiers on edge hardware, and, since 2026, Professor of Computer Vision at IU. I study gaze in
humans too: my latest first-author work uses mobile eye-tracking and machine learning to read
intended behaviour from gaze [89]. And I have helped shape participatory research as a field: first
author of the Open Citizen Science framework [36], co-corresponding author of a plant
electrophysiology study led by school pupils [88], co-director of a research fellowship spanning more
than 20 countries, science-jury member of the German Federal Ministry of Research's IdeenLauf
initiative, and invited speaker at citizen-science conferences. HOVER is a new programme that I lead
with my own team. It is not a continuation of my postdoctoral projects, nor of the Fenk laboratory's
*Drosophila* programme on eye-movement mechanisms, with which it is complementary: HOVER asks *why* a
visual circuit differs between the sexes, in a different species, with models and machines as the
instruments.

*Why here.* IU is Germany's largest, largely distance-learning university. A computer-vision
professorship there makes WP4 and WP5 core activities, with students, courses and a route to
thousands of remote learners with kits at home. The partner laboratories supply what IU cannot: the
only hoverfly retinal-muscle physiology set-ups and genomics for a non-model insect.

## 7. Expected outcomes and impact

(1) The first connectome-constrained spiking model of a complete visuomotor loop, with electrical
synapses, from photon to eye movement, in both sexes of *Drosophila*. (2) A mechanistic and normative
explanation of a visual sexual dimorphism, including the origin of the only known sexually dimorphic
eye muscle. (3) A tested, open catalogue of fly-derived motifs for active event-based vision, with a
benchmark that lets the field measure "bio-inspired" claims. (4) A participatory infrastructure that
turns connectomics and spiking models into something students and citizens can build, test and
contribute to. Beyond flies, HOVER establishes a template for asking *why* a circuit is wired as it
is: pit models of different task hypotheses against each other, in animals and in machines.

*Ambition and risk.* HOVER is high-gain because it joins three things that have not been joined
before: a complete connectome-constrained motor loop with electrical synapses, a sexual dimorphism as
a normative test, and a machine-vision benchmark as the final arbiter. The riskiest elements,
free-flight retinal tracking and the transfer hypothesis H4, are isolated so that their failure does
not stop the rest, and a rigorous negative result on H4 would itself be a valuable, open contribution
to a field full of untested bio-inspired claims.

**Figure A (proposal/figures/fig_A_overview.png).** *HOVER closes a loop from synapse to society.* Left: the natural experiment, male and female *Eristalis* with the male bright zone, the narrowed HSN receptive field and the male-only third retinal muscle (MIO). Centre: the modelling ladder from the female and male *Drosophila* connectomes and MESH-detected electrical synapses through biophysical (Tier 1), reduced (Tier 2) and trainable (Tier 3) spiking models, with the controversial-stimulus engine. Right: the model is tested in the animal (WP2, H2), explained by task optimisation (WP3, H3) and transferred to active event-based vision on neuromorphic hardware and a quadrotor (WP4, H4). Bottom: students and citizens validate the models on spiking robots, proofread electrical synapses and collect pursuit statistics, which feed back into WP1 and WP3 (WP5).

## References (abbreviated; full list in `references.md`)

[1] Nordström *et al.* 2008 Curr Biol · [2] **Kviatko, …, Serbe-Kamp, …, Fenk** 2026 (manuscript) [verify status] · [7] Fenk *et al.* 2022 Nature · [12] Dorkenwald *et al.* 2024 Nature · [14] **Falt, Ammer, Serbe-Kamp *et al.*** 2026 bioRxiv · [15] Straw *et al.* 2006 J Exp Biol · [16] Nordström *et al.* 2006 PLoS Biol · [21] Thyselius *et al.* 2023 J Exp Biol · [23] Nicholas *et al.* 2026 eLife · [26] **Ammer, Serbe-Kamp *et al.*** 2023 Nat Neurosci · [30] Golan *et al.* 2020 PNAS · [36] **Serbe-Kamp *et al.*** 2023 RIO · [38] **Drews *et al.*** 2020 Curr Biol · [39] Berg *et al.* 2026 Cell · [41] **Serbe-Kamp** 2026 MESH software · [42] Lawrence & Johnston 1986 Cell · [43] Usui-Aoki *et al.* 2000 Nat Cell Biol · [44] *Eristalis tenax* genome, Darwin Tree of Life · [45] Lappalainen *et al.* 2024 Nature · [46] Shiu *et al.* 2024 Nature · [47] Schlegel *et al.* 2024 Nature · [48] Matsliah *et al.* 2024 Nature · [49] Bates *et al.* 2026 Nature · [50] Ammer *et al.* 2022 Curr Biol · [51] Juusola *et al.* 2017 eLife · [52] Kemppainen *et al.* 2022 PNAS · [53] Gallego *et al.* 2022 IEEE TPAMI · [54] He *et al.* 2024 Sci Robot · [55] Paredes-Vallés *et al.* 2024 Sci Robot · [56] Hagenaars *et al.* 2021 NeurIPS · [57] Gehrig *et al.* 2021 3DV · [58] Gehrig *et al.* 2021 IEEE RA-L · [59] Zhu *et al.* 2018 IEEE RA-L · [61] Wiederman *et al.* 2008 PLoS ONE · [62] Nordström & O'Carroll 2009 Trends Neurosci · [64] Neftci *et al.* 2019 IEEE SPM · [65] Zenke & Ganguli 2018 Neural Comput · [66] Deistler *et al.* 2025 Nat Methods · [67] Davies *et al.* 2021 Proc IEEE · [68] Mayr *et al.* 2019 arXiv · [70] Yao *et al.* 2024 Nat Commun · [71] Collett & Land 1975 · [72] Collett & Land 1978 · [74] Hausen & Strausfeld 1980 · [75] Gilbert & Strausfeld 1991 · [76] Hornstein *et al.* 2000 · [77] Ribeiro *et al.* 2018 Cell · [78] Hindmarsh Sten *et al.* 2021 Nature · [79] Gailey *et al.* 1991 Development · [80] Niven & Laughlin 2008 J Exp Biol · [81] Yamins & DiCarlo 2016 · [82] Lindsey *et al.* 2019 ICLR · [85] Kim *et al.* 2014 Nature · [88] **Madariaga, …, Serbe-Kamp, Marzullo** 2024 Plant Signal Behav · [89] **Serbe-Kamp *et al.*** 2026 PsyArXiv · [92] Hürkey *et al.* 2023 Nature · [93] Liu *et al.* 2024 (KAN) · [94] Gehrig & Scaramuzza 2023 CVPR · [95] **Serbe *et al.*** 2016 Neuron · [96] **Leonhardt, …, Serbe, …** 2016 Nat Neurosci · [108] Gehrig & Scaramuzza 2024 Nature
