# HOVER model v0: from the eye to the eye movement, three circuits, one stimulus engine

Status 3 Nov 2026. This document fixes the architecture of the computational model that underlies
WP1–WP3 and the preliminary results in B2, answers the question "does the whole set-up make sense",
records what the first implementation reproduces, and lists what is fixed by data, what is a free
parameter, and what still has to be supplied. Code: `code/hover/` (see §5).

## 0. Verdict

The set-up makes sense and is the right order of operations. Three adjustments make it defensible:

1. **One ground truth, two derived models.** The *Drosophila* female circuit is the only one with a
   connectome, measured HS/VS tuning, measured motor-neuron tuning, measured muscle pull directions,
   a measured optokinetic reflex and a measured efference copy (Falt *et al.* 2026). Every stage of the
   model is fitted and validated there first (§3). The hoverfly models are built from it by homology,
   and every hoverfly-specific element is an explicit, named free parameter or hypothesis (§4).
2. **The eye comes first.** Receptive fields are not rectangles in azimuth and elevation. They sit on
   a compound eye whose ommatidial lattice is sheared and non-uniform, so the *local* preferred
   direction of the motion detectors feeding an LPTC depends on where on the eye the LPTC looks
   (Zhao *et al.* 2025). The model therefore starts from an eye map on the sphere, species- and
   sex-specific, and the male hoverfly's bright zone enters as a change of the sampling density, not
   as a label.
3. **The behaviour to predict is the retinal movement.** The circuit model ends in the retinal motor
   neurons and the muscles; its direct, quantitative output is the retinal displacement, which is
   measured through the cornea in tethered animals and is the quantity Falt *et al.* predict with
   R² = 0.994. Flight behaviour (hovering, optomotor turns, pursuit) runs through descending neurons
   and the wing motor, is sexually monomorphic in the optomotor domain (Nicholas *et al.* 2026) and
   would blur the test. So: primary readout = retinal trajectory (deep-pseudopupil tracking) plus EMG
   of the three muscles; secondary readout = tethered-flight optomotor and pursuit responses; the
   SpikerBot carries the same circuits as an embodied demonstration and a robustness test of the
   task-specific-channel idea, not as a test of the MIO (§6).

## 1. Pipeline (implemented)

```
stimulus movie (az, el, t)
   │  Stage 0  eye map on the sphere: ommatidia, local +h/+v axes, virtual neighbours   hover/eye.py
   ▼
photoreceptors → lamina (high-pass + DC, ON/OFF half-wave)                              hover/hrbl.py
   │  Stage 1  T4/T5 three-arm detectors along the local lattice axes (Ammer calc_HRBL)
   ▼
   │  Stage 2  local opponency circuits per ~20-ommatidium patch: the six-unit recurrent
   │           network of Ammer et al. 2023 (T4T5 ± , LPi ± , LPTC ± ; τ = 20 ms)       hover/hrbl.py
   ▼
   │  Stage 3  LPTC receptive fields → g_exc, g_inh (RF-weighted means over patches)    hover/lptc.py
   │           membrane: V = (40 g_e − 20 g_i)/(g_e + g_i + 1)  [mV rel. rest]
   ▼
   │  Stage 4  electrical network: HS chain, VS chain, LPTC↔RMN gap junctions,          hover/tier1_hh.py
   │           HH retinal motor neurons (MESH Tier-1); conductance drive with the
   │           Ammer reversal potentials; tonic rate calibrated to 100 Hz
   ▼
   │  Stage 5  oculomotor model: retinal shift = Σ w_i · unit(θ_i); frames             hover/oculomotor.py
   ▼
retinal-shift vector / trajectory  ──►  Stage 8 readouts: DPP tracking, EMG, tethered flight, robots
   ▲
   │  Stage 7  stimulus engine: (i) parametric evolution strategy on a rate surrogate,
   │           Tier-1 verification (hover/adversarial.py); (ii) pixel-level gradient descent
   │           through the whole front end with autograd (hover/frontend_ad.py)
   │  Stage 6  species variants: Drosophila ♀ (ground truth), Eristalis ♀, Eristalis ♂ (+MIO)
   │                                                                                     hover/species.py
```

