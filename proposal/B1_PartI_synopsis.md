<!-- ERC-2027-CoG Part B1: Part I of the Scientific Proposal | max 5 pages, excluding cover page and references
Must contain: (1) current state of knowledge, (2) scientific question and objectives, (3) overall approach (IfA p. 28).
Read at Step 1 by panel members acting as GENERALISTS: keep jargon low. Header on every page: Serbe-Kamp | HOVER | Part B1
Figures: Fig. 1 (concept, proposal/figures/fig_1_concept.svg, 170 x 86 mm) and Fig. 2 (results, fig_2_results.svg, 170 x 68 mm).
Every number in section 4 comes from code/hover (bowl_result.json, eventcam_result.json, docs/model_design.md).
[verify] = check against the source before submission -->

# HOVER: Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits

**PI:** Étienne Serbe-Kamp · **Host:** IU Internationale Hochschule (Germany) · **Partners:** MPI for Biological Intelligence, LMU Munich · **Duration:** 60 months · **Panel:** LS5 (secondary PE6)

## 1. The question

Seeing is active. Animals move their eyes to stabilise the image, to follow a target and to refresh
what they see, and how they move them depends on the task. Machine vision is rediscovering this
[112]: event cameras, the neuromorphic sensors that report only changes of brightness, are blind to
a static scene unless the sensor moves [53,54]. How should a sensor move for a given task, and which
circuit should read it? Flies answer both questions with about 10⁵ neurons and a few milliwatts, and
evolution has left a clean experiment. Male and female hoverflies share a genome and a brain plan,
but only males chase mates in high-speed aerial pursuits, and only males, as we discovered, carry
**a third muscle that moves the retina** (Fig. 1). Nobody knows what it is for.

<div class="key">

**HOVER will find out what the third eye muscle is for, explain why the male's task demands it, and
test whether the answer is a design principle for machine vision.**

</div>

It works in a loop (Fig. 1). A spiking model of the complete fly gaze circuit, built from the
connectome, predicts the stimuli that single out the muscle (WP1). Hoverflies see these stimuli
while their own eye movements steer the search for better ones (WP2). The model is trained for the
male or the female task, to see whether the muscle emerges (WP3). The resulting principles drive
event cameras that move their sensor (WP4), and students and citizens test every model on low-cost
robots (WP5).

**Figure 1 (proposal/figures/fig_1_concept.svg).** *HOVER in six steps.* (1) Micro-CT of a male hoverfly head, retinal muscles in red; the third muscle, between the two eyes, exists only in males [2]. (2) The gaze circuit as a spiking model built from the connectome, with electrical synapses (zigzags); what drives the third muscle is unknown. (3) Two stimuli on one display, then a stimulus search steered by the tracked retinae. (4) One network trained for the female or the male task. (5) Event cameras that move their sensor, on neuromorphic chips and a quadrotor. (6) Every model runs on low-cost spiking robots.

## 2. A natural experiment: one genome, two visual machines

Male hoverflies (*Eristalis tenax*) hover on station and dart after passing conspecifics on
interception courses [71,72]; females hover, feed and lay eggs. The male visual system is
specialised at every level. A dorso-frontal "bright zone" of enlarged facets gathers more light and
gives faster, more contrast-sensitive motion detection [15]. It is the hoverfly version of the "love
spot" of houseflies and blowflies, where photoreceptor speed is matched to chasing [76] and
male-specific neurons exist [74,75]. Hoverflies have four horizontal-system cells, wide-field motion
neurons that stabilise gaze in other flies. In males one of them, HSN, has its receptive field
narrowed to the bright zone and responds to small moving targets [1]. Descending neurons differ
between the sexes at high velocities [23], and hoverfly small-target detectors [16,62] and the male
pursuit itself [21] have been measured in the laboratory.

