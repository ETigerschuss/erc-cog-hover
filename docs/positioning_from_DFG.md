# From the DFG *Eristalis* proposal to the HOVER ERC CoG

Source: `ETigerschuss/dfg-eristalis` → `proposal.md` (as-submitted version, 2026; planned start 1 Oct 2026).

| Dimension | DFG (36 mo, MPI-BI, with L. Fenk) | HOVER ERC CoG (60 mo, IU, single PI with own team) |
|---|---|---|
| Core question | What does the male third retinal muscle do? | **What makes a visual system task-specific, and do those motifs generalise to engineered spiking vision?** The *Eristalis* dimorphism is the natural experiment. |
| Level | Circuit → muscle → retinal displacement | Connectome → SNN theory → active-vision CV systems → robots / people |
| Models | Tier-1 HH toy model in MESH; CMA-ES adversarial stimuli | Three-tier modelling ladder (biophysical HH/compartmental → reduced LIF/AdEx with gap junctions → trainable SNN), with **mathematical reduction** linking the tiers; controversial stimuli between *model families*, not only between 2- and 3-muscle circuits |
| Experiments | EMG, patch clamp, free flight, micro-CT done in-house | Hypothesis-critical experiments by HOVER PhD students hosted at **MPI for Biological Intelligence** (Fenk lab: physiology) and **LMU** (Merrill lab: developmental genetics) |
| Development / genetics | — | **New:** where the male third muscle comes from and which genes make it male (T2.5, H2b), with the motor neuron as candidate inducer |
| Computer vision | Braitenberg-vehicle outreach day | A full work package: event cameras, SNNs with active micro-movements, small-target detection in clutter, ego-motion; benchmarks against CNNs (Drews et al. 2020 `deepfly`) |
| Outreach | One day, ~200 visitors | Continuous: SpikerBot inside IU CV courses every semester, a distributed "robot zoo" citizen-science experiment, and community proofreading of gap junctions in MESH |
| Connectomics | FlyWire (FAFB) via MESH | FlyWire via Codex, plus newer datasets on platforms such as coda.science (**verify what it provides and how to cite it**), MESH gap-junction proofreading pipeline, transfer of the Drosophila wiring to Eristalis |

## Material reused directly

- Fig. 1 (CT, stepwise evolution, Kviatko et al.), Fig. 2 (neurobiotin + MESH + RMN tuning, Falt, Ammer et al.), Fig. 3 (Tier-1 circuit model).
- H2 (HSN → RMN MOI → third muscle) becomes **H2** in HOVER, generalised to: "dimorphic receptive fields + dedicated effector = a task-specific channel".
- Risk table structure, data management plan (rewrite for IU infrastructure).

## Material that must go or shrink

- Free-flight EMG in three species: too wet-lab-heavy for a CV professorship. Keep one
  *Eristalis* free-flight eye-tracking aim as the **high-risk/high-gain** element (through a partner).
- *Musca* / *Calliphora* comparisons → cite as literature only.
- Muscle biomechanics (Hill model, micro-CT dynamics) → a reduced module in WP1, collaborator-supported.

## Rules that make the distinction essential

- The ERC wants "truly novel ideas, not just continuations of ongoing work or existing collaboration" (IfA p. 7).
  HOVER must read as *your* new programme, not the Fenk-lab project in a bigger form.
- The 2026 DFG draft was never submitted, so the **Funding ID** (B2) lists no related application. If the DFG
  backup is submitted later, keep its scope separate from HOVER's.
- B2 now has only **7 pages**, so the background, objectives and the "why" must be complete in B1 Part I.

## Keys to the ERC narrative

1. **Ground-breaking**: the first connectome-constrained SNN that explains a *sexual
   dimorphism* in vision as a task-optimal solution, *and* shows that the solution transfers to machines.
2. **Ambition**: closes the loop from synapse (gap junction in EM) to behaviour (eye
   movement) to engineering (event-camera target tracking) to society (thousands of students and citizens running fly circuits).
3. **Feasibility**: MESH (49 validated MN–LPTC contacts, 2,895 EM images), the Tier-1 model,
   ALIstim differentiable detectors, the CT atlas, and a PI who has done EM, physiology, modelling and outreach.