### Stage 0: eye map (`hover/eye.py`)

- Ommatidia are placed on the unit sphere by growing a hexagonal lattice in the azimuthal-equidistant
  chart around the acute zone, with radial steps integrated from the local inter-ommatidial angle
  Δφ(az, el), followed by a spring relaxation on the sphere (rest length = Δφ at the bond midpoint)
  and an elliptical field-of-view clip. *Drosophila*: Δφ 4.0° frontal-equatorial → 6.2° periphery
  (Zhao *et al.* 2025), 886 ommatidia, 47 local circuits. *Eristalis* ♀: Δφ 1.6° → 3.0° [verify,
  Straw 2006], 4,864 ommatidia, 220 circuits. *Eristalis* ♂: same plus a dorso-frontal bright zone
  (ellipse at azimuth −5°, elevation 30°, semi-axes 22° × 25°, Δφ ≈ 1.0° [verify]), 5,215 ommatidia,
  235 circuits. Because a hexagonal lattice cannot expand its ring count outward, the realised
  lateral spacing is ~0.65–0.75 of the nominal Δφ (as in real eyes, which solve this with shear and
  lattice defects); the detectors are not affected (next point).
- Local axes: the +h axis (T4a/T5a, HS) is a normalised mixture of the yaw-rotation flow (fraction
  `yaw_fraction` = 0.4) and the expansion flow of forward translation, which tilts +h upward in the
  dorso-frontal and downward in the ventro-frontal eye (±44° at azimuth 0–20°, elevation ±20–50°),
  as described for the T4b map by Zhao *et al.* (globally aligned with yaw and reverse thrust). The
  +v axis is +h rotated by the local shear angle α (75–105°, < 90° fronto-dorsally and
  postero-ventrally).
- Detector arms sample the stimulus at **virtual neighbours**: the points one local Δφ away along
  ±h and ±v, after a Gaussian optical blur of σ = Δφ/2. So the detector geometry (axis and
  baseline) is exact by construction, independent of lattice frustration.
- Patches of ~20 ommatidia (blocks of the initial lattice) host one local opponency circuit each.

### Stages 1–2: detectors and the Ammer local circuit (`hover/hrbl.py`)

Taken verbatim from the Ammer *et al.* 2023 Figure-7 notebook (supplied 3 Nov):
- lamina: `interim = highpass(x, 250 ms) + 0.1·x`; L1 = rect(interim); L2 = rect(−(interim − 0.05));
  delayed arms lowpass(x, 50 ms) (ON) and lowpass(1 − x, 50 ms) (OFF);
- detectors: `T± = rect(A·B/(DC + C), DC)` with A, C the delayed arms of the two neighbours, B the fast
  arm of the centre, DC = 0.02 (threshold and offset), ON → T4, OFF → T5;
- local circuit: six leaky units (τ = 20 ms) with the connection matrix `connM` (LT 0.5, TL 1, LL 1,
  TV 1, LV 1): T4T5± receive −LT·LPi∓, LPi± receive TL·T4T5± − LL·LPi∓, LPTC± receive
  TV·T4T5± − LV·LPi∓; input = patch mean of rect(T4 + T5) per direction; all eight blocking
  conditions of the notebook (`block_feedb`, `block_LT`, `block_LL`, `block_LV`, LPi and T4T5
  blocks) are available as `CircuitParams.condition` for in-silico ablations;
- conductances and membrane: g_exc = TV·mean rect(T4T5_PD), g_inh = LV·mean rect(LPi_ND),
  V = (40 g_e − 20 g_i)/(g_e + g_i + 1). The ALIstim HRBL class is the feed-forward special case.