Our own recent work adds the missing level: the effector. Flies move their retinae beneath the
stationary lenses with small muscles, which produces an optokinetic reflex and spontaneous,
saccade-like shifts [7]. In a comparative survey of 167 insect species by micro-CT and synchrotron
tomography, with behaviour in 59 of them, we found retinal movements only in Diptera, reconstructed
their stepwise evolution and discovered in hoverflies **a male-only third retinal muscle, the
M. interocularis (MIO)**, lodged between the two nearly fused male eyes, next to the bright zones
[2]. The male hoverfly therefore has not only a different sensor and a different circuit but a
different *active-vision effector*. This is a natural knockout experiment with its rationale built
in: the female shows the gaze system without the muscle, the male with it, and the male's extra task
is known. HOVER uses it three times: as a test of mechanism (what drives the muscle, and what does it
do?), as a test of optimality (does the muscle emerge in a model trained for pursuit?) and as a
source of design principles for machines.

## 3. State of the art and three gaps

**Gap 1. Connectomes have outpaced models, and both miss electrical synapses.** Synapse-level wiring
diagrams now exist for the female *Drosophila* brain [12,47,48], for brain and nerve cord [49] and,
since September 2026, for the complete male central nervous system [39]. The models built on them
predict neural activity [45] and sensorimotor processing [46], but they (i) use chemical synapses
only, because gap junctions are invisible in these electron-microscopy volumes [50], (ii) stop
before the motor output and (iii) describe one sex of one species in a passive setting. We have
shown why this matters for gaze: the motor neurons that move the *Drosophila* retina receive only
3 % of their chemical synapses from visual neurons, yet they are electrically coupled to the HS and
VS cells, and this wiring alone predicts their direction tuning, the two-dimensional optokinetic
reflex (R² = 0.99) and an efference copy that flows back into the visual neurons during spontaneous
eye movements [14]. To find electrical synapses at connectome scale I built **MESH**, an open
pipeline that detects membrane appositions between neuron meshes, validates them in the
electron-microscopy volume and serves them for proofreading [41]: 49 validated contact sites out of
619 candidates for the 26 neurons of the gaze circuit.

**Gap 2. Active vision is missing from circuit models and from event-based machine vision.** Retinal
micro-movements refresh the image, defeat photoreceptor adaptation and sharpen acuity [7,51,52].
Event cameras have the mirror-image problem: they go blind on static scenes [53], although they now
reach automotive products [108]. Engineers have begun to add artificial microsaccades with a rotating
prism [54], and spiking networks on neuromorphic chips estimate optic flow and fly drones with a few
milliwatts [55,56]. But these movement policies are fixed and task-agnostic, and no model links a
sensor movement to the circuit that reads it. Our simulations show why this matters (Fig. 2c): the
movement that lets an event camera register a static scene hides a small moving target. The
hoverfly, which stabilises with two muscles and pursues with three, is nature's worked example of a
question engineers have only begun to ask: should a pursuit system move its sensor differently from
a stabilising one?

**Gap 3. Finding out what a circuit element is for needs stimuli chosen by models, and by the
animal.** Standard gratings rarely discriminate competing circuit hypotheses; stimuli optimised so
that models disagree can [30], and closed-loop methods that let neural responses choose the next
image have found what visual neurons respond to best [110,111]. No such method exists for an eye
movement. We have built its two parts: a model from photoreceptor to eye muscle that designs the
stimuli before an animal is used, and a search in which the tracked retinal movement chooses the
next stimulus (section 4).

**What machines need from this.** Most spiking vision networks are deep networks converted to spikes
[64]. They lack the motifs that make fly vision fast, sparse and robust: sensor movements matched to
the task [7], an efference copy that tells self-generated from external motion [14], electrical
coupling that pools signals without synaptic delay [14,92], push-pull opponent coding [26] and
contrast normalisation [38,96]. Whether these transfer can only be decided with a model of a
complete biological loop and a benchmark with matched baselines. HOVER provides both.

## 4. Preliminary results: what the project is about, in three panels

**A model from photoreceptor to eye muscle.** We have built the model that WP1–WP3 refine:
compound-eye sampling [109], motion detectors with opponency [26], electrically coupled wide-field
cells and spiking motor neurons from MESH, and the muscle model of [14]. Fitted to *Drosophila* with
two parameters, it reproduces the preferred directions of both retinal motor neurons (212° and 146°;
measured 212° and 141°) and the direction of the optokinetic reflex (mean error 17°).

