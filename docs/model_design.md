# HOVER model v0: from the eye to the eye movement, three circuits, one stimulus engine

Status 10 Nov 2026. This document fixes the architecture of the computational model that underlies
WP1–WP3 and the preliminary results in B2, answers the question "does the whole set-up make sense",
records what the first implementation reproduces, and lists what is fixed by data, what is a free
parameter, and what still has to be supplied. Code: `code/hover/` (see §5).

**Update 10 Nov.** Four decisions since the first version: (i) the HS–HS and VS–VS junctions are
restored to their MESH strength (§1, Stage 4); (ii) hypothesis H2 is sharpened to one direction: the
MIO is a median muscle that pulls both retinae toward the midline (§3d, §3e); (iii) the hoverfly
model has two eyes (§3f); (iv) the controversial stimulus contrasts male with female (§3f, Fig. B1g).
The direction scan of §3c remains as the check of the assumed direction.

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

## 3b. Controversial stimuli for the male hoverfly (Stage 7 results)

Hypotheses: MIO pull anterior (0°) vs dorsal (90°), MIO driven by HSN (`w_mio` = 3). Objective:
angle between the predicted retinal-shift vectors × min(1, ΔMIO/10 Hz) × min(1, |shift|/0.15).

| Engine | stimulus | MIO / MOT / MOS Δrate | shift directions (anterior, dorsal) | female | run time |
|---|---|---|---|---|---|
| parametric (1+5)-ES on the rate surrogate, Tier-1 verified (`hover/adversarial.py`) | full-contrast grating patch, centre (3°, 24°), radius 25°, direction 23°, 38°/s, on a faint (0.3) background moving at 218°, 23°/s, plus a weak lateral patch | +12.6 / +6.2 / +7.9 Hz | 175°, 124° (51° apart) | 169° | 2 min |
| pixel-level gradient descent, autograd through Stages 0–3 (`hover/adversarial_pixel.py`, 40 Adam steps on 20 × 14 × 18 control points) | high-contrast blotch pattern, strongest over the HSN field | +9.1 / +1.8 / −3.0 Hz | 202°, 85° (117° apart) | 302° | 3 min |

The parametric stimulus is the experiment-ready one (Fig. B1g): it separates the two MIO hypotheses
by 51° with retinal shifts of normal size, while the female circuit predicts a direction close to the
"anterior" hypothesis, so a second objective (male vs female) is needed to separate those two; the
engine supports it (`objective_from_rates` with any pair of models). The pixel-optimised stimulus
shows the ALIstim-type capability on the full pipeline: it nulls MOT and MOS almost completely and
reaches a 117° separation, at the price of small absolute shifts (magnitudes 0.05–0.08 vs 0.16–0.21).
Both results are stored next to the code (`adversarial_result.json`, `adversarial_pixel_result.json`).

## 3c. The MIO pull direction on the full circle (12 hypotheses, `hover/mio_ring.py`)

The MIO is a fan-shaped muscle (§3d), so no single fibre orientation gives its pull. The model
therefore treats the pull direction θ as free on the whole circle, in 12 steps of 30°. With the
common MOT/MOS term c and the MIO weight w, the predicted retinal shift under hypothesis k is
v_k = c + w·u(θ_k). The 12 predictions can only be told apart if the stimulus isolates the MIO:
for ρ = |c|/|w| < 1 the predicted directions wind once around the circle, and for ρ → 0 the measured
shift direction *is* the pull direction. The design goal changes from "largest angle between two
hypotheses" to "smallest ρ at a sufficient MIO drive".

| Stimulus | ΔMIO / ΔMOT / ΔMOS (Hz) | ρ | smallest separation of neighbouring hypotheses (ideal 30°) | largest error of "shift = pull" |
|---|---|---|---|---|
| pairwise, parametric (the earlier Fig. B1g stimulus) | +9.9 / +6.7 / +8.7 | 1.09 | 1° | 104° |
| pairwise, pixel (§3b) | +6.2 / +1.9 / −2.9 | 0.56 | 19° | 34° |
| MIO-isolating, parametric | +7.8 / +4.6 / +1.0 | 0.59 | – | – |
| **MIO-isolating, pixel** (30 Adam steps from the pairwise pixel solution) | +7.2 / +2.6 / +1.3 | **0.40** | **22°** | **23°** |

(With the HS chain coupling restored. Without it the same searches gave ρ = 0.26 and a largest error
of 15°: the coupling spreads every horizontal-system signal into HSN and from HSN into its
neighbours, so the MIO cannot be driven alone. This is the reason for giving up the direction scan as
the main design and committing to the anatomical direction, §3f.)

