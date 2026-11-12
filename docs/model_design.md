# HOVER model v0: from the eye to the eye movement, three circuits, one stimulus engine

Status 12 Nov 2026. This document fixes the architecture of the computational model that underlies
WP1–WP3 and the preliminary results of the proposal, records what the implementation reproduces, and
lists what is fixed by data, what is a free parameter, and what still has to be supplied. Code:
`code/hover/` (see §5). Every number quoted in the proposal is in `code/hover/bowl_result.json`,
`code/hover/eventcam_result.json` or `code/hover/results_raw/validate_falt.json`.

**Update 12 Nov: what changed, and why.**

1. *The question is what the third muscle is for.* H2 is no longer "a vergence muscle". It is the
   neutral, testable statement that the muscle is a separate channel for the bright zone, driven by
   motion inside the love spot, with two alternatives (an amplifier of the stabilising reflex; no
   visual drive). Binocular coordination and depth are left to the Fenk laboratory and are not part
   of the proposal; the earlier two-eye vergence analysis is archived (§3g).
2. *Two stimuli instead of one controversial stimulus* (§3b): a matched stimulus that moves male and
   female retinae alike, and a love-spot stimulus that moves them differently. Both are square-wave
   gratings on one bowl-shaped projector display; nothing dichoptic.
3. *The animal in the loop* (§3d): a stimulus search driven by the tracked retinal movement.
4. *A machine-vision result* (§3e): an event-camera simulation in which the sensor movement that
   shows the scene hides a small moving target.
5. *Two corrections of fact.* The male bright zone gathers more light but has no finer lattice
   (Straw *et al.* 2006), so male and female eye maps are now identical in sampling. HSNE exists in
   both sexes (Nordström *et al.* 2008); only HSN is dimorphic. All hoverfly numbers below were
   recomputed after the first correction.

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
   (Zhao *et al.* 2025). The model therefore starts from an eye map on the sphere, specific to the
   species. The male hoverfly's bright zone is not a finer lattice (Straw *et al.* 2006: enlarged
   facets, more light, faster and more contrast-sensitive motion detection, no substantial gain in
   resolution); in the model the sexes differ in the HSN receptive field and in the third muscle,
   and the bright zone's higher contrast sensitivity is a detector property still to be added.
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
  Straw 2006], 4,864 ommatidia, 220 circuits, the same in both sexes (the male bright zone has
  larger facets, not smaller inter-ommatidial angles). Because a hexagonal lattice cannot expand its ring count outward, the realised
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
low-pass-filtered bidirectional gap junctions. Changes for HOVER: (i) conductance drive
g·g_leak with reversal potentials rest + 40 / rest − 20 mV, so that the Tier-1 LPTC reproduces the
Ammer membrane in steady state; (ii) `lptc_leak_scale` = 50: the preset LPTC leak (0.057) is far below
the junction conductances, so the motor neurons would clamp the LPTCs; the real cells are large and
low-impedance, and the scaling makes them stiff graded voltage sources whose coupling onto the RMNs is
set by `g_lptc_mn` (= 0.5) alone; (iii) bias calibration: each RMN's bias current is set so that its
tonic rate at rest is 100 Hz, compensating the tonic junction current (Falt: RMNs operate at an
intermediate activation regime with a bidirectional range); (iv) the LPTC↔RMN junctions carry a
15 ms low-pass filter (C = G·τ) representing the cable distance between junction site and
spike-initiation zone: with the MESH preset (≈ 1.6 ms) the RMN spikes appear as 10 mV spikelets in
the LPTCs, with 15 ms they are 1.5–2 mV and the rate-coded modulation is unchanged. With these
settings a preferred-direction grating modulates MOT by +22/−15 Hz (HS cells) and MOS by +31 Hz
(VS cells); stronger coupling drives the HH neurons into depolarisation block. The male's MIO
receives its single HSN input with a junction three times the HS→MOT conductance (`w_mio` = 3), so
that the three motor neurons have comparable visual modulation; this is a free parameter (§4). (v) The HS–HS and VS–VS junctions scale with the LPTC leak, so that
the MESH ratio of junction to membrane conductance (0.9) is kept: a potential change in HSS reaches
HSE with 0.29 and HSN with 0.08 of its amplitude, HSN reaches HSNE with 0.36 and HSE with 0.30, VS1
reaches VS2 with 0.30 and VS3 with 0.11 (HS and VS cells are electrically coupled [11,32]). An
earlier version of this model kept the junctions at their absolute preset value, which removed the
coupling once the cells were made stiff; all numbers below are with the coupling restored. The
*Drosophila* validation (§3) is unchanged by it, because full-field gratings drive the coupled cells
alike.

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