**Two stimuli single out the third muscle (Fig. 2a,b).** In the hoverfly version, with both eyes, the
narrowed HSN drives the third muscle. The model then designs two stimuli for one display. A
square-wave grating that spares the love spot moves the retinae of both sexes alike (within 5 %),
although their HSN cells differ: it calibrates each animal and tests the shared part of the circuit.
The same grating shown only in the love spot moves the male retina 2.9 times as far as the female's,
and 88 % of that difference disappears when the muscle is cut in the model. A small patch shown
anywhere else leaves the sexes alike (Fig. 2b). If the muscle were driven by the vertical cells
instead, as an amplifier of the stabilising reflex, the pattern would reverse (matched stimulus:
male 1.9 times the female; love spot: 1.3); without visual drive, neither stimulus would separate
the sexes. Two stimuli thus decide between three ideas of what the muscle is for. **The animal can
then correct the model:** in simulation, a search that reads only the noisy retinal movement
improved the model's stimulus by 18–33 % within about 100 presentations, five minutes of
experiment, for an "animal" whose love spot lies 20° higher than the model assumes.

**Machines face the same conflict (Fig. 2c).** In 150 simulated scenes, an event sensor registered a
static scene in 0 % of cases without movement, in 89 % with a movement of half a pixel and in at
least 98 % with two to six pixels. The same movement hid a small moving target: detection fell from
97 % at half a pixel to 44 % at one pixel and 7 % at two, and for a low-contrast target to 23 %
already at half a pixel. No fixed movement serves both tasks. Either the movement follows the task,
or self-generated events are told apart from the target's, which is what the efference copy does in
the fly [14].

**Figure 2 (proposal/figures/fig_2_results.svg).** *Preliminary results.* (a) Two stimuli designed with the model for one bowl-shaped display (dashed circle: love spot; arrow: drift) and the predicted retinal movement of females, males and males whose third muscle is cut in the model. (b) Difference between the sexes for a small grating patch at each position of the display. (c) Event-camera simulation: share of 150 scenes in which a static scene is registered to a quarter of a pixel (orange) and a small moving target is found (blue), against the size of the sensor movement.

## 5. Objectives and hypotheses

**O1. Model.** Build a multi-tier, connectome-constrained spiking neural network (SNN) of the fly gaze
loop, from photoreceptors to retinal displacement, *including electrical synapses*, in the female
[12] and the male [39] *Drosophila* connectome.
→ **H1 (Sufficiency).** Chemical plus gap-junction connectivity from EM, with gap-junction weights set
by apposition area, predicts motor-neuron tuning (± 15°), eye-movement direction and latency; a
reduced SNN with ≥ 10× fewer state variables preserves these predictions.

**O2. Test.** Find out what the third muscle is for, in male and female *Eristalis*.
→ **H2 (A separate channel for the bright zone).** The third muscle is driven by motion inside the
love spot, through the narrowed HSN, and moves the male retina in addition to, and independently of,
the stabilising reflex that both sexes share. The experiments decide between this and two
alternatives: an amplifier of the stabilising reflex, driven by wide-field motion, and a muscle
without visual drive that moves the retina spontaneously. → **H2b (Origin).** The muscle is specified
by its motor neuron, as the male-only Muscle of Lawrence of *Drosophila* forms only under
*fruitless*-expressing motor neurons [42,43,79].

**O3. Explain.** → **H3 (Task optimality).** When connectome-constrained SNNs are trained on the
male task (pursuit of small fast targets in clutter) or on the female task (hover stabilisation,
feeding approach) under identical wiring priors and energy budgets [80], the male features (narrowed
dorso-frontal integration, a third effector) emerge only under the pursuit objective, and the
network uses the third effector as the male uses the muscle.

**O4. Transfer.** → **H4 (Transfer).** Event-based SNNs built from the extracted motifs, with
task-dependent micro-movements of the sensor, outperform parameter- and energy-matched deep-network
baselines on small-target detection in clutter and on ego-motion estimation, and achieve closed-loop
hovering and pursuit on an indoor quadrotor at a fraction of the energy.

