# Part A: budget table and Resources text

> The numbers are **placeholders for sizing**. Replace them with the real personnel cost rates of IU,
> the MPG and LMU, and with quotes. `tools/check_limits.py` sums the table below (per beneficiary and
> in total) and checks the €2.0 M cap and the 8000-character Resources limit. In the online form, each
> beneficiary has its own budget section, and the table prevails over the text (IfA p. 25, 29).
> Team structure decided on 3 Nov 2026: a 36-month postdoc at MPI-BI, a PhD at LMU, and at IU one
> postdoc, two PhD students and a part-time research engineer instead of a second postdoc.

## Beneficiaries

| Beneficiary | Role | Team members hosted |
|---|---|---|
| **IU Internationale Hochschule** (host institution) | PI; modelling, theory, active event-based vision, robots, teaching and citizen science | PI, Postdoc 1, PhD 1, PhD 2, research engineer, student assistants |
| **Max-Planck-Gesellschaft**: MPI for Biological Intelligence, Active Sensing (L. Fenk) | *Eristalis* physiology (WP2, T2.3–T2.4) | Postdoc 2 (36 months) |
| **LMU München**: Evolutionary Biology (R. Merrill) *[confirm unit]* | Developmental and genetic origin of the MIO (WP2, T2.5) | PhD 3 |

Additional beneficiaries are allowed when they add scientific value (IfA p. 24, fn 48). Their
participation and its extra cost must be justified in Resources (IfA p. 30). Personnel costs cannot
be covered by the additional-funding option, so the whole team must fit under the €2.0 M cap.

## Budget table (whole euros)

The 25 % indirect rate (E) applies to A + C, not to B or D (IfA p. 29).

```budget-csv
beneficiary,category,item,amount
IU,A,PI (salary paid by IU; not charged),0
IU,A,Postdoc 1 computational neuroscience and SNN theory (48 PM),330000
IU,A,PhD 1 connectomics and machine learning (48 PM),190000
IU,A,PhD 2 event-based spiking vision and neuromorphic hardware (48 PM),190000
IU,A,Research engineer neuromorphic robotics (50 %; 36 PM; M13-48),110000
IU,A,Other personnel: student assistants (courses; robot zoo; proofreading),30000
IU,C.1,Travel and subsistence,25000
IU,C.2,Equipment (depreciation): active event-camera head (2 event cameras; piezo tip-tilt stage; gimbal; motion platform),40000
IU,C.2,Equipment (depreciation): indoor event-camera quadrotor with neuromorphic processor; netted motion-capture arena,30000
IU,C.2,Equipment (depreciation): GPU server,25000
IU,C.3,Two-wheeled camera robots for courses and the robot zoo (IU procurement; hardware-neutral spec),20000
IU,C.3,Open-access publication fees (fully OA venues),15000
IU,C.3,Dissemination and citizen-science events,5000
IU,C.3,Neuromorphic hardware access and cloud compute,5000
IU,C.3,Other additional direct costs: certificate on the financial statements,5000
MPG,A,Postdoc 2 hoverfly physiology (36 PM; M7-42),255000
MPG,C.1,Travel and subsistence,8000
MPG,C.2,Equipment (depreciation): IR high-speed cameras and optics for retinal tracking and EMG,45000
MPG,C.3,Consumables: Eristalis and Drosophila rearing; electrodes; dyes,25000
LMU,A,PhD 3 evolutionary developmental genetics (48 PM),190000
LMU,C.1,Travel and subsistence,5000
LMU,C.3,Consumables and services: RNA-seq time series; HCR probes; library preparation; micro-CT,50000
```

Additional funding (up to €1 M): not requested. It may only cover major equipment, access to large
facilities or major experimental and field-work costs, not personnel. Consider it only if the
quadrotor arena or tomography beamtime turns out to need it.

## Resources text (form field, max 8000 characters incl. spaces)

<!-- RESOURCES START -->
HOVER requests EUR 1,997,500 for 60 months: EUR 1,598,000 direct costs and EUR 399,500 indirect costs (25 % flat rate). No additional funding is requested. HOVER is a single-PI project with three beneficiaries. IU Internationale Hochschule is the host institution (EUR 1,275,000). Two partner institutions each host one member of the PI's team where the required expertise and infrastructure exist and cannot be built at IU within the project: the Max Planck Society (MPI for Biological Intelligence, EUR 416,250) and LMU Munich (EUR 306,250).