- Check: a full-field grating (λ 30°, 30°/s, the Falt stimulus) gives HSE g_e = 0.77, V = +15 mV in the
  preferred and g_i = 0.77, V = −10 mV in the null direction; VS3 +17 / −11 mV; the same range as the
  notebook's VS responses and Ammer's recordings.

### Stage 3: receptive fields (`hover/lptc.py`)

| Cell | *Drosophila* ♀ | *Eristalis* ♀ | *Eristalis* ♂ | axis / PD |
|---|---|---|---|---|
| HSN, HSE, HSS | dorsal / equatorial / ventral thirds | HSN: broad Gaussian, centre (−8°, 25°), σ 20° × 20° (Nordström 2008) | HSN: narrow Gaussian, centre (0°, 25°), σ 9° × 16° | +h (front-to-back) |
| HSNE | – | azimuth 0–90°, elevation 0–60° [verify] | same | +h [verify: upward component] |
| VS1–4 | azimuth columns −10–30, 25–65, 60–100, 95–140° | same | same | −v (downward) |

### Stage 4: electrical network (`hover/tier1_hh.py`)

MESH Tier-1 presets for LPTCs (graded, K⁺ and T-type Ca²⁺) and motor neurons (HH + persistent Na⁺),
low-pass-filtered bidirectional gap junctions. Three changes for HOVER: (i) conductance drive
g·g_leak with reversal potentials rest + 40 / rest − 20 mV, so that the Tier-1 LPTC reproduces the
Ammer membrane in steady state; (ii) `lptc_leak_scale` = 50: the preset LPTC leak (0.057) is far below
the junction conductances, so the motor neurons would clamp the LPTCs; the real cells are large and
low-impedance, and the scaling makes them stiff graded voltage sources whose coupling onto the RMNs is
set by `g_lptc_mn` (= 0.5) alone; (iii) bias calibration: each RMN's bias current is set so that its
tonic rate at rest is 100 Hz, compensating the tonic junction current (Falt: RMNs operate at an
intermediate activation regime with a bidirectional range). With these settings a preferred-direction
grating modulates MOT by +26/−26 Hz (HS cells) and MOS by +33/−14 Hz (VS cells); stronger coupling
drives the HH neurons into depolarisation block.

### Stage 5: frames and the oculomotor model (`hover/oculomotor.py`)

Falt *et al.* express visual motion and retinal shifts in one holder frame: 0° anterior
(back-to-front motion; retina toward the antennae), 90° dorsal, 180° posterior, 270° ventral. The
model frame (right eye) has 0° = toward +azimuth (front-to-back), 90° upward; the two are mirror
images, θ_model = 180° − (θ_Falt − β), where β is the rotation of the holder frame relative to the
anatomical eye frame (head pitch in the holder). Retinal shift = Σ w_i·unit(θ_i) with w_i the
baseline-normalised rate change of RMN i and pulls MOS 51°, MOT 320° (Falt); a retinal shift in
direction s produces visual motion in direction s, so the OKR to motion φ is a shift toward φ + 180°.

## 2. Ground truth from Falt *et al.* 2026 (numbers used in the model)

- One motor neuron per muscle: MOS RMN = CB0901, MOT RMN = CB0804 (FAFB).
- Muscle pull directions (holder frame): MOS 51 ± 4° (forward and up), MOT 320 ± 4° (forward and
  down), both together 354 ± 4°; the two pulls are orthogonal.
- RMN preferred directions (holder frame): MOS 212 ± 2° (DS 0.76, opponency 0.42); MOT 141 ± 2°
  (DS 0.79, opponency 0.48); broadly tuned to front-to-back motion, peaks 72° apart.
- Electrical partners (results text, Fig. 4h, and the efference-copy methods): MOS RMN ↔ HS (3 cells)
  and VS1–4; MOT RMN ↔ HS only. MOT PD within 7.96° of the HS PD; MOS PD within 6.38° of the linear
  sum 4/7·VS1–4 + 3/7·HS of normalised tuning curves. **Note for the authors: the sentence in the
  methods "MOS RMN tuning was determined solely by HS cell tuning, whereas MOT RMN tuning was
  calculated as the weighted sum of VS1-4 … and HS" has MOS and MOT swapped relative to the results,
  Fig. 4 and the efference-copy section.**