All numbers are Tier-1 verifications. With the isolating stimulus one measurement of the retinal-shift
direction reads out θ to within 23°, whatever θ is, and the female circuit hardly moves at all
(shift magnitude 0.01): the stimulus predicts a retinal movement in males only. The scan is kept as
the check of the direction assumed in §3f. Figure: `proposal/figures/fig_mio_ring.png` (not yet used in B2). Result files:
`code/hover/mio_ring_result.json` and `.z.npy`.

Limits of the 12-direction description: it assumes a rigid shift by one muscle with one motor
command. A fan can also (i) be driven in compartments, which would let the nervous system steer the
pull within the fan's angular span, and (ii) gather the retina toward its focus, a non-rigid, radial
deformation that changes the local sampling geometry of the love spot rather than its direction.
The isolating stimulus is the right probe for all three cases because it assumes no direction; the
readout then needs the pseudopupil's shape as well as its position.

## 3d. What the CT images say about the pull direction

Images: male *Eristalis* frontal section (`proposal/figures/src/ct_eristalis_m.jpg`), male
*Melanostoma* and *Sphaerophoria* sagittal renderings (DFG repository,
`271_melanostoma_M_MIO_colored.png`, `297_sphaerophoria_M_MIO.png`, and the two zooms).

- Frontal view (*Eristalis*): the muscle sits at the dorsal midline directly below the cuticular
  septum where the two eyes meet, as an inverted V: apex at the septum, one limb to the dorso-medial
  corner of each circumocular ridge (COR). Both eyes are attached to one median structure.
- Sagittal views (*Melanostoma*, *Sphaerophoria*): the muscle is elongated along the eye junction
  beneath the frons, between antennae and ocellar triangle. Its fibres are radial: they converge on a
  focus at the inner edge and fan out to the outer margin along the junction, with a larger lobe
  toward the vertex and a smaller one toward the antennae (*Melanostoma*: focus at about one third of
  the length from the antennal end; *Sphaerophoria*: nearly central, bow-tie shaped).

Reading. (1) Robust: each limb pulls its retina toward the median plane. In the eye's own
frame that is "anterior" (0°; medial), and it is mirror-symmetric in the two eyes. (2) The fan adds a
component along the eye junction whose sign the images cannot settle, because it depends on which end
is the fixed origin (septum) and which the movable insertion (COR), and on the lobe asymmetry:
dorsal if the focus is the insertion, ventral if it is the origin. (3) Part of the action may be
along the ommatidial axes, which changes focus rather than gaze. Anatomical prior on the ring: the
half-circle facing the midline (270° → 0° → 90°), centred on 0°.

Functional prior. If HSN drives the MIO as HS cells drive MOT, the reflex is compensatory only when
the pull is opposite to HSN's local preferred direction (as MOT: PD 141°, pull 320°). The male HSN
field sits where the local +h axis is tilted upward (§1, Stage 0), so its PD is front-to-back and up
(≈ 140–150°) and the compensatory pull is ≈ 320–330°: anterior with a ventral component. Both priors
agree on the medial half-circle; the best single estimate is 330° ± 40°, and "dorsal" (90°), one of
the two hypotheses of Fig. B1g, is the less likely one.

## 3e. Hypothesis H2, sharpened: the MIO is a vergence muscle (binocular command, depth)

Because one median muscle attaches to both CORs, its contraction shifts both retinae toward the
midline. Photoreceptors sample inverted images (Falt *et al.*), so the lines of sight of the two love
spots rotate apart on contraction and together on relaxation: the MIO changes the **vergence** of the
two acute zones, something MOS and MOT can only do by coordinated commands to four muscles
(Fenk *et al.* 2022 [7] report such vergence movements in *Drosophila* during gap crossing).

- Sign check. A target approaching on the midline moves back-to-front in both HSN fields; HSN
  hyperpolarises, the MIO relaxes, both retinae move laterally and the lines of sight converge on the
  target. A receding target does the opposite. An HSN-driven, medially pulling MIO is therefore a
  negative-feedback vergence reflex of the love spots.