A. Personnel (EUR 1,295,000). The PI devotes 50 % of working time to HOVER, above the 40 % minimum. The PI's salary is paid by IU and is not charged to the grant.
At IU: Postdoc 1, computational neuroscience and spiking-network theory (48 person-months, EUR 330,000), leads the Tier 1-3 models (WP1) and the theory (WP3). PhD 1 (48 PM, EUR 190,000) scales MESH, builds the electrical-synapse classifier and the Tier-1/Tier-2 models (WP1). PhD 2 (48 PM, EUR 190,000) develops event-based spiking vision, the hardware deployment and the benchmarks (WP4). A research engineer in neuromorphic robotics (50 %, 36 PM, M13-48, EUR 110,000) builds and maintains the active event-camera head, the indoor quadrotor and the robot fleet (WP4, WP5). Student assistants (EUR 30,000) support EM proofreading, teaching kits and the robot-zoo experiment (WP5), which otherwise runs through the PI's computer-vision courses.
At MPI for Biological Intelligence (Active Sensing group, L. Fenk): Postdoc 2 (36 PM, M7-42, EUR 255,000) performs the Eristalis experiments of WP2: retinal tracking, electromyography of the three retinal muscles, intracellular recordings and neurobiotin fills, and the controversial-stimulus experiments. A postdoc rather than a PhD student is requested because physiology in a non-genetic insect requires established electrophysiology skills. This group has the only established retinal-muscle physiology set-ups and protocols; building them at IU would cost more and take longer.
At LMU Munich (R. Merrill): PhD 3 (48 PM, EUR 190,000) studies the developmental and genetic origin of the male-only third retinal muscle (T2.5). This group provides genomics and developmental-genetics expertise and infrastructure for non-model insects that IU does not have.
All team members are selected and supervised by the PI. Partner-group leaders act as local co-supervisors. Costs follow each institution's personnel cost rates [confirm].

C.1 Travel (EUR 38,000): exchange between the three sites (about monthly team meetings in Munich), conferences for team members (about two per year), and visits to neuromorphic-hardware and event-camera providers. The Step 2 interview is remote.

C.2 Equipment (EUR 140,000, depreciation according to each beneficiary's accounting rules):
the active event-camera head (two event cameras, a piezo tip-tilt stage, a gimbal and a motion platform; IU, EUR 40,000), used continuously from M13 for WP4;
an indoor event-camera quadrotor with an on-board neuromorphic processor and a netted motion-capture arena (IU, EUR 30,000) for the closed-loop benchmark of WP4;
a GPU server (IU, EUR 25,000) for connectome-constrained network training and simulation (WP1, WP3, WP4), complemented by cloud and EBRAINS resources;
infrared high-speed cameras and optics for retinal tracking and electromyography (MPG, EUR 45,000), used in WP2 about 70 % of the time.

C.3 Other goods, works and services (EUR 125,000):
RNA-seq of a male/female developmental time series, in situ HCR probes, library preparation and micro-CT (LMU, EUR 50,000);
consumables for hoverfly and Drosophila rearing, electrodes and dyes (MPG, EUR 25,000);
two-wheeled camera robots for IU courses and the robot zoo (IU, EUR 20,000), bought by IU procurement against a hardware-neutral specification;
open-access fees in fully open-access venues (EUR 15,000);
dissemination and citizen-science events (EUR 5,000);
neuromorphic hardware access and cloud compute (EUR 5,000);
a certificate on the financial statements for IU (EUR 5,000).

Existing resources not charged to the grant: IU computer-vision laboratory and computing resources [confirm]; set-ups for two-photon imaging, electrophysiology, retinal tracking and micro-CT access at MPI for Biological Intelligence; genomics infrastructure at LMU; the open FlyWire and male CNS connectomes and the MESH software; neuromorphic hardware through EBRAINS and vendor research programmes.

Conflict of interest: the PI holds a senior role at Backyard Brains, the manufacturer of one of the candidate classroom robots. IU procurement selects robot hardware without the PI's involvement, the quadrotor and the active head use unrelated vendors, and all HOVER software is released openly and runs on at least one open-hardware platform. [If Backyard Brains contributes robots in kind, state the value here.]
<!-- RESOURCES END -->
