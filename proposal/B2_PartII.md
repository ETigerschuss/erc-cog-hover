<!-- ERC-2027-CoG Part B2: Part II of the Scientific Proposal | max 7 pages, references excluded (IfA p. 28)
Content: detailed implementation — methodology, work plan, risk assessment and mitigation, further background not in Part I.
Must NOT repeat Part I; must be consistent with the Part A Resources section (budget table prevails).
Step 2 questions answered here: methodology and working arrangements appropriate? timescales and resources adequate and justified?
Header on every page: Serbe-Kamp | HOVER | Part B2
Figures: B1 preliminary results (≈ ⅓ page, from your DFG material), B2 work-plan dependencies and B3 Gantt (proposal/figures/, ≈ ⅓ page together). -->

# HOVER: Part II of the Scientific Proposal

## 1. Preliminary results and further background

**Figure B1 (proposal/figures/fig_B1_preliminary.png).** *Preliminary results.* (a) MESH: neuron meshes of the right-eye gaze circuit with contact sites, and the EM cut-out of a validated membrane apposition between the MOS motor neuron and VS2 (FlyWire, 8 nm). (b) The electrical wiring motif: VS1–4 couple to the MOS motor neuron, HS cells to both motor neurons [14]. (c) Measured against predicted preferred directions of the two retinal motor neurons; the prediction uses gap-junction connectivity alone [14]. (d) The Tier-1 model inside MESH: membrane potentials of the right-eye LPTCs and of both motor neurons, decoded eye displacement and its direction during a 500 ms drive of the motor neurons. (e) Micro-CT of a male *Eristalis* head with the three retinal muscles in red [2]. (f) The MIO (red) of a male *Melanostoma*, between the eyes [2]. (g) Controversial stimulus computed with the Tier-1 model extended by HSNE and an HSN-driven MIO motor neuron: a full-contrast grating confined to the male HSN field, moving front-to-back and slightly upward, on a faint counter-moving background (left; contours: receptive fields of the male and female HSN, HSNE and HSE) drives the three motor neurons (middle; LPTC membrane potentials and motor-neuron rates of the biophysical network) and yields predicted retinal-shift directions of 175° if the MIO pulls anteriorly and 124° if it pulls dorsally (0° posterior, 90° dorsal), against 169° for the female circuit (right).

**P1 MESH: electrical synapses at connectome scale.** MESH retrieves the surface meshes of selected
FlyWire neurons, builds a k-d tree over mesh vertices and finds every location where two membranes
lie within 100 nm. Contacts are grouped into sites by hierarchical clustering, validated in the
8-nm EM volume (only genuine membrane appositions without an annotated chemical specialisation are
kept) and served to experts in a viewer. For the 26-neuron set of HS, VS and retinal motor neurons
(RMNs) in both hemispheres it found 619 sites, of which 49 motor-neuron–LPTC sites survived
validation (2,895 EM images, public viewer), including the best-characterised candidate, between the
MOT motor neuron and HSN [14,41].

**P2 The electrical gaze pathway.** Each retinal muscle is innervated by one motor neuron (MOS RMN:
FlyWire type CB0901; MOT RMN: CB0804). The two muscles pull orthogonally (51° and 320°). Only 3 % of
the RMNs' chemical input comes from visual neurons, but neurobiotin fills and MESH agree that the MOS
RMN is coupled to the three HS cells and VS1–4, and the MOT RMN to the HS cells only. A linear sum
over the coupled cells predicts each RMN's preferred direction within 8°, and the vector sum of
muscle pulls weighted by RMN activity predicts the two-dimensional optokinetic reflex (R² = 0.994).
Mutants lacking the neuronal gap-junction protein shakB show a reduced reflex, and spontaneous
retinal movements are preceded by motor-related potentials in HS cells that mirror the visual
consequence of the movement (R² = 0.97, slope −1) [14]. The pathway from photoreceptor to retinal
movement is therefore complete at the level of identified cells, which is the precondition for O1.

**P3 Tier-1 model.** A Hodgkin–Huxley model of the right-eye circuit, with electrical and chemical
coupling, runs inside MESH. It reproduces sustained RMN spiking and the eye-displacement direction
observed after optogenetic activation of the MOT and MOS motor neurons (unpublished).

