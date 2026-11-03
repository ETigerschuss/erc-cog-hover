# Part A: budget table and Resources text

> The numbers are **placeholders for sizing**. Replace them with IU's real personnel cost rates and
> quotes. `tools/check_limits.py` sums the table below and checks the €2.0 M cap and the 8000-character
> Resources limit. In the online form the budget table prevails over the text (IfA p. 29).

## Budget table (whole euros)

The 25 % indirect rate (E) applies to A + C, not to B or D (IfA p. 29).

```budget-csv
category,item,amount
A,PI (salary paid by IU; not charged),0
A,Postdoc 1 computational neuroscience (48 PM),330000
A,Postdoc 2 neuromorphic computer vision (36 PM),245000
A,PhD 1-3 (3 x 48 PM),570000
A,Other personnel: research engineer / outreach coordinator 50% (60 months),110000
A,Other personnel: student assistants,30000
B,Subcontracting,0
C.1,Travel and subsistence,40000
C.2,Equipment (depreciation): 2 event cameras + piezo/galvo micro-movement stage,40000
C.2,Equipment (depreciation): IR high-speed camera + optics for retinal tracking,55000
C.2,Equipment (depreciation): GPU server,45000
C.3,Consumables: fly rearing; electrodes; dyes; EM data handling,35000
C.3,Robot kits for courses and robot zoo (IU procurement; hardware-neutral spec),30000
C.3,Open-access publication fees (fully OA venues),40000
C.3,Dissemination and citizen-science events,10000
C.3,Neuromorphic hardware access and cloud compute,15000
C.3,Other additional direct costs: certificate on the financial statements,5000
D,Internally invoiced goods and services,0
```

Additional funding (up to €1 M): not requested in this draft. Consider it only if decision 2(a),
a HOVER insect lab at IU, needs major equipment that IU cannot provide. It must be justified as
necessary for the project.

## Resources text (form field, max 8000 characters incl. spaces)

<!-- RESOURCES START -->
HOVER requests EUR 2,000,000 for 60 months: EUR 1,600,000 direct costs and EUR 400,000 indirect costs (25 % flat rate). No additional funding is requested.

A. Personnel (EUR 1,285,000). The PI devotes 50 % of working time to HOVER, above the 40 % minimum. The PI's salary is paid by IU and is not charged to the grant. The team has five research positions and two support roles.
Postdoc 1, computational neuroscience (48 person-months, EUR 330,000): leads the Tier 1-3 models in WP1 and the theory in WP3 (task optimisation, mean-field analysis, motif extraction).
Postdoc 2, neuromorphic computer vision (36 PM, EUR 245,000, from M18): builds the active event camera, implements the motif networks and runs the benchmarks in WP4.
Three PhD students (48 PM each, EUR 190,000 each, EUR 570,000): PhD 1 scales MESH and builds the gap-junction classifier (WP1). PhD 2 builds the Eristalis model families, designs the controversial stimuli and performs the tethered recordings (WP2). PhD 3 develops spiking networks for event-based vision (WP4).
A research engineer and outreach coordinator at 50 % for 60 months (EUR 110,000) develops hardware-neutral robot firmware and teaching kits and runs the robot-zoo citizen-science experiment (WP5). Student assistants (EUR 30,000) support EM proofreading, kit production and course sessions.
Costs follow IU's personnel cost rates [confirm].

C.1 Travel (EUR 40,000): visits to the partner laboratory for experiments in WP2 (about 6 per year), conference participation for team members (about 2 per year), and one project meeting per year with collaborators. The Step 2 interview is remote and costs nothing.

C.2 Equipment (EUR 140,000, depreciation according to IU accounting rules):
two event cameras with a piezo/galvo micro-movement stage (EUR 40,000), used continuously from M18 for WP4;
an infrared high-speed camera with optics for retinal tracking (EUR 55,000), used for WP2 and T4.1, about 60 % of its time;
a GPU server (EUR 45,000) for connectome-constrained network training and simulation (WP1, WP3, WP4).

C.3 Other goods, works and services (EUR 135,000):
consumables for hoverfly and Drosophila rearing, electrodes, dyes and EM data storage (EUR 35,000);
robot kits for IU courses and the robot zoo (EUR 30,000), bought by IU procurement against a hardware-neutral specification;
open-access fees for about 12 articles in fully open-access venues (EUR 40,000);
citizen-science and dissemination events (EUR 10,000);
access to neuromorphic hardware and cloud compute (EUR 15,000);
a certificate on the financial statements (EUR 5,000).

Existing resources not charged to the grant: the IU computer-vision laboratory and computing resources [confirm]; the open FlyWire connectome and the MESH software; partner equipment (two-photon imaging, micro-CT access) available through collaboration.

Conflict of interest: the PI holds a [role] at Backyard Brains, the manufacturer of SpikerBot. IU procurement selects robot hardware without the PI's involvement, and all HOVER software is released openly and runs on at least one open-hardware platform. [If Backyard Brains contributes robots in kind, state the value here.]
<!-- RESOURCES END -->
