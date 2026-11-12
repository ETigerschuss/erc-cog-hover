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
Seeing is active: eyes move, and how they should move depends on the task. Machine vision is rediscovering this with event cameras, which are blind to static scenes unless the sensor moves. Flies solve the problem on a few milliwatts, and evolution has left a clean experiment. Male hoverflies (Eristalis tenax) chase mates in aerial pursuits; females do not. Males have a specialised dorso-frontal eye zone, a sexually dimorphic motion-sensitive neuron and, as we discovered, a male-only third muscle that moves the retina beneath the lenses. Nobody knows what it is for. HOVER will find out, explain why the male's task demands it, and test whether the answer is a design principle for machine vision.
We will (1) build the first connectome-constrained spiking model of a complete gaze loop, from photoreceptors to eye movement, including the electrical synapses we found between motion-sensitive neurons and eye-muscle motor neurons, in the female and the new male Drosophila connectome; (2) map the model onto male and female hoverflies, let it design the stimuli that single out the third muscle, and test them with retinal tracking in closed loop and muscle recordings, while tracing the muscle's developmental and genetic origin; (3) train the models on pursuit versus stabilisation under identical wiring and energy budgets, to test whether the male features emerge as task-optimal solutions; (4) transfer the principles to event cameras that move their sensors, with spiking networks on neuromorphic hardware, benchmarked against deep networks on small-target detection, ego-motion estimation and closed-loop flight; and (5) validate every model on low-cost spiking robots run by students and citizens.
HOVER delivers the first photon-to-eye-movement model of a visual circuit, the function and origin of a sex-specific eye muscle, and open, tested design principles for efficient active machine vision.
<!-- ABSTRACT END -->

## Why a second panel

HOVER asks a question of systems neuroscience: why is the hoverfly visual system sexually dimorphic,
and which circuit motifs make it task-specific (LS5_16, LS5_7)? Two of its five objectives, however,
are tested in machines. Objective 4 builds event-based spiking vision systems with task-dependent
sensor micro-movements and benchmarks them, on public event-camera datasets and on neuromorphic
hardware, against deep-network baselines (PE6_11, PE6_14). Objective 5 runs the models on robots
at scale. Reviewers with expertise in computer vision and neuromorphic computing are needed to judge
the benchmark design, the baselines and the hardware claims of that part of the work.