**P4 A validated ground-truth model, and controversial stimuli from it (Fig. B1g).** We have built the model that WP1–WP3 refine (`code/hover`): an eye map on the sphere with the local lattice axes of [109], the T4/T5 detectors and multilevel-opponency circuits of [26] feeding the LPTC receptive fields, the MESH Tier-1 electrical network with HH retinal motor neurons, and the vector-sum oculomotor model of [14]. Fitted to *Drosophila* with one frame rotation and one wiring ratio, it reproduces the measured MOS (212° vs 212°) and MOT (146° vs 141°) preferred directions, the HS→MOT and VS+HS→MOS relations and the direction of the optokinetic reflex (mean error 17°; [14]: 7°), and it predicts VS1–4→MOS junctions twice as strong as HS→MOS, a number T1.1 reads off FAFB. Extended by HSNE, the male HSN field [1] and an HSN-coupled MIO motor neuron, the same model is searched, by an evolution strategy verified with the biophysical network and by pixel-level gradient descent through the differentiable front end (ALIstim), for the stimulus on which two MIO pull directions, anterior or dorsal, predict the most different retinal shifts. The answer is a grating confined to the male HSN field on a faint counter-moving background: it drives the MIO about twice as much as MOT and MOS, the two hypotheses predict shift directions 51° apart (117° for the pixel-optimised stimulus), and the female circuit predicts a third one (Fig. B1g). The same machinery will rank every WP2 experiment before an animal is used.

**P5 Comparative anatomy.** Micro-CT and synchrotron tomography of 167 insect species, behaviour in
59, show specific retinal muscles only in Diptera. Hoverflies are among the earliest-branching flies with a
specific retinal muscle (MOT) and an optokinetic reflex, and males carry the additional M. interocularis (MIO) between the
two eyes, placed to shift the bright-zone retina [2]. A thinner circumocular ridge is associated with
retinal movements across the phylogeny, and both known muscles probably derive from antennal
musculature: the first clues to where the MIO comes from.

**P6 Edge AI, teaching and participation.** TinyML classifiers for real-time event detection on
Arduino-class hardware (Computational SpikerBox, SpikerBot; NIH SBIR), a participatory
plant-electrophysiology study with pupils as first authors [88], a research fellowship co-directed in
more than 20 countries, and IU computer-vision courses from [semester; fill] with [n] students.

## 2. Methodology and work plan

**Figure B2 (proposal/figures/fig_B2_workplan.png).** Work packages, tasks, deliverables (D), milestones (MS) and the main dependencies. Solid arrows: models and motifs flow from WP1 through WP3 to WP4 and onto robots; dashed arrows: data, labels and task statistics flow back from WP2 and WP5.

Five work packages share one modelling ladder and one stimulus engine (Fig. B2). "→ H" marks the
hypothesis a task tests; D = deliverable; M = project month. Team: PI; Postdoc 1 (PD1, IU,
computational neuroscience); PhD 1 (IU, connectomics and machine learning); PhD 2 (IU, event-based
spiking vision); research engineer (RE, IU, neuromorphic robotics, part-time); Postdoc 2 (PD2,
MPI for Biological Intelligence, hoverfly physiology); PhD 3 (LMU, evolutionary developmental
genetics); student assistants (SA).

### WP1 Connectome → spiking circuit, with electrical synapses (M1–36; PhD 1, PD1, PI) → H1

- **T1.1 Electrical synapses of the gaze system in both sexes.** Neuron set: all lobula-plate
  tangential cells (the HS, VS and the further types catalogued in [90]), the four RMNs, neck motor
  neurons and optic-flow descending neurons, in the female FlyWire connectome (v783 [12]) and the
  male central-nervous-system connectome (v1.0 [39]). MESH detects appositions; a 3D convolutional
  classifier trained on the expert-validated sites (membrane apposition, pentalaminar profile, no
  chemical specialisation; negatives are rejected sites) ranks the rest; uncertainty-ranked queues go
  to expert and community proofreading (T5.3). *Validation:* held-out expert labels (precision and
  recall), agreement with the neurobiotin coupling in [14] and with the innexin immunostaining maps of
  [50]. *Sex comparison:* cell types are matched across the two connectomes with the cross-dataset
  typing of [47,39]; chemical and electrical connectivity of the gaze circuit are compared type by
  type. The expected result, a monomorphic circuit in *Drosophila*, is the baseline against which the
  hoverfly dimorphism is read; a difference would itself be a finding for H1's corollary.
  **D1.1 (M18):** open atlas of candidate electrical synapses of the fly gaze system, female and
  male, with the first sex comparison of this circuit (corollary of H1).