- Depth. Disparity ≈ b/d for an interocular baseline b of the two bright zones [b to be measured;
  1–3 mm assumed]: 0.6–1.7° at 10 cm, 0.3–0.9° at 20 cm, 0.1–0.3° at 50 cm. With Δφ ≈ 1° the
  vergence state carries range within about 10–20 cm, further if timing is used: mirror-symmetric
  movements sweep a target over corresponding receptors of the two eyes with a time difference
  proportional to disparity (the principle shown for photoreceptor microsaccades by Kemppainen
  *et al.* 2022 [52]). Male hoverflies launch interceptions without measuring range, assuming a
  conspecific of standard size and speed (Collett & Land 1978 [72]); a vergence signal would supply
  range in the terminal phase.
- Efference copy. By the electrical coupling of Falt *et al.*, the MIO command flows back into HSN
  on both sides: a range-related signal inside the visual system (extends H2c).
- Predictions that separate "one median vergence muscle" from "two independent third muscles":
  (i) binocular expansion or contraction confined to the two HSN fields moves both retinae
  mirror-symmetrically; binocular rotation moves them in opposite senses if the halves are
  independent and not at all if one command sums both HSNs; (ii) both pseudopupils recorded at once;
  (iii) number of motor axons and whether the two limbs are separate bellies (µCT, backfills);
  (iv) HSN membrane potential co-varies with spontaneous MIO activity.
- Model. Built in §3f (mirrored left eye, the MIO as one actuator on both eyes, version and vergence
  readout); the stimulus geometry of real targets at a given distance is not yet included.
- Machine vision (H4g in B2). Two event cameras with mirror-symmetric micro-vergence: depth of
  static scenes from inter-ocular event timing, decoded by coincidence-detecting spiking units.

## 3f. Two eyes: the bilateral model and the male-versus-female stimulus (`hover/binocular.py`, `hover/binocular_search.py`)

