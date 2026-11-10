<!-- ERC-2027-CoG Part B1 cover page (not counted in the page limits).
Every page of B1 carries the header:  Serbe-Kamp | HOVER | Part B1
The abstract below must be identical to the abstract in Part A (tools/check_limits.py checks this). -->

# ERC Consolidator Grant 2027: Research Proposal, Part B1

**Acronym:** HOVER

**Title:** Hoverfly-Optimised Vision through Event-driven Recurrent spiking circuits: from a sexually dimorphic eye to active machine vision

**Principal Investigator:** Prof. Dr. Étienne Serbe-Kamp

**Host institution:** IU Internationale Hochschule GmbH, Germany *[confirm exact legal name]*

**Proposal duration:** 60 months

**Primary panel:** LS5, Neuroscience and Disorders of the Nervous System · **Secondary panel:** PE6, Computer Science and Informatics

## Abstract

<!-- ABSTRACT START -->
Animal eyes are built for the tasks their owners face, yet it is hard to say which circuit features exist because of a task: species differ in too much at once. Sexual dimorphism removes this confound. Male hoverflies (Eristalis tenax) chase mates in aerial pursuits, and their visual system differs from the female one at every level: a high-acuity dorso-frontal zone, a sexually dimorphic motion-sensitive neuron (HSN) and, as we discovered, a male-only third retinal muscle, set between the eyes, that moves the retinae beneath the lenses. HOVER asks which circuit motifs make a visual system task-specific, and whether those motifs are design principles that engineered spiking vision can use.
We will (1) build the first connectome-constrained spiking model of a complete gaze loop, from photoreceptors to eye movement, including the electrical synapses we found between motion-sensitive and eye-muscle motor neurons, at three linked levels (biophysical, reduced, trainable) and in both the female and the new male Drosophila connectome; (2) map the model onto male and female hoverflies, test competing circuit hypotheses with optimised controversial stimuli, retinal tracking and muscle recordings, and trace the developmental and genetic origin of the male muscle; (3) train the models on pursuit versus stabilisation under identical wiring and energy budgets, to test whether the male features emerge as task-optimal solutions; (4) transfer the extracted motifs to event-camera spiking vision with task-dependent sensor micro-movements on neuromorphic hardware, benchmarked against deep networks for small-target detection, ego-motion and depth estimation, and closed-loop tracking; and (5) validate every model on low-cost spiking robots run by students and citizens.
HOVER delivers the first photon-to-eye-movement model of a visual circuit, a mechanistic and normative explanation of a visual sexual dimorphism, and open, tested design principles for efficient active machine vision.
<!-- ABSTRACT END -->

## Why a second panel

HOVER asks a question of systems neuroscience: why is the hoverfly visual system sexually dimorphic,
and which circuit motifs make it task-specific (LS5_16, LS5_7)? Two of its five objectives, however,
are tested in machines. Objective 4 builds event-based spiking vision systems with task-dependent
sensor micro-movements and benchmarks them, on public event-camera datasets and on neuromorphic
hardware, against deep-network baselines (PE6_11, PE6_14). Objective 5 runs the models on robots
at scale. Reviewers with expertise in computer vision and neuromorphic computing are needed to judge
the benchmark design, the baselines and the hardware claims of that part of the work.