- **T1.2 Tier 1, biophysical.** Morphologically reduced multi-compartment HS, VS and RMN models
  built from the EM skeletons, active spike generation in the RMNs, chemical synapses from the
  connectome and gap-junction conductances proportional to validated apposition area. Parameters are
  fitted by gradient descent in a differentiable simulator [66] to published HS/VS physiology
  [11,31,32], RMN calcium tuning and the optogenetic displacement vectors of [14]. The front end is the
  differentiable detector bank (P4), with the connectome-constrained optic-lobe model of [45] as an
  alternative input.
- **T1.3 Tier 2, reduced.** Integrate-and-fire or adaptive-exponential point neurons with linear
  gap-junction coupling. Effective couplings come from Tier-1 transfer impedances. For each module
  (dendritic integration, gap-junction transfer, muscle mechanics) small Kolmogorov–Arnold networks
  [93] are trained on Tier-1 input–output pairs, pruned and regressed to closed-form expressions, so
  that the reduction is explicit and inspectable. We report error bounds on RMN tuning and latency
  (target < 10 % against Tier 1). **D1.2 (M24):** reduced model and the reduction toolkit, reusable
  for other circuits.
- **T1.4 Tier 3, trainable.** A connectome-masked SNN with sign constraints, trained with surrogate
  gradients [64,65] in a JAX/PyTorch stack that exports to the neuromorphic toolchains used in WP4.
  Gap junctions enter as differentiable linear couplings, which also regularises training.
- **T1.5 Motor readout and efference copy.** Muscle activation → force (Hill-type) → retinal
  displacement through the measured pull directions; the efference copy is a model output, tested
  against the HS recordings in [14]. Validated against retinal tracking in WP2.

### WP2 The dimorphic gaze circuit of *Eristalis* (M6–48; PD2 at MPI-BI, PhD 3 at LMU, PI) → H2, H2b

- **T2.1 Model families.** Male and female circuits are built by homology (HSN, HSE, HSS, HSNE, VS;
  RMNs of MOT, MOS and MIO), constrained by the tomography atlas (P5), the fills of T2.3 and published
  hoverfly physiology [1,15,17,23]. Four male hypotheses: **M-H2** (HSN → MIO), **M-HSNE** (HSNE →
  MIO), **M-HS** (pooled HS → MIO), **M-VS** (VS → MIO), each with and without an additional
  small-target input [16,63].
- **T2.2 Controversial stimuli.** For every model pair, stimuli are optimised to maximise the
  predicted difference in retinal trajectory or MIO activity, within display limits (luminance,
  contrast, spatio-temporal frequency) and under a naturalness prior. The expected evidence per trial
  sets the number of animals: the **power analysis is done in silico before any experiment**.
  **D2.1 (M24):** the stimulus set.
- **T2.3 Experiments (MPI for Biological Intelligence, Fenk laboratory; PD2, M7–42).** Tethered male
  and female *Eristalis*: retinal tracking through the cornea by deep-pseudopupil imaging under
  infrared light [7,14]; electromyography of MOT, MOS and MIO (the MIO is identified by its position
  between the two eyes [2]); intracellular recordings and neurobiotin fills of HSN, HSNE and the RMNs
  with sharp electrodes, the standard method in hoverfly tangential cells [1]; visual stimulation on
  an open platform [22]; animals reared year-round [19]. *Analysis:* hierarchical Bayesian comparison
  of the model families across animals [35].
- **T2.4 Free-flight retinal tracking (high risk, high gain).** Pursuit of artificial targets in an
  indoor arena [21] with head-mounted ultralight markers and high-speed cameras. Started only after
  T2.3 succeeds (decision at MS4); no other task depends on it.
