# Ethics and security self-assessment (Part A): draft

Both tables must be completed even where nothing applies. Page numbers given in the ethics table must
point to **Part B2** (IfA p. 26). Ethics review happens only after a positive evaluation, but a complete
self-assessment speeds it up (IfA p. 19–20).

## Ethics issues table

| Area | Applies? | In HOVER | What to write or do |
|---|---|---|---|
| Human participants | **Yes** | IU students (courses); citizens, **including school pupils (minors)**, in the robot zoo; teachers | Informed consent; **parental consent for minors**; voluntary participation; research consent kept separate from grading; IU ethics-committee approval before T5.2 / T5.5 |
| Personal data | **Yes** | Contact data, pre/post surveys, robot logs (pseudonymous device IDs), photos/videos at events; "Hoverfly watch" phone videos can contain people or GPS metadata | GDPR; data minimisation; strip EXIF/GPS on upload; pseudonymisation; IU data-protection officer; data management plan within 6 months (IfA p. 8) |
| Animals | **Yes (insects only)** | *Drosophila* (including GAL4/UAS transgenic lines at MPI-BI) and lab-reared *Eristalis tenax* [19] | No vertebrates or cephalopods, so outside Directive 2010/63/EU. Transgenic flies are kept under the partner facility's S1 genetic-engineering approval (GenTG) *[confirm]*. Humane handling: short tethering, cold/CO₂ anaesthesia. |
| Non-EU countries / genetic resources | Possibly | Specimens or DNA of syrphid species collected outside the EU (T2.5 comparison) | EU access-and-benefit-sharing rules (Nagoya Protocol, Regulation (EU) 511/2014): due diligence and permits; material-transfer agreements |
| Environment, health and safety | Minor | IR illumination, lasers in microscopy, robots in classrooms | Laboratory safety rules; CE-marked robots; a risk assessment for school events |
| Artificial intelligence | **Yes** | Development of spiking networks, computer-vision models and autonomous robots | Research use only, not a high-risk AI system under the EU AI Act *[check]*; no personal or biometric data in training sets; documented datasets; human oversight of robots |
| Civil applications | — | HOVER has an **exclusive focus on civil applications** | State it in B2 §7 |

## Security issues table

| Question (paraphrased) | Answer | Note |
|---|---|---|
| Use or generation of classified information | No | — |
| Potential for misuse of results | **Answer carefully: low, and explain** | Small-target detection and target tracking are dual-use in principle. HOVER develops generic, published, bio-inspired vision models evaluated on civil tasks: collision avoidance, ego-motion, insect tracking, classroom robots. No weapons, targeting or surveillance applications; no export-controlled hardware. Follow the Commission guidance note on potential misuse of research results. |
| National or third-country security restrictions | No *[check the terms of any neuromorphic-hardware access]* | — |
