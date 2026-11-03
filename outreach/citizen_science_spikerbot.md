# Citizen science with spiking robots (WP5)

Built on the open-citizen-science framework of Serbe-Kamp *et al.* 2023 (RIO): participants are
contributors who generate data and co-own results, not only an audience.

## Three strands

### 1. Robot zoo: a distributed embodied experiment (tests H3/H4 in the real world)
- Participants (schools, makerspaces, IU students, outreach events) run standardised
  circuits ("Drosophila-type", "Eristalis female-type", "Eristalis male-type with third effector")
  on spiking robots with a camera.
- Standard tasks with printable arenas: (a) follow a moving target (pursuit), (b) hold
  heading against a rotating pattern (stabilisation/OKR).
- Robots log spikes, motor commands and camera-derived performance. Upload goes to an open
  database, giving thousands of embodied trials under uncontrolled real-world optics,
  lighting and noise. This is a robustness test no lab could run alone.
- Analysis: mixed-effects models with participant/device as random effects (cf. Dingemanse & Dochtermann 2013).

### 2. Gap-junction proofreading in MESH
- MESH web viewer with a simplified "is this a membrane apposition?" task on EM cutouts.
- Consensus of ≥ N citizens + expert gold-standard subset → training labels for the GJ classifier (WP1.1).
- Model: FlyWire's community proofreading. Credit contributors in data releases.

### 3. Hoverfly watch
- Hoverflies are common pollinators. Smartphone slow-motion videos of male hovering/pursuit
  in gardens give natural-scene and behaviour statistics (pursuit speeds, target sizes) for
  the WP3 task definitions. Link to existing pollinator-monitoring schemes.

## Platform and neutrality
- SpikerBot (Backyard Brains) is the reference platform because it natively runs
  spiking-neuron circuits with a camera at classroom cost.
- All firmware and circuit files are open (MIT) and portable to ESP32/RPi robots, so the
  project does not depend on one vendor. The PI's Backyard Brains affiliation is declared and managed:
  see `docs/coi_backyard_brains.md`.

## Ethics
- School pupils are minors: parental consent, no personal data in robot logs (pseudonymous device IDs),
  IU ethics approval before launch. Strip GPS/EXIF from uploaded videos. See `admin/ethics_security_self_assessment.md`.

## Metrics (for the ERC "impact" narrative, and for reporting)
Participants, trials uploaded, labels contributed, schools reached, student theses,
open-source downloads, robot-zoo papers with citizen co-authors.