- **T2.5 Developmental and genetic origin of the MIO (LMU, R. Merrill; PhD 3, M7–48) → H2b.**
  - *Origin:* a developmental series of male and female pupae (micro-CT and phalloidin confocal
    imaging) identifies the anlage the MIO forms from. Candidates: a split of the MOT anlage, or a
    further repurposed antennal muscle, as proposed for MOS and MOT [2].
  - *Genes:* sex- and stage-resolved RNA-seq of the anlage region at three pupal stages (pooled,
    low-input protocols), using the chromosome-level *E. tenax* genome [44]; male-biased muscle-identity
    genes and the sex-determination factors *doublesex* and *fruitless*; candidates localised by in
    situ hybridisation chain reaction in the muscle and in the MIO motor neuron.
  - *H2b, the motor neuron specifies the muscle:* in *Drosophila* the male-specific Muscle of Lawrence
    forms only when its motor neurons carry the male *fruitless* programme [42,43,79]. We predict the
    same logic in *Eristalis*: a male-specific identity of the MIO motor neuron induces the muscle, so
    that one dedicated neuron builds one dedicated muscle, mirroring H2.
  - *Comparison:* syrphid species with and without a male MIO from the tomography survey test whether
    candidate changes track the trait. *Exploratory, high risk:* RNAi knock-down in pupae.

### WP3 Theory: why is vision dimorphic? (M12–54; PD1, PI) → H3

- **T3.1 Embodied simulator.** Compound-eye sampling (including the male bright-zone resolution
  [15]), retinal actuators, simplified flight dynamics; GPU-based and open.
- **T3.2 Task optimisation.** Tier-3 networks are trained on *pursuit* (small fast targets in clutter
  [16,21]) or on *stabilisation* (hovering against optic flow; feeding approach [18]). Both conditions
  share the wiring prior and the spike-count energy penalty [80], and both may recruit a third
  actuator and shape its movement policy. Readouts: receptive-field width and position of HSN-like
  units, actuator recruitment and the performance–energy trade-off. Controls: shuffled wiring prior,
  a range of energy penalties, ≥ 10 seeds, and a variant in which the sensor-movement policy is
  optimised jointly with the network.
- **T3.3 Analysis.** Ablation to the minimal motif set; linear-response and mean-field theory of
  gap-junction-coupled populations; information-theoretic receptive-field analysis; Kolmogorov–Arnold
  readouts that convert trained networks into equations. **D3.2 (M48):** the motif catalogue.

### WP4 Active event-based machine vision (M13–60; PhD 2, RE, PD1, PI) → H4

- **T4.1 Active event-camera head.** A high-resolution event camera on a two-axis piezo tip-tilt
  stage that reproduces fly retinal trajectories (amplitudes of a few degrees [7]), carried by a
  pan-tilt gimbal on a motion platform that replays ego-motion. Movement policies: none, fixed
  artificial microsaccades [54], fly-derived (recorded in WP2, including the male MIO pattern) and
  learned (T3.2). Measures: event yield, static-scene acuity and latency.
- **T4.2 Motif SNNs on neuromorphic hardware.** Catalogue motifs (D3.2) become event-driven SNNs,
  deployed on a sensor-integrated chip with sub-milliwatt resting power [70] and on large-scale
  systems [67,68] through EBRAINS and vendor research programmes. Ablations: a Kolmogorov–Arnold
  parameterised event front end against convolutional front ends.
