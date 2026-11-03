# Blockers and decisions to clear before writing further

These items decide whether the proposal can be submitted and to which panel. Clear them first.

## 1. Host institution: which "IU"?  ⛔ blocker

- **IU Internationale Hochschule (Erfurt, DE)**: eligible as an ERC host (legal entity
  in an EU Member State). However, ERC panels check **whether the host provides the
  conditions for frontier research**. A private university of applied sciences
  oriented toward teaching will be questioned on: lab space for fly work, GPU/HPC,
  PhD supervision rights (does IU award doctorates? If not, plan co-supervision with
  LMU / MPI-BI / a TU), and protected research time. Get this in writing in the host
  support letter (`admin/host_support_letter_template.md`).
- **Indiana University (Bloomington, US)**: **not an eligible host.** Options would be a
  European host, or a different funder (NSF CAREER, NIH BRAIN Initiative).

→ Decision: ________

## 2. Years since PhD  ⛔ blocker

CoG window: 7 to 12 years since PhD on 1 January of the call year (plus documented extensions).

| Call | Reference date | PhD must be between |
|---|---|---|
| ERC-2027-CoG | 1 Jan 2027 | 1 Jan 2015 – 31 Dec 2019 |
| ERC-2028-CoG | 1 Jan 2028 | 1 Jan 2016 – 31 Dec 2020 |

PhD date (date of award on the certificate): ________ → Call: ________
If it falls before the window: consider Advanced Grant (AdG) later, or claim eligible extensions.

## 3. Conflict of interest with Backyard Brains / SpikerBot  ⚠️ must be declared

The proposal uses SpikerBot and SpikeStation (Backyard Brains). If the PI is employed
by, owns shares in, or is paid by Backyard Brains, then:

- declare it in Part A and in the host letter;
- **do not** budget SpikerBot purchases as a sole-source supplier without a market justification
  (EU procurement rules, best value for money);
- make all HOVER software, models and teaching material **open and
  hardware-agnostic** (MIT/CC-BY), runnable on any Arduino/ESP32/RPi robot. SpikerBot is
  then the reference platform, not a dependency;
- keep the interview answer ready: "Why this robot?" → low cost, already deployed in
  schools, native spiking-neuron programming, camera + motors, existing user community.

## 4. Panel choice: LS5 or PE6?

| | LS5 (neuroscience) | PE6 (computer science) |
|---|---|---|
| Track-record fit | Strong (Nat Neurosci 2023, Neuron, Curr Biol, Nature co-authorships) | Weaker: few CV/ML venue papers yet |
| Fit with the new professorship | Neutral | Strong |
| Risk | Reviewers may see the CV/robotics aims as an add-on | Reviewers may see the fly work as "just biology", and the benchmark bar is high (CVPR-level baselines) |

**Recommendation: LS5 primary, PE6 secondary reviewer request.** Frame the project
as *computational neuroscience with a computer-vision test bed*: the question is
biological (why is the system dimorphic?), and the computer-vision aims are the
**test** of whether the extracted computations are general. Revisit this if you have
CV-venue papers by submission.

## 5. Independence from former mentors

The CoG panel checks that the PI is independent. Fenk and Borst / Ammer appear on the
key preprints. Make clear:

- MESH was conceived and built by you (sole software author in `CITATION.cff`);
- HOVER's questions (dimorphism → task-specific SNNs → CV) are yours and not a continuation of the Fenk lab programme;
- the Fenk lab is a **collaborator** (letter of commitment for *Drosophila* EMG/imaging
  and micro-CT access), not a co-PI. Do not list former supervisors as team members.

## 6. "Eigene Stelle" (DFG) vs. ERC

With a professorship you can no longer use the DFG *Eigene Stelle* module (it funds the
applicant's own position). The DFG version of this work should be resubmitted as a
regular **Sachbeihilfe** (positions for PhD students and postdocs, no PI salary), or folded into HOVER.
Before resubmitting, check DFG/ERC double-funding rules: overlapping objectives must
be declared, and the same work cannot be funded twice.