*The computer-vision question behind H4.* Six predictions are specific enough to fail (H4a–g in
B2). (i) A sensor-movement policy tuned to the task beats a fixed one: the pursuit policy wins on
small targets, the stabilising policy on ego-motion, and a fixed rotation [54] wins on neither.
(ii) Feeding the motor command back into the motion units, the efference copy of [14], removes
self-generated events better than software compensation. (iii) Linear electrical pooling cuts the
latency from first event to motor command without loss of accuracy. (iv) Opponent coding with
contrast normalisation makes velocity estimates robust to contrast and clutter [38]. (v) Under one
energy budget, two task-specialised circuits with a shared front end beat one generalist. (vi) A
sensor with a specialised zone gains from a second, independent movement of that zone: the machine
version of the third muscle. Success is measured as accuracy per joule and as latency, against
baselines matched in parameters and synaptic operations, under pre-registered protocols.

**O5. Validate at scale and open everything.** Every model runs on low-cost spiking robots in IU
computer-vision courses and in a public experiment; students and citizens produce robustness data,
proofread electrical synapses and collect hoverfly pursuit statistics.

## 6. Approach

**WP1 Connectome → spiking circuit (M1–36).** (a) MESH is scaled from 26 neurons to all wide-field
motion neurons, retinal and neck motor neurons and optic-flow descending neurons, in the female and
the male connectome; a 3D convolutional classifier trained on the validated sites ranks candidates,
and community proofreading (WP5) confirms them. (b) Three model tiers: **Tier 1**, morphologically
reduced biophysical neurons with electrical and chemical coupling, fitted by differentiable
simulation [66]; **Tier 2**, integrate-and-fire neurons with gap-junction coupling, derived from
Tier 1 by a reduction in which Kolmogorov–Arnold networks [93] return closed-form transfer
functions; **Tier 3**, trainable SNNs masked by the connectome, trained with surrogate gradients
[64,65]. (c) A motor readout maps muscle activation to retinal displacement [7,14]. Validation:
motor-neuron imaging, eye tracking and the efference-copy recordings of [14].

**WP2 What is the third muscle for? (M6–48).** No hoverfly connectome exists, so male and female
circuits are built by homology from the *Drosophila* model (the four HS cells, the VS cells and the
motor neurons of the three muscles), constrained by our tomography atlas [2], dye fills and published
hoverfly physiology [1,15,23]. This gives a family of male models that differ in what drives the
third muscle and where it pulls. The experiments use one bowl-shaped projector display [22] and track
the retinae of both eyes through the cornea, in three steps: (a) the matched and the love-spot
stimulus in males and females; (b) a closed-loop search in which the measured retinal movement
chooses the next stimulus, started from the model's proposal, so that the animal can correct the
model; (c) electromyography of the three muscles, recordings and dye fills of the candidate cells,
and section of the muscle as the causal test. A HOVER postdoc does this work in the Fenk laboratory
(MPI for Biological Intelligence), which holds the only established retinal-tracking and
retinal-muscle set-ups. *High risk, high gain:* retinal tracking during free-flight pursuit [21].
With R. Merrill (LMU), a HOVER PhD student traces the developmental origin of the muscle in pupae
and its genetic basis (sex- and stage-resolved transcriptomics, the hoverfly genome [44]): H2b.

**WP3 Theory: why a third muscle? (M12–54).** In an embodied simulator with compound-eye optics and
retinal actuators, Tier-3 networks are optimised for pursuit and for stabilisation under the same
wiring prior and a spike-count energy penalty, both with the option of a third actuator [81,82]. We
test whether the male features emerge and how the third actuator is used (H3), and extract the
**minimal motif set** by ablation, mean-field analysis and Kolmogorov–Arnold readouts that turn the
trained networks into equations.

**WP4 Active event-based machine vision (M13–60).** The motifs become event-driven SNNs on an active
camera head: a wide-angle and a telephoto event camera, the machine counterparts of eye and bright
zone, each on a piezo stage that moves its sensor by fractions of a pixel. Movement policies are
fixed, fly-derived or learned, and an efference copy of each movement is fed to the network.
Networks run on sensor-integrated and large-scale neuromorphic hardware [67,68,70]. Three
pre-registered benchmarks: small-target detection and tracking in clutter against insect-inspired
[61] and deep [94] detectors; ego-motion estimation on public event-camera datasets [58,59] against
state-of-the-art artificial and spiking networks [55–57] and the fly-derived velocity CNN [38]; and
closed-loop hovering and target pursuit on an indoor event-camera quadrotor. Metrics: accuracy,
latency, synaptic operations and measured energy. All applications are civil; code, data and the
benchmark leaderboard are open.