- **T4.3 Benchmarks (civil tasks, pre-registered protocols).**
  - **B-I Small-target detection and tracking in clutter:** our own *HoverEye* dataset, recorded with
    the active head (balls, insects and small drones against vegetation, with motion-capture ground
    truth) plus the public EV-IMO set [60]. Baselines: insect-inspired target detectors [61,107],
    event-based deep detectors [94] and converted SNNs. Metrics: detection F1, track continuity,
    event-to-output latency.
  - **B-II Ego-motion and optic-flow estimation:** MVSEC [59] and DSEC [58]. Baselines: E-RAFT [57],
    spiking optic-flow networks [55,56] and the fly-derived velocity CNN [38]. Metrics: endpoint error,
    latency, synaptic operations and measured energy on hardware against a GPU board.
  - **B-III Closed-loop hovering and pursuit on a quadrotor:** an indoor event-camera quadrotor with
    an on-board neuromorphic processor in a netted motion-capture arena, the robotic counterpart of the
    hoverfly arena of [21]. Tasks: hold position against optic flow (female task) and intercept a
    moving target (male task). Baselines: classical flow-based control and a GPU CNN pipeline [55].
    Metrics: position error, time to capture, energy per trial.

  *Protocol.* Each benchmark is pre-registered (tasks, splits, metrics, baselines, seeds, stopping
  rules) before data collection. Models are matched in parameter count and in synaptic operations
  per inference; energy is measured with a power meter on the deployed hardware and reported as
  accuracy per joule next to the GPU reference; five seeds per model; HoverEye is recorded under a
  CC-BY licence with target sizes, speeds and backgrounds drawn from the hoverfly-watch statistics
  (T5.4). H4 counts as supported if the motif SNNs with active sampling reach at least the baseline
  accuracy at one third of the energy, or 20 % higher accuracy per joule, on two of the three
  benchmarks. Results go to an open leaderboard that accepts outside entries.
  **D4.3 (M54):** the benchmark, HoverEye and the `hover-snn` library.
- **T4.4 Controversial stimuli for machines.** The WP2 engine applied to CNN–SNN pairs and to the
  movement policies as a robustness diagnostic (H4d).

### WP5 Embodied validation at scale, teaching and open science (M1–60; PI, SA, IU courses)

- **T5.1 Course integration.** HOVER modules in IU computer-vision courses every semester; student
  projects deliver benchmark entries and robot data; distance students receive a robot kit by mail.
- **T5.2 Robot zoo.** Schools, makerspaces and citizens run fly-type, female-type and male-type
  circuits on low-cost two-wheeled camera robots over printable pursuit and stabilisation courses.
  Logs (spikes, motor commands, camera-derived performance) go to an open database and are analysed
  with mixed-effects models [35] with participant and device as random effects: thousands of embodied
  trials under uncontrolled optics, lighting and noise.
- **T5.3 Community proofreading** of candidate electrical synapses in the MESH viewer, with an expert
  gold standard, feeding T1.1 [85].
- **T5.4 Hoverfly watch.** Smartphone slow-motion videos of male hovering and pursuit in gardens,
  with location and EXIF data stripped, give natural pursuit statistics (target sizes, speeds,
  backgrounds) for T3.2 and B-I.
- **T5.5 Open releases and evaluation.** Code under MIT, data under CC-BY, teacher kits; firmware
  hardware-neutral (one commercial, one open platform); learning outcomes measured before and after.

*Conflict of interest:* the PI holds a senior role at Backyard Brains, the manufacturer of one of
the candidate classroom robots. IU procurement selects robots against a hardware-neutral
specification without the PI's involvement, the quadrotor and the active head (WP4) use unrelated
vendors, and all code runs on at least one open platform.

## 3. Timeline, milestones and decision points

**Figure B3 (proposal/figures/fig_B3_gantt.png).** Gantt chart of the 22 tasks and six milestones (M1 = September 2028, placeholder). WP1, WP3 and WP4 form the modelling and engineering spine; WP2 and WP5 run alongside and feed data back.

| MS | Month | Milestone | Decision |
|---|---|---|---|
| MS1 | 12 | Electrical-synapse atlas v1 (female); Tier-2 *Drosophila* model | Tier-2 error against Tier 1 < 10 %? If not, Tier 1 serves WP2 |
| MS2 | 24 | Male atlas and sex comparison; male and female *Eristalis* model families; controversial stimuli designed in silico | Do the stimuli separate the families with the planned number of animals? If not, refine models before experiments |
| MS3 | 30 | Active head and quadrotor flying; robot zoo launched; HoverEye v1 | Hardware access confirmed, else GPU emulation with energy modelling |
| MS4 | 36 | H1 decided; tethered *Eristalis* data complete | Constraints fixed for WP3; go/no-go for T2.4 |
| MS5 | 48 | H2, H2b and H3 decided; motif catalogue | Motifs passed to WP4 |
| MS6 | 60 | H4 decided; benchmark, models, dataset and kits released | — |