| Quantity | Falt *et al.* 2026 | model, w_vs_mos = 1 | model, w_vs_mos = 2 | final (w_vs_mos = 2, junction filter 15 ms) |
|---|---|---|---|---|
| MOT PD | 141° | 159° | 149° | 146° |
| MOS PD | 212° | 204° | 210° | 212° |
| MOS − MOT divergence | ≈ 72° | 45° | 61° | 66° |
| MOT − HS | 8° | 4° | 2° | 0° |
| MOS − linear sum (4/7 VS + 3/7 HS) | 6° | 2° | 13° | 16° |
| VS1–4 PD (prediction) | – | 243° | 233° | 233° |
| OKR mean error (inverted shift vs stimulus) | 7.1° | 23° | 20° | 17° |
| fitted β | – | −25.5° | −34.5° | −35° |
| tonic rates MOT / MOS | – | 113 / 124 Hz | 110 / 141 Hz | 109 / 111 Hz |

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

Figure: `proposal/figures/fig_model_validation.png` (eye map with local axes; LPTC tuning; RMN tuning
in the holder frame with Falt's PDs; OKR plot), produced by `python -m hover.validate_falt --wvs 2`.

## 3b. Two stimuli for one bowl display (`hover/bowl.py`)

**Why two.** The sexes differ in two things at once: the HSN receptive field (narrow in males) and
the third muscle. One stimulus cannot say which of the two causes a difference in eye movement. Two
can: a *matched* stimulus on which the model predicts the same retinal movement in both sexes
although their HSN cells differ, and a *love-spot* stimulus on which it predicts the largest
difference. The matched stimulus calibrates each animal (gain of the shared reflex, quality of the
tracking) and tests the homology assumption; the love-spot stimulus tests the muscle. Cutting the
muscle in the model (the same simulation with the muscle's mechanical term removed) says how much of
a difference the muscle carries and how much the narrowed HSN.

**Display.** One bowl-shaped projection screen in front of the tethered animal (Prech, Groschner &
Borst 2024: about 180° × 125°; 60 Hz image refresh in the published version, faster projectors
possible [verify with the set-up]). In the model the screen covers azimuth ±90° and elevation −52° to
+73°; outside it the field is uniform and static. Both eyes see the same head-centred movie.

**Stimulus family.** Drifting square-wave gratings (wavelength 20°, 30°/s, full contrast, 1 s with
motion onset at 0.25 s; edges are 1° ramps so that sub-pixel drift is smooth), shown on the whole
bowl, only inside a disc at the love spot (centre azimuth 0°, elevation 27°, radius 17°), or
everywhere except in that disc. Directions in head coordinates: 0° toward the animal's right, 90° up.

**Models.** Female; male with the third muscle (one motor neuron per side, coupled to HSN of its
side with `w_mio` = 3, pulling toward the midline); the same male with the muscle cut. Readout: the
retinal movement of both eyes (anterior and dorsal component per eye); "movement" is its length
averaged over the eyes, "difference" the length of the male-minus-female vectors averaged over the
eyes. Units are relative (sum of rate change over baseline rate, times the pull vectors).

| Stimulus | female | male | male, muscle cut | male ÷ female | third-muscle motor neuron |
|---|---|---|---|---|---|
| whole bowl, drift downward | 0.272 | 0.237 | 0.269 | 0.87 (difference 23 % of the movement) | −5.5 Hz |
| whole bowl, drift to the right | 0.261 | 0.411 | 0.256 | 1.57 | +22.9 / −11.7 Hz |
| whole bowl, drift upward | 0.134 | 0.249 | 0.139 | 1.87 | +18.2 Hz |
| **matched: bowl without love spot, downward** | 0.282 | 0.295 | 0.280 | **1.05** (difference 5 %) | +2.1 Hz |
| same with a 12° mask | 0.280 | 0.281 | 0.279 | 1.00 (difference 0.7 %) | +0.3 Hz |
| same with a 22° mask | 0.289 | 0.312 | 0.287 | 1.08 (difference 10 %) | +3.4 Hz |
| **love spot only, upward** | 0.068 | 0.198 | 0.083 | **2.93** | +12.7 Hz on both sides |
| love spot only, to the right | 0.050 | 0.130 | 0.058 | 2.60 | +10.8 / −4.8 Hz |
| love spot only, downward | 0.027 | 0.082 | 0.031 | 3.07 | −6.2 Hz |

Reading. (i) A full-field grating does not match the sexes in any direction: the coupled HS network
carries wide-field motion to HSN and from there to the muscle's motor neuron (your point about the
chain coupling). (ii) Sparing the love spot matches them for downward drift; the residual depends on
the mask because two effects balance, null-direction inhibition inside the HSN field and excitation
arriving through the chain, and a 12° mask balances them almost exactly. For the proposal the
17° aperture is used for both stimuli (5 %), and the 12° result is quoted as the best case. (iii)
Inside the love spot the male moves 2.4–3.1 times as far as the female in every direction; upward
drift gives the largest absolute difference and is symmetric for the two eyes. The narrowed HSN
alone, with the muscle cut, gives 1.22: 88 % of the difference is the muscle. (iv) *Position map*: a
12° patch drifting upward, at 204 positions of the display, separates the sexes only at the love
spot (peak difference 0.090 at azimuth 0°, elevation 25°; half-maximum within ±10° and 15–35°; 37
times the median of the display; 19 of 204 positions above a tenth of the peak).

Commands: `python -m hover.bowl --scan --map --map-dir 90`, `--apertures`, then `--collect`.

## 3c. What drives the muscle: three answers from two stimuli

The same two stimuli were run with the muscle driven by other cells (`--mio-from`). Male ÷ female:

| Third muscle driven by | matched | love spot | whole bowl, to the right | reading |
|---|---|---|---|---|
| HSN (H2) | 1.05 | 2.93 | 1.57 | a channel for the bright zone |
| HSNE | 1.00 | 2.12 | 1.79 | same class; separated from HSN by fills and direction tuning |
| all HS cells, pooled | 1.20 | 2.47 | 1.91 | same class, with a wide-field component |
| VS cells, pooled | 1.91 | 1.27 | 1.11 | an amplifier of the (vertical) stabilising reflex |
| no visual drive | 0.99 | 1.23 | 1.00 | spontaneous use only; the 1.23 is the narrowed HSN |

So the pattern (matched ≈ 1, love spot ≫ 1) identifies a horizontal-cell drive; the reverse pattern a
vertical-cell drive; (≈ 1, ≈ 1.2) no visual drive. Within the horizontal class the three variants
differ on full-field horizontal motion (1.6, 1.8, 1.9) and in where on the display the difference
arises, which is what fills, the muscle's direction tuning and the position map then decide. The
pull direction is not needed for this table; it is read from the direction of the male's extra
movement (twelve candidate directions, §3g).

## 3d. The animal in the loop (`hover.bowl.closed_loop`)

A search that reads only the retinal movement. Each trial shows one grating patch (six parameters:
azimuth, elevation, radius, drift direction, speed, wavelength) and reads the movement of both
retinae with Gaussian noise on each of the four components. Objective: the part of the movement that
the model *without* the third muscle does not explain (distance to the prediction of the male model
with the muscle cut). Optimiser: a (3, 8) evolution strategy with step sizes shrinking by 7 % per
generation; nine presentations per generation including one of the current mean.

In silico test. The "animal" is a male model whose HSN field, and with it the drive of the muscle,
lies 20° higher than the designer's model assumes (elevation 45° instead of 25°) and whose muscle
pulls at 330° instead of 0°. The search starts from the love-spot stimulus designed with the model.

| Run | noise (s.d. per component; share of the initial effect) | muscle-specific movement: start → after ≈100 → after 181 presentations | final patch |
|---|---|---|---|
| seed 0 | 0.02 (15 %) | 0.133 → 0.173 (+30 %) → 0.182 (+37 %) | elevation 42°, radius 28° |
| seed 0 | 0.05 (38 %) | 0.133 → 0.176 (+33 %) → 0.175 (+32 %) | elevation 41°, radius 26° |
| seed 1 | 0.05 | 0.133 → 0.157 (+18 %) → 0.167 (+26 %) | elevation 30°, radius 29° |
| seed 2 | 0.05 | 0.133 → 0.171 (+28 %) → 0.170 (+28 %) | elevation 37°, radius 27° |
| arbitrary start (azimuth 40°, elevation 0°), animal as the model assumes | 0.02 | 0.003 → 0.018 → 0.036 (the designed stimulus gives 0.118) | not converged |

Reading. From the model's stimulus, every run improves the stimulus within about 100 presentations
(at 3 s per trial, five minutes) by enlarging the patch and moving it up to 15° toward the animal's
true love spot. From an arbitrary stimulus the landscape is flat (the difference between the sexes
exists only at the love spot, §3b) and the search finds nothing in 181 presentations. Hence the
division of labour: the model starts the search, the animal finishes it. Limits: one scenario of
mismatch, four runs, a simple optimiser; Bayesian optimisation should do better under noise and is
part of T2.2. The same loop, with a pattern that moves with the tracked retina, gives the
gaze-contingent mode of T2.2c (visual feedback of an eye movement removed, restored or reversed);
that mode is not simulated yet.

## 3e. An event camera with a moving sensor (`hover/eventcam.py`)

The machine-vision counterpart of the question. An event camera reports changes of log intensity, so
on a hovering platform it sees a moving target but not the static scene it must hold position
against. Moving the sensor makes the scene visible and fills the image with events.

Model. Scene: log intensity of a dead-leaves image (occluding discs, radii 3–80 px with density
∝ r⁻³, log-intensity s.d. 0.4) plus 1/f texture (s.d. 0.15), blurred by the lens in the intensity
domain (Gaussian, σ = 0.6 px). Sensor: 128 × 128 pixels; an ON or OFF event whenever the log
intensity of a pixel has changed by its threshold since its last event (0.20 ± 0.03 between pixels);
Poisson noise events (0.03 per pixel and glance). One glance: the sensor sweeps a given distance in
a random direction while a dark disc (2 px, 80 % darker than the background) moves 2 px in another
random direction. Scene task: register the scene between two glances that differ by an unknown
platform drift of up to 6 px (cross-correlation of smoothed event images; success: error below a
quarter of a pixel). Target task: the strongest response of a size-tuned detector with lateral
inhibition (centre minus the largest of eight flanks) lies on the target. 150 scenes per condition.

| Sensor movement (px) | 0 | ¼ | ½ | ¾ | 1 | 1.5 | 2 | 3 | 4 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| scene registered (%) | 0 | 13 | 89 | 89 | 91 | 95 | 98 | 99 | 100 | 99 | 84 | 60 |
| target found (%) | 100 | 100 | 97 | 69 | 44 | 16 | 7 | 3 | 3 | 3 | 7 | 6 |
| target found, 4 px target | 100 | 100 | 100 | 99 | 90 | 75 | 69 | 59 | 57 | 55 | 51 | 36 |
| target found, low contrast (50 % darker) | 97 | 91 | 23 | 4 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | 2 |
| target found, sparse clutter (discs ≥ 8 px) | 100 | 100 | 100 | 79 | 55 | 23 | 11 | 3 | 4 | 1 | 3 | 5 |
| target found, target moving 4 px | 100 | 100 | 100 | 99 | 97 | 55 | 25 | 5 | 4 | 4 | 7 | 8 |
| events per pixel and glance | 0.03 | 0.03 | 0.07 | 0.14 | 0.21 | 0.39 | 0.56 | 0.91 | 1.26 | 1.94 | 2.63 | 3.99 |

Reading. The scene needs a movement of at least half a pixel and is registered best at 2–6 px; a
small moving target is lost beyond about one pixel, earlier if its contrast is low, later if it is
large. A 1-px target at this contrast stays below the sensor's threshold whatever the movement (3 %
even with a still sensor), which is a limit of the sensor, not of the movement. The event count,
the currency of energy on neuromorphic hardware, grows eight-fold from ½ px to 2 px and eighteen-fold
to 4 px. No fixed movement serves both tasks. Two ways out, which are hypotheses H4a and H4b: let the
movement follow the task, or tell self-generated events from the target's with an efference copy
(not simulated yet; with a perfect copy the scene's events could be predicted and removed). The
link to the fly is the question itself: a male hoverfly stabilises with two muscles and pursues
with three, and whether the third muscle is its way out of this conflict is what WP2 and WP3 test.
Limits: one detector and one registration method, synthetic scenes, a linear sweep; WP4 replaces
all three with hardware and benchmarks.

## 3f. What the two stimuli do not decide

- *Where the muscle pulls.* Read from the direction of the male's extra retinal movement on the
  love-spot stimulus; the tomography suggests toward the midline (§3g).
- *One motor command or two.* The love-spot stimulus with vertical drift is mirror-symmetric, so both
  variants predict the same movement. A horizontally drifting patch separates them (the two limbs
  are then driven in opposite directions), as do fills of the motor neuron(s).
- *Small targets.* The male HSN responds to small targets (Nordström *et al.* 2008). The model has
  no small-target pathway yet; T2.1 adds it as a model variant.
- *Speed and contrast sensitivity of the bright zone.* Not in the model (see §0, point 2).

## 3g. Earlier analyses, archived

Computed on 10 November with the uncorrected eye map; results in `code/hover/results_archive/`; none
of them is used in the proposal. The scripts still run.

- *Controversial stimuli for two pull directions, one eye* (`hover/adversarial.py`,
  `adversarial_pixel.py`): a parametric stimulus separated a pull toward 0° from a pull toward 90°
  by 51°; pixel-level gradient descent through the front end reached 117° with smaller movements.
- *Twelve pull directions* (`hover/mio_ring.py`): with the pull direction free on the circle, a
  stimulus that isolates the muscle (ratio of the common MOT/MOS term to the muscle term 0.40)
  lets the twelve predicted directions be told apart with a largest error of 23°.
- *Reading of the tomography*: the muscle is a median fan between the circumocular ridges of both
  eyes; best estimate of the pull 330° ± 40° in each eye's anatomical frame (toward the midline,
  slightly ventral). This remains the prior for the pull direction.