**WP5 Embodied validation at scale, teaching and open science (M1–60).** All Tier-2 and Tier-3
models compile to low-cost two-wheeled camera robots that run spiking neurons natively. (a) Each
semester, IU computer-vision students implement and test one HOVER motif; remote students receive a
kit by mail. (b) A "robot zoo": schools, makerspaces and citizens run fly-type, female-type and
male-type circuits on standard pursuit and stabilisation courses and upload logs: thousands of
embodied trials under real-world optics and noise. (c) Community proofreading of candidate gap
junctions in the MESH viewer [12,85]. (d) "Hoverfly watch": smartphone slow-motion videos of male
pursuits supply the target statistics that define the WP3 tasks.

*Feasibility.* The pieces exist (section 4): MESH and its validated electrical synapses [14,41], a
model from photoreceptor to eye muscle that already designs the WP2 stimuli, the closed-loop search
and the event-camera simulation. The tomography atlas is in hand [2], hoverflies are reared
year-round [19] and their genome is public [44]. I have shipped TinyML pipelines on classroom robots
and teach computer vision to the cohorts that will run WP5. Hypothesis-critical experiments are done
by HOVER team members hosted at the partner sites.

## 7. Why now, why me, why here

*Why now.* Whole-brain connectomes of both sexes, a validated pipeline for electrical synapses,
differentiable biophysics, surrogate-gradient training, affordable event cameras, neuromorphic chips
and classroom spiking robots have all matured within three years. Nobody has closed the loop.

*Why me.* My path runs through every level HOVER needs. I spent a decade recording from the fly
motion-vision circuit, from the inputs of the elementary motion detector [95] to opponency and
real-world velocity coding [26,38,96]. I then moved from one circuit to the whole wiring diagram,
built MESH, performed the connectome analysis that revealed the electrical gaze pathway [14,41], and
helped trace the evolution of insect eye movements and discover the third muscle [2]. In parallel I
became a computer-vision scientist: segmentation and object recognition in terabyte
electron-microscopy volumes, video-based event detection and TinyML classifiers on edge hardware,
mobile eye-tracking with machine learning to read intended behaviour from human gaze [89] and, since
2026, Professor of Computer Vision at IU. I have also helped shape participatory research: first
author of the Open Citizen Science framework [36], co-corresponding author of a plant
electrophysiology study led by school pupils [88] and co-director of a research fellowship spanning
more than 20 countries. HOVER is a new programme that I lead with my own team. It is not a
continuation of my postdoctoral projects, nor of the Fenk laboratory's *Drosophila* programme on the
mechanisms of eye movements, with which it is complementary: HOVER asks what a sex-specific eye
muscle is for and what machines can learn from it, in a different species, with models and machines
as the instruments.

*Why here.* IU is Germany's largest, largely distance-learning university. A computer-vision
professorship there makes WP4 and WP5 core activities, with courses and a route to thousands of
remote learners with kits at home. The partner laboratories supply what IU cannot: the only hoverfly
retinal-muscle physiology set-ups and genomics for a non-model insect.

## 8. Expected outcomes and impact

(1) The first connectome-constrained spiking model of a complete visuomotor loop, with electrical
synapses, from photon to eye movement, in both sexes of *Drosophila*. (2) The function, the neural
drive and the developmental origin of the only known sexually dimorphic eye muscle, and with them a
mechanistic and normative explanation of a visual sexual dimorphism. (3) A tested, open catalogue of
fly-derived principles for active event-based vision, with a benchmark that lets the field measure
"bio-inspired" claims. (4) An infrastructure through which students and citizens build and test
spiking models. Beyond flies, HOVER is a template for asking what a circuit element is *for*: let
models propose the decisive stimuli, let the animal correct them, and let a machine show whether the
answer is useful.