## 4. Hypotheses: tests and what each outcome teaches

| Hyp. | Supported if | Falsified if | Value if falsified |
|---|---|---|---|
| H1 | The Tier-2 SNN with EM-derived weights predicts RMN preferred directions (± 15°), eye-movement direction and latency in both sexes | Connectivity-only models miss ≥ 2 RMN tunings | Unannotated or neuromodulatory inputs matter; the MESH search is widened |
| H2 | MIO activity follows HSN-preferred motion confined to the dorso-frontal field | MIO EMG tracks MOT-type or VS-type motion | The muscle is a general range extension; the model comparison still decides between families |
| H2b | *fruitless* or *doublesex* are expressed male-specifically in the MIO motor neuron and anlage; the muscle forms from a defined anlage only in males | No sex-biased expression in the motor neuron; specification is muscle-intrinsic | A muscle-intrinsic programme; still the first developmental account of a dimorphic eye muscle |
| H3 | Narrowed dorso-frontal integration and an extra effector emerge only under the pursuit objective | They emerge under both objectives, or neither | Points to developmental or genetic constraint rather than task optimality |
| H4 | Motif SNNs with active micro-movements beat matched baselines in accuracy per energy on ≥ 2 of 3 benchmarks | No advantage | A rigorous, open negative result for bio-inspired claims; the benchmark remains |
| H1b | The Tier-1/2 model reproduces, with no added pathway, the motor-related potentials of HS cells during spontaneous retinal movements (direction tuning R² ≥ 0.9 against [14]) | The coupling alone cannot produce them | Identifies the missing element (a chemical pathway, a delay) and constrains Tier 1 |
| H2c | Spontaneous MIO activity produces male-specific motor-related potentials in HSN; female HSN shows none | HSN motor-related potentials are the same in both sexes | The MIO channel is one-way; the efference copy is not part of the dimorphism |
| H3b | The narrowed male HSN field emerges only with the spike-count penalty | It emerges at any penalty, or never | Separates task from efficiency as the cause of the narrowing |

**Computer-vision hypotheses tested in WP4** (all against baselines matched in parameters and synaptic operations; metrics: accuracy per joule and latency; pre-registered):

| | Prediction | Test |
|---|---|---|
| H4a Task-specific sampling | Pursuit-type micro-movement policies beat fixed microsaccades [54] on small-target detection at equal event rate; stabilising policies win on ego-motion; no fixed policy wins both | B-I and B-II with the four policies of T4.1 |
| H4b Efference-copy cancellation | Feeding the motor command back into the motion units through the LPTC–RMN coupling motif removes self-generated events from the flow estimate better than software compensation [54] | Flow error during sensor motion, B-II and B-III |
| H4c Electrical pooling | Linear, delay-free pooling of local motion into wide-field units reaches a given ego-motion accuracy at lower event-to-command latency than learned synaptic pooling | Latency at matched accuracy, B-II and B-III |
| H4d Opponency and normalisation | Push-pull coding with dynamic signal compression [38] is more robust to contrast change and to controversial stimuli than convolutional front ends | T4.4 diagnostic on B-I and B-II |
| H4e Specialisation per joule | Under one energy budget, two task-specialised circuits with a shared front end, the dimorphic solution, beat one generalist circuit on the combined pursuit and stabilisation task | B-III with pursuit and hover episodes mixed |
| H4f Hyperacuity | Known micro-movements let the network localise small targets below the pixel pitch, as photoreceptor micro-movements do in the fly [51] | Localisation error against pixel size, B-I |