- *Two-eye model with one median command* (`hover/binocular.py`, `binocular_search.py`): rotation
  and expansion tests, and a male-versus-female stimulus search including dichoptic stimuli. Not
  pursued: stimuli are shown on one display, and binocular coordination is not HOVER's topic.

## 4. Free parameters and hypotheses of the hoverfly models

| Parameter | Prior / v0 value | Fixed by |
|---|---|---|
| Third-muscle pull direction | toward the midline (0° in each eye's frame); tomography: 330° ± 40° (§3g) | direction of the male's extra movement on the love-spot stimulus; EMG; µCT fibre tracing |
| Third-muscle motor command | one motor neuron per side (v0); alternative: one for both limbs | horizontally drifting love-spot patch; fills |
| Third-muscle drive | HSN (H2); HSNE, pooled HS, pooled VS, small-target input, none (§3c) | the two stimuli; fills; closed loop |
| Third-muscle action | rigid shift of the retina; alternatives: local or radial deformation | pseudopupil shape and position |
| HSN ♂ receptive field | Nordström 2008 contours (Gaussian fits above) | WP2 recordings |
| HSNE local PD | +h with an upward component | WP2 recordings |
| LPTC↔RMN conductances | g_lptc_mn 0.5, VS→MOS ×2 (Falt fit), HSN→MIO ×3, junction filter 15 ms | WP1 apposition areas, WP2 fills, EMG |
| Bright zone | same lattice as the female (Straw 2006); higher contrast sensitivity and speed not yet modelled | facet maps, WP2 recordings |
| Love-spot aperture | disc at azimuth 0°, elevation 27°, radius 17° | facet maps of the male eye; closed loop |
| Display | 180° × 125°, centred 10° above the horizon | the set-up at the MPI-BI |
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
| `hover/bowl.py` | 7 | done: bowl display, square-wave gratings in apertures, matched and love-spot stimuli, position map, alternative drives, closed-loop search, `--collect` |
| `hover/eventcam.py` | – | done: event-camera simulation (scene registration against small-target detection as a function of the sensor movement) |
| `hover/binocular.py` | 4–6 | done: both eyes, bilateral Tier-1 network, third muscle with one motor neuron per side or one for both |
| `hover/adversarial.py`, `adversarial_pixel.py`, `frontend_ad.py`, `mio_ring.py`, `binocular_search.py` | 7 | archived analyses (§3g); scripts run, results in `results_archive/` |
| `hover/mio_search.py` | 7 | superseded (first-generation front end; kept for the record) |
| `tools/fig_concept.py`, `fig_results.py`, `fig_support.py`, `fig_workplan.py` | – | the five figures of the proposal, drawn at print size from the result files |

Run times (4 cores): eye maps 0.3–1.7 s; one stimulus through the front end 1–2 s (*Eristalis*);
Tier-1 1.5 s of simulated time ≈ 0.3 s; the 12-direction validation ≈ 1 min; one stimulus through both sexes of the two-eye model ≈ 3 s; the direction scan ≈ 2.5 min; the position map ≈ 10 min; one closed-loop run ≈ 10 min; the event-camera simulation ≈ 8 min per condition.

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

1. The display at the MPI-BI: field of view, tilt, refresh rate and resolution of the bowl, and
   whether a 17° disc at the love spot can be masked cleanly. The model assumes 180° × 125°.
2. Where the love spot is in *Eristalis* males (centre and extent from facet maps), and the tracking
   noise you expect for the deep pseudopupil in a hoverfly, to set the noise level of §3d.
3. Whether the third muscle can be reached for electromyography and for section through the dorsal
   cuticle, and whether its two limbs are separate bellies with one or two motor axons.
4. In the male tomography image used in Fig. 1, which red structures are MOS and which are MOT. The
   figure labels only the third muscle by name and the others as "muscles of both sexes".
5. Any hoverfly HS or HSNE tuning curves beyond Nordström 2008, in particular null-direction and
   small-target responses of the male HSN.
6. Whether you want the Falt methods typo (§2) raised with the co-authors before the preprint is
   cited in the proposal.
