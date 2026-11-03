# Part A: budget table and Resources text

> The numbers are **placeholders for sizing**. Replace them with the real personnel cost rates of IU,
> the MPG and LMU, and with quotes. `tools/check_limits.py` sums the table below (per beneficiary and
> in total) and checks the €2.0 M cap and the 8000-character Resources limit. In the online form, each
> beneficiary has its own budget section, and the table prevails over the text (IfA p. 25, 29).

## Beneficiaries

| Beneficiary | Role | Team members hosted |
|---|---|---|
| **IU Internationale Hochschule** (host institution) | PI; modelling, computer vision, citizen science | PI, Postdoc 1, Postdoc 2, PhD 1, PhD 3, student assistants |
| **Max-Planck-Gesellschaft**: MPI for Biological Intelligence, Active Sensing (L. Fenk) | *Eristalis* and *Drosophila* physiology (WP2) | PhD 2 |
| **LMU München**: Evolutionary Biology (R. Merrill) *[confirm unit]* | Developmental and genetic origin of the third muscle (WP2, T2.5) | PhD 4 |

Additional beneficiaries are allowed when they add scientific value (IfA p. 24, fn 48). Their
participation and its extra cost must be justified in Resources (IfA p. 30).

## Budget table (whole euros)

The 25 % indirect rate (E) applies to A + C, not to B or D (IfA p. 29).

```budget-csv
beneficiary,category,item,amount
IU,A,PI (salary paid by IU; not charged),0
IU,A,Postdoc 1 computational neuroscience (48 PM),330000
IU,A,Postdoc 2 neuromorphic computer vision (24 PM),165000
IU,A,PhD 1 connectomics/ML (48 PM),190000
IU,A,PhD 3 spiking networks for vision (48 PM),190000
IU,A,Other personnel: student assistants (course and robot-zoo support; proofreading),30000
IU,C.1,Travel and subsistence,25000
IU,C.2,Equipment (depreciation): 2 event cameras + piezo/galvo micro-movement stage,40000
IU,C.2,Equipment (depreciation): GPU server,45000
IU,C.3,Robot kits for courses and robot zoo (IU procurement; hardware-neutral spec),20000
IU,C.3,Open-access publication fees (fully OA venues),20000
IU,C.3,Dissemination and citizen-science events,5000
IU,C.3,Neuromorphic hardware access and cloud compute,5000
IU,C.3,Other additional direct costs: certificate on the financial statements,5000
MPG,A,PhD 2 hoverfly physiology (48 PM),190000
MPG,C.1,Travel and subsistence,10000
MPG,C.2,Equipment (depreciation): IR high-speed camera + optics for retinal tracking,55000
MPG,C.3,Consumables: Eristalis and Drosophila rearing; electrodes; dyes,25000
LMU,A,PhD 4 evolutionary developmental genetics (48 PM),190000
LMU,C.1,Travel and subsistence,5000
LMU,C.3,Consumables and services: RNA-seq time series; in situ HCR probes; library prep,55000
```

Additional funding (up to €1 M): not requested. Consider it only if a cost is necessary for the work
and cannot fit under the cap. It must be justified as such.

*Trade-off made here:* no separate outreach engineer. WP5 runs through the PI's courses and student
assistants. If you prefer the engineer (50 %, ≈ €110k), drop Postdoc 2 instead.

## Resources text (form field, max 8000 characters incl. spaces)

<!-- RESOURCES START -->
HOVER requests EUR 2,000,000 for 60 months: EUR 1,600,000 direct costs and EUR 400,000 indirect costs (25 % flat rate). No additional funding is requested. HOVER is a single-PI project with three beneficiaries. IU Internationale Hochschule is the host institution (EUR 1,337,500). Two partner institutions each host one doctoral researcher of the PI's team, where the required expertise and infrastructure exist: the Max Planck Society (MPI for Biological Intelligence, EUR 350,000) and LMU Munich (EUR 312,500).

A. Personnel (EUR 1,285,000). The PI devotes 50 % of working time to HOVER, above the 40 % minimum. The PI's salary is paid by IU and is not charged to the grant.
At IU: Postdoc 1, computational neuroscience (48 person-months, EUR 330,000), leads the Tier 1-3 models (WP1) and the theory (WP3). Postdoc 2, neuromorphic computer vision (24 PM from M25, EUR 165,000), builds the motif networks and benchmarks (WP4). PhD 1 (48 PM, EUR 190,000) scales MESH and builds the gap-junction classifier (WP1). PhD 3 (48 PM, EUR 190,000) develops event-based spiking vision and the active event camera (WP4). Student assistants (EUR 30,000) support EM proofreading, teaching kits and the robot-zoo experiment (WP5), which otherwise runs through the PI's computer-vision courses.
At MPI for Biological Intelligence (Active Sensing group, L. Fenk): PhD 2 (48 PM, EUR 190,000) performs the Eristalis and Drosophila experiments of WP2: retinal tracking, EMG of the three retinal muscles, neurobiotin fills and controversial-stimulus experiments. This group has the only established retinal-muscle physiology set-ups and protocols; building them at IU would cost more and take longer.
At LMU Munich (R. Merrill): PhD 4 (48 PM, EUR 190,000) studies the developmental and genetic origin of the male-only third muscle (T2.5). This lab provides genomics and transcriptomics expertise and infrastructure not available at IU.
All team members are selected and supervised by the PI. Partner-group leaders act as local co-supervisors. Costs follow each institution's personnel cost rates [confirm].

C.1 Travel (EUR 40,000): exchange between the three sites (about monthly team meetings in Munich), conferences for team members (about 2 per year), and visits to neuromorphic-hardware providers. The Step 2 interview is remote and costs nothing.

C.2 Equipment (EUR 140,000, depreciation according to each beneficiary's accounting rules):
two event cameras with a piezo/galvo micro-movement stage (IU, EUR 40,000), used continuously from M18 for WP4;
a GPU server (IU, EUR 45,000) for connectome-constrained network training and simulation (WP1, WP3, WP4);
an infrared high-speed camera with optics for retinal tracking (MPG, EUR 55,000), used in WP2 about 70 % of its time.

C.3 Other goods, works and services (EUR 135,000):
RNA-seq of a male/female developmental time series, in situ HCR probes and library preparation (LMU, EUR 55,000);
consumables for hoverfly and Drosophila rearing, electrodes and dyes (MPG, EUR 25,000);
robot kits for IU courses and the robot zoo (IU, EUR 20,000), bought by IU procurement against a hardware-neutral specification;
open-access fees in fully open-access venues (EUR 20,000);
dissemination and citizen-science events (EUR 5,000);
neuromorphic hardware access and cloud compute (EUR 5,000);
a certificate on the financial statements for IU (EUR 5,000).

Existing resources not charged to the grant: IU computer-vision laboratory and computing resources [confirm]; set-ups for two-photon imaging, electrophysiology and micro-CT access at MPI for Biological Intelligence; genomics infrastructure at LMU; the open FlyWire connectome and the MESH software.

Conflict of interest: the PI holds a [role] at Backyard Brains, the manufacturer of SpikerBot. IU procurement selects robot hardware without the PI's involvement, and all HOVER software is released openly and runs on at least one open-hardware platform. [If Backyard Brains contributes robots in kind, state the value here.]
<!-- RESOURCES END -->