## 5. Risks and mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Gap-junction classifier does not generalise beyond validated sites | Medium | Medium | Expert and community proofreading; gap-junction weights become bounded free parameters |
| No *Eristalis* connectome, so the homology mapping is wrong | Medium | High | Competing model families instead of one model; discriminating stimuli; fills as ground truth |
| Hoverfly physiology slower than planned (non-genetic animal) | Medium | High | An experienced postdoc at the only site with the set-ups; stimuli designed in silico first; WP1, WP3 and WP4 do not wait |
| Developing muscle tissue too small for RNA-seq | Medium | Medium | Pooled samples, low-input protocols; HCR for *Drosophila*-known candidates as fallback |
| Free-flight tracking fails | High | Medium | Tethered closed-loop virtual flight; no task depends on T2.4 |
| Quadrotor integration delayed or unsafe; hardware access restricted | Medium | Medium | B-I and B-II are independent; the active head covers ego-motion; indoor netted arena only; two hardware routes plus GPU emulation with calibrated energy models |
| SNNs lose to deep baselines (H4 null) | Medium | Medium | Reported rigorously; hybrid motif front end with learned back end as a secondary result |
| Recruitment delays | Low | Medium | Posting on EURAXESS at signature; IU computer-vision students as the MSc → PhD pipeline |

## 6. Team, working arrangements and environment

- **PI (50 %, above the 40 % minimum):** scientific lead; WP1 and WP3 modelling; WP5 lead.
- **Team, three beneficiaries.** At IU: PD1, computational neuroscience and SNN theory (48 months);
  PhD 1, connectomics and machine learning; PhD 2, event-based spiking vision and neuromorphic
  hardware; a part-time research engineer for the active head, the quadrotor and the robot fleet (M13–48);
  student assistants. At MPI for Biological Intelligence (Active Sensing, L. Fenk): PD2, hoverfly
  physiology (36 months, M7–42). At LMU Munich (R. Merrill): PhD 3, evolutionary developmental
  genetics (48 months). The PI selects, funds and supervises all team members; the partner group
  leaders co-supervise locally and give access to their set-ups.
- **Relation to the Fenk laboratory's ERC project** on *Drosophila* eye-movement mechanisms: HOVER
  works on *Eristalis*, on models and on machines; the division of scope is fixed in a written
  collaboration agreement; data and tools flow both ways.
- **Doctoral route:** PhD students enrol at LMU (doctorate-granting), co-supervised by the PI [confirm
  the agreement and whether IU has doctoral rights].
- **Collaborators** (written consent before submission; roles limited to what is stated): L. Fenk
  (physiology set-ups, *Drosophila* RMN data, tomography); R. Merrill (genomics, developmental
  genetics); [neuromorphic hardware contact]; [event-camera or drone partner].
- **Working arrangements:** monthly all-team meeting in Munich; quarterly WP reviews against the
  milestones; one shared code and data repository with continuous integration; pre-registration of the
  benchmark protocols; a data management plan by M6.
- **Data and software management:** every model tier, stimulus set, recording and benchmark run is
  versioned and released with a DOI (Zenodo, DANDI for physiology, the FlyWire and MaleCNS
  annotation channels for proofread synapses); software follows a tested, documented release
  process with the pre-built MESH viewer as the model; PhD 1 acts as data steward with 10 % of time;
  a FAIR audit is part of every milestone review.
- **Environment:** the IU computer-vision group, students and GPU resources [confirm]; physiology
  and tomography at MPI-BI; genomics at LMU; EBRAINS neuromorphic access.

## 7. Ethics, civil focus, open science and data

- **Civil focus:** HOVER has an exclusive focus on civil applications. The quadrotor flies indoors
  only. Insects only (no vertebrates). Human participants (students, citizens including school pupils)
  take part with informed and parental consent under IU ethics approval, with GDPR-compliant data
  handling; uploaded videos are stripped of location and metadata.
- **AI:** HOVER develops AI-based vision models; no personal data are used for training.
- **Open science:** code under MIT, data under CC-BY via DANDI and Zenodo, immediate open access to
  publications, pre-registered benchmark protocols.

---

## Funding ID (not counted in the page limit)

*Required: current research grants and their subject, and any ongoing application for work related to
this proposal (IfA p. 29).*

| Title | Funder | Amount | Period | Role | Status | Relation to HOVER |
|---|---|---|---|---|---|---|
| [IU start-up package] | IU | [€] | [ ] | PI | [current] | [what it pays for; no overlap with HOVER costs] |
| [LMUexcellence Innovation Fund project] | LMU | [€] | [2024–] | [role] | [status] | [subject; no overlap] |
| [other current grants] | | | | | | |

No applications for work related to HOVER are pending.

## References

See `references.md` (not counted in the page limit).