- Chemical visual input to RMNs is 3 % of their synapses; T4/T5 silencing abolishes the OKR; shakB²
  mutants show a reduced OKR and less directional optogenetic responses.
- OKR: inverted predicted shift direction vs stimulus direction, R² = 0.994, slope 1.01, mean
  deviation 7.07°. Efference copy: HS membrane potential changes mirror the visual tuning
  (R² = 0.97, slope −1); amplitude scales with movement size.
- Stimulus: full-contrast sine grating, λ = 30°, 30°/s (1 Hz), 3 s, eight directions.

## 3. Validation v0 of the *Drosophila* ♀ model (`python -m hover.validate_falt --wvs 2`)

Twelve grating directions (λ 30°, 30°/s, 1 s of motion), the circuit above, one fitted frame
rotation β and one fitted wiring ratio `w_vs_mos` (VS1–4 → MOS junction conductance relative to
HS → MOS, per cell):

| Quantity | Falt *et al.* 2026 | model (w_vs_mos = 1) | model (w_vs_mos = 2) |
|---|---|---|---|
| MOT PD | 141° | 159° | 149° |
| MOS PD | 212° | 204° | 210° |
| MOS − MOT divergence | ≈ 72° | 45° | 61° |
| MOT − HS | 8° | 4° | 2° |
| MOS − linear sum (4/7 VS + 3/7 HS) | 6° | 2° | 13° |
| VS1–4 PD (prediction) | – | 243° | 233° |
| OKR mean error (inverted shift vs stimulus) | 7.1° | 23° | 20° |
| fitted β | – | −25.5° | −34.5° |
| tonic rates MOT / MOS | – | 113 / 124 Hz | 110 / 141 Hz |

What the model reproduces without tuning: the MOT PD follows the HS cells; the MOS PD is the
electrical linear sum of VS1–4 and HS; the two RMNs diverge; the inverted vector sum of the pulls
tracks the stimulus direction (slope 1). What it does not yet reproduce: the full 72° divergence and
the 7° OKR precision. Both depend on the same two quantities, the VS/HS weight into MOS and the
sharpness of the RMN tuning (model DSI ≈ 0.5 vs 0.76–0.79). The weight is a **prediction for WP1**:
matching the divergence requires VS1–4 → MOS gap junctions about twice as large per cell as
HS → MOS, which T1.1 will read off the validated apposition areas in FAFB. The sharpness is set by
the eye-lattice tilt (broadens the HS population tuning) and by the RMN f–I curve; WP2 recordings
constrain both. The direction-dependent OKR error is largest where both RMNs respond weakly
(stimulus 60–90° in the model frame) and is a direct consequence of a divergence below 90°: this is
why the system needs the VS input to MOS, and the hoverfly's third muscle is the obvious candidate
for completing the basis in the male.

