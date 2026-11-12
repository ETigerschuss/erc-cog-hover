# HOVER inside IU computer-vision teaching

Goal: every semester, students *do* part of HOVER, so teaching produces research outputs
(models, benchmarks, robot data) and HOVER gives the courses a distinctive, hands-on identity.
ERC reviewers value this when it is **integral, not decorative**. Each module below has a research deliverable.

| Course (adapt to IU curriculum) | HOVER module | Student deliverable → research use |
|---|---|---|
| Intro to Computer Vision | Optic flow two ways: Lucas–Kanade vs. Hassenstein–Reichardt (`hover.emd`) on SpikerBot camera streams | Comparison logs on real-world scenes → WP4 baseline data |
| Image Processing / Signals | Temporal filtering, ON/OFF pathways, contrast normalisation (Drews *et al.* 2020) | Filter-bank ablations → WP1 Tier-3 front end |
| Machine Learning for CV | Train a CNN vs. a connectome-masked SNN on velocity estimation | Entries to the HOVER benchmark (WP4.3) |
| Neuromorphic / Bio-inspired Vision (new elective) | Active event-camera head (micro-movement stage); build a motif-SNN; deploy on a camera robot; advanced projects on the indoor quadrotor | Motif-catalogue validation on hardware (T4.1–T4.3, T5.2) |
| Project / thesis (BSc/MSc) | Gap-junction classifier, robot-zoo firmware, controversial stimuli for CNNs | Theses as WP sub-tasks; best ones → co-authored papers |

## Platforms (three tiers)
- Lab: the active event-camera head on a motion stage (precise, WP4).
- Lab: one indoor event-camera quadrotor in a netted motion-capture arena for closed-loop hover and pursuit (WP4, supervised projects only).
- Scale: low-cost two-wheeled camera robots that run spiking neurons natively (SpikerBot or an open equivalent), for every student and for the robot zoo (WP5).

## Formats
- **Lab sessions** with the camera robots: each team gets a "male" and a "female" circuit and must
  find, by experiment, which one pursues a moving target better. This is H3 in miniature.
- **Challenge week**: controversial stimuli and closed-loop search. Students search for inputs that make two models disagree (`hover.controversial`) and tune the sensor movement of a simulated event camera for a task (`hover.eventcam`).
- Online/remote students (IU is largely distance learning): browser simulation of the same
  circuits + optional robot kit by mail. This is a scaling argument for reach.

## Evaluation
Pre/post concept inventories, project grades and robot-log quality. Human-participant
research → IU ethics approval, informed consent, GDPR.