Geometry. Stimuli are defined in head-centred coordinates (azimuth ψ positive to the animal's right).
The right eye sees ψ ∈ [−20°, 165°] at its own azimuth az = ψ, the left eye ψ ∈ [−165°, 20°] at
az = −ψ, so one right-eye front end serves both eyes with a mirrored movie. Each eye can be given its
own movie (dichoptic stimulation). The Tier-1 network is duplicated (suffixes _R, _L). The MIO is
either **one motor neuron** coupled to HSN of both sides (H2; half the junction conductance per side,
so the total equals that of one independent neuron) or **two motor neurons**, one per side. Pull
directions: MOS 51°, MOT 320° in each eye's own frame, MIO 0° (toward the midline). Readout per eye:
anterior/medial component a and dorsal component d of the retinal shift; "medial" = (a_R + a_L)/2
(both retinae toward the midline; the lines of sight diverge), "version" = (a_R − a_L)/2 (conjugate
shift toward the animal's left). Not included: heterolateral LPTC input (H1, H2, Hu) and the disparity
geometry of real targets.

A consequence of the anatomy of the receptive fields: the male HSN fields of the two eyes are centred
on the midline and overlap almost completely. Conjugate motion in this zone drives the two HSNs in
opposite directions; they are driven together only by motion that differs between the eyes (a change
of disparity, i.e. motion in depth), by upward motion (the local +h axes of the two eyes are mirror
images and both tilt upward there) and, through the HS chain, by mirror-symmetric motion of the
surround.

Predictions for five stimuli (medial / version / ΔMIO in Hz; two-command model: left / right):

| Stimulus | male, one command (H2) | male, two commands | female |
|---|---|---|---|
| yaw rotation (full field) | +0.15 / +0.18 / +5.5 | +0.14 / +0.28 / -6.3 / +15.8 | +0.10 / +0.19 / – |
| expansion (full field) | +0.37 / +0.00 / +12.5 | +0.36 / +0.00 / +12.1 / +12.1 | +0.27 / +0.00 / – |
| frontal patch, conjugate drift to the right | +0.05 / +0.04 / +3.0 | +0.05 / +0.08 / -1.6 / +7.6 | +0.02 / +0.03 / – |
| frontal patch, receding in depth | +0.13 / +0.00 / +7.5 | +0.13 / +0.00 / +7.1 / +7.6 | +0.05 / +0.00 / – |
| frontal patch, approaching in depth | -0.03 / +0.00 / -1.9 | -0.02 / +0.00 / -1.6 / -1.3 | -0.02 / +0.00 / – |

Reading: the sexes differ in the medial component whenever the horizontal system is driven
symmetrically; one command and two commands differ in the conjugate response to conjugate motion
(two commands double it and split the MIO rates). Approaching patterns hardly drive the model, a
consequence of the weak null-direction responses of the conductance model that WP2 recordings will
have to check.

Controversial stimulus, male against female. Both sexes see the same binocular stimulus (two
half-field backgrounds, two patches, each patch with a conjugate and an optional disparity drift;
19 parameters). Objective: |shift_male − shift_female| − |shift_female| over the four shift
components, i.e. the largest sex difference with the female at rest; (1+6) evolution strategy with
sparse mutations, 30 generations, every evaluation on the full Tier-1 network of both sexes.

- **Dichoptic** (Fig. B1g; `binocular_result.json`): a frontal patch (ψ 0°, elevation 26°, radius
  22°) whose pattern drifts at 33°/s in opposite directions in the two eyes (front-to-back in both: it
  recedes in depth), on a surround that contracts and drifts upward (contrast 0.5), plus a weaker
  patch below it. male: medial +0.090, MIO +7.1 Hz, MOT +3.2/+2.5, MOS +0.1/+1.2 Hz (left/right); female: medial +0.005, MOT +1.6/+0.6, MOS -1.0/-0.1 Hz; difference 0.121, of which 77 % disappears when the MIO is cut.
- **Single display** (`binocular_result_single_screen.json`; panel in
  `proposal/figures/src/fig_binocular_single_screen.png`): the same image for both eyes: an upward
  drifting patch on the midline (ψ 2°, elevation 28°, 44°/s) and a patch left of it drifting toward
  the midline, on the same kind of surround. male: medial +0.085, MIO +6.5 Hz, MOT +2.7/+3.2, MOS +0.6/+0.7 Hz (left/right); female: medial +0.008, MOT +0.9/+1.5, MOS -0.2/-0.0 Hz; difference 0.109, of which 77 % disappears when the MIO is cut. This solution relies on the upward tilt of
  the local lattice axes in the dorso-frontal eye (`yaw_fraction`), which is taken from *Drosophila*
  and unmeasured in *Eristalis*; the dichoptic solution does not.

In both cases the male with two independent MIO commands behaves like the one-command male (the
stimulus is symmetric), so this stimulus tests the sex difference, and the conjugate-motion pair of
the table tests one command against two.

## 4. Free parameters and hypotheses of the hoverfly models

| Parameter | Prior / v0 value | Fixed by |
|---|---|---|
| θ_MIO (pull direction) | H2: 0°, toward the midline (§3d); the 12-direction scan (§3c) is the check | isolating stimulus + DPP tracking of both eyes, EMG, µCT fibre tracing |
| MIO laterality | H2: one command for both limbs; alternative: two independent commands (§3f) | conjugate vs mirror-symmetric motion with two-camera DPP, backfills, µCT |
| MIO action | rigid shift, compartmental steering, or radial deformation | pseudopupil shape and position |
| MIO drive | HSN (H2), HSNE, pooled HS, VS | neurobiotin fills, stimuli optimised on MIO activity |
| HSN ♂ receptive field | Nordström 2008 contours (Gaussian fits above) | WP2 recordings |
| HSNE local PD | +h with an upward component | WP2 recordings |
| LPTC↔RMN conductances | g_lptc_mn 0.5, VS→MOS ×2 (Falt fit), HSN→MIO ×3, junction filter 15 ms | WP1 apposition areas, WP2 fills, EMG |
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
| `hover/mio_ring.py` | 7 | done: 12-direction scan of the MIO pull, MIO-isolating stimulus (ES and pixel gradient), figure |
| `hover/binocular.py` | 4–6 | done: both eyes, bilateral Tier-1 network, median or independent MIO, version/vergence readout |
| `hover/binocular_search.py` | 7 | done: male-versus-female controversial stimulus (dichoptic and single display), Fig. B1g panel |
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

1. For the MIO: which attachment is fixed (septum) and which moves (COR), whether the two limbs are
   separate bellies, and the number of motor axons, if the CT or your dissections show it.
2. How you would present a pattern that moves in depth to a tethered hoverfly (a real target on a
   linear stage, or separate images for the two eyes), and whether the single-display stimulus of
   §3f should be the first experiment instead.
3. The interocular baseline of the two bright zones and their binocular overlap (Straw 2006 or CT),
   for the depth range in §3e, and the local facet-row orientation in the male dorso-frontal eye.
4. Any hoverfly HS/HSNE tuning curves beyond Nordström 2008, in particular null-direction responses,
   and your preferred bright-zone parameters (centre, extent, Δφ).
5. Whether you want the Falt methods typo (§2) raised with the co-authors before the preprint is
   cited in the proposal.