Figure: `scratchpad/val_w2.0.png` (eye map with local axes; LPTC tuning; RMN tuning in the holder
frame with Falt's PDs; OKR plot) — to be copied into `proposal/figures/` once the parameters are final.

## 4. Free parameters and hypotheses of the hoverfly models

| Parameter | Prior / v0 value | Fixed by |
|---|---|---|
| θ_MIO (pull direction) | 0° (anterior/medial pull) or 90° (dorsal); CT fibre orientation says mainly horizontal | WP2 CT at contraction, EMG + tracking |
| MIO drive | HSN (H2), HSNE, pooled HS, VS | neurobiotin fills, stimuli optimised on MIO activity |
| HSN ♂ receptive field | Nordström 2008 contours (Gaussian fits above) | WP2 recordings |
| HSNE local PD | +h with an upward component | WP2 recordings |
| LPTC↔RMN conductances | g_lptc_mn 0.5, VS→MOS ×2 (Falt fit) | WP1 apposition areas, WP2 fills |
| Bright-zone sampling | Straw 2006; v0 ellipse | optics, CT |
| Hoverfly MOS/MOT pull directions | same as *Drosophila* | CT |
| yaw_fraction (eye-lattice tilt) | 0.4 | Zhao-type eye map of *Eristalis* (WP2 CT) |

## 5. Code

| Module | Stage | Status |
|---|---|---|
| `hover/eye.py` | 0 | done: sphere eye maps for *Drosophila* and *Eristalis* ♀/♂, local axes, virtual-neighbour sampling, patches |
| `hover/hrbl.py` | 1–2 | done: Ammer 2023 detectors and six-unit local circuit, blocking conditions, membrane |
| `hover/lptc.py` | 3 | done: receptive-field maps (incl. Nordström ♀/♂ HSN), RF-weighted conductances |
| `hover/tier1_hh.py` | 4 | done: MESH Tier-1 port; conductance drive with reversal potentials; leak scale; VS→MOS weight |
| `hover/oculomotor.py` | 5 | done: frames (holder ↔ model), pulls, vector sum, preferred-direction helper |
| `hover/species.py` | 6 | done: `Model(species, sex, mio_from, mio_pull, …)`, bias calibration, `run(movie)` |
| `hover/validate_falt.py` | 3 | done: direction tuning, β fit, report, validation figure |
| `hover/adversarial.py` | 7 | done: parametric (1+λ)-ES on the rate surrogate, Tier-1 verification, female prediction, Fig. B1g panel |
| `hover/frontend_ad.py` | 7 | done: autograd re-implementation of Stages 0–3 for pixel-level gradient descent (ALIstim-style) |
| `hover/mio_search.py` | 7 | superseded (first-generation front end; kept for the record) |

Run times (4 cores): eye maps 0.3–1.7 s; one stimulus through the front end 1–2 s (*Eristalis*);
Tier-1 1.5 s of simulated time ≈ 0.3 s; the 12-direction validation ≈ 1 min; the ES search ≈ 10 min.

## 6. Readout: pseudopupil, hovering, or both?

The circuit model predicts, per stimulus, the retinal-shift vector of each hypothesis. The
experiment that tests it with the fewest assumptions is therefore the one Falt *et al.* used:
deep-pseudopupil (DPP) tracking of the retina in the tethered animal, with EMG of the three muscles
where possible. This is the primary readout of WP2 and the quantity the controversial stimuli are
optimised for. Hovering and gaze stabilisation in flight are the *function* we attribute to the
pathway, but they are read out through descending neurons and the wing motor, where the hoverfly's
optomotor behaviour is sexually monomorphic; as a test of the MIO hypotheses they would add
unknowns rather than remove them. We therefore use tethered flight (wingbeat amplitude, head yaw)
as the secondary readout, to ask whether the dimorphic channel reaches flight control at all, and the
SpikerBot/quadrotor as the embodiment: the same circuits, the same stimuli, the robot's heading
stabilisation as the behaviour. That embodiment can start now (the circuits exist), and it is what
the proposal promises in WP4.

## 7. What I still need from you

1. From the CT: the two candidate MIO pull directions you consider anatomically plausible (the
   search currently contrasts an anterior/medial pull with a dorsal pull), and the MOS/MOT pull
   directions in *Eristalis* if they differ from *Drosophila*.
2. Any hoverfly HS/HSNE tuning curves beyond Nordström 2008 (your own recordings, if they exist),
   and your preferred bright-zone parameters (centre, extent, Δφ) from Straw 2006 or your CT.
3. Your decision on the readout (§6; recommended: retinal trajectory primary, tethered flight
   secondary, robot embodiment).
4. Whether you want the Falt methods typo (§2) raised with the co-authors before the preprint is
   cited in the proposal.