*Ambition and risk.* HOVER joins three things that have not been joined before: a complete
connectome-constrained motor loop with electrical synapses, a sex-specific effector as a natural
experiment, and a machine-vision benchmark as the final arbiter. The riskiest elements, free-flight
retinal tracking and the transfer hypothesis H4, are isolated so that their failure does not stop
the rest; a rigorous negative result on H4 would still be a valuable, open contribution.

## References (abbreviated; full list in `references.md`)

[1] Nordström *et al.* 2008 Curr Biol · [2] **Kviatko, …, Serbe-Kamp, …, Fenk** 2026 (manuscript) [verify status] · [7] Fenk *et al.* 2022 Nature · [12] Dorkenwald *et al.* 2024 Nature · [14] **Falt, Ammer, Serbe-Kamp *et al.*** 2026 bioRxiv · [15] Straw *et al.* 2006 J Exp Biol · [16] Nordström *et al.* 2006 PLoS Biol · [19] Nicholas *et al.* 2018 J Vis Exp · [21] Thyselius *et al.* 2023 J Exp Biol · [22] Prech *et al.* 2024 PLoS ONE · [23] Nicholas *et al.* 2026 eLife · [26] **Ammer, Serbe-Kamp *et al.*** 2023 Nat Neurosci · [30] Golan *et al.* 2020 PNAS · [36] **Serbe-Kamp *et al.*** 2023 RIO · [38] **Drews *et al.*** 2020 Curr Biol · [39] Berg *et al.* 2026 Cell · [41] **Serbe-Kamp** 2026 MESH software · [42] Lawrence & Johnston 1986 Cell · [43] Usui-Aoki *et al.* 2000 Nat Cell Biol · [44] *Eristalis tenax* genome, Darwin Tree of Life · [45] Lappalainen *et al.* 2024 Nature · [46] Shiu *et al.* 2024 Nature · [47] Schlegel *et al.* 2024 Nature · [48] Matsliah *et al.* 2024 Nature · [49] Bates *et al.* 2026 Nature · [50] Ammer *et al.* 2022 Curr Biol · [51] Juusola *et al.* 2017 eLife · [52] Kemppainen *et al.* 2022 PNAS · [53] Gallego *et al.* 2022 IEEE TPAMI · [54] He *et al.* 2024 Sci Robot · [55] Paredes-Vallés *et al.* 2024 Sci Robot · [56] Hagenaars *et al.* 2021 NeurIPS · [57] Gehrig *et al.* 2021 3DV · [58] Gehrig *et al.* 2021 IEEE RA-L · [59] Zhu *et al.* 2018 IEEE RA-L · [61] Wiederman *et al.* 2008 PLoS ONE · [62] Nordström & O'Carroll 2009 Trends Neurosci · [64] Neftci *et al.* 2019 IEEE SPM · [65] Zenke & Ganguli 2018 Neural Comput · [66] Deistler *et al.* 2025 Nat Methods · [67] Davies *et al.* 2021 Proc IEEE · [68] Mayr *et al.* 2019 arXiv · [70] Yao *et al.* 2024 Nat Commun · [71] Collett & Land 1975 · [72] Collett & Land 1978 · [74] Hausen & Strausfeld 1980 · [75] Gilbert & Strausfeld 1991 · [76] Hornstein *et al.* 2000 · [79] Gailey *et al.* 1991 Development · [80] Niven & Laughlin 2008 J Exp Biol · [81] Yamins & DiCarlo 2016 · [82] Lindsey *et al.* 2019 ICLR · [85] Kim *et al.* 2014 Nature · [88] **Madariaga, …, Serbe-Kamp, Marzullo** 2024 Plant Signal Behav · [89] **Serbe-Kamp *et al.*** 2026 PsyArXiv · [92] Hürkey *et al.* 2023 Nature · [93] Liu *et al.* 2024 (KAN) · [94] Gehrig & Scaramuzza 2023 CVPR · [95] **Serbe *et al.*** 2016 Neuron · [96] **Leonhardt, …, Serbe, …** 2016 Nat Neurosci · [108] Gehrig & Scaramuzza 2024 Nature · [109] Zhao *et al.* 2025 Nature · [110] Ponce *et al.* 2019 Cell · [111] Walker *et al.* 2019 Nat Neurosci · [112] Aloimonos *et al.* 1988 Int J Comput Vis
