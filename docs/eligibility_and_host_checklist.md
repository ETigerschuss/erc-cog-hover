# Eligibility, host and open items

Status after your answers on 3 Nov 2026. ✅ settled · ⏳ action needed · ❓ your decision.
Page numbers refer to the ERC-2027 Information for Applicants (IfA v11.0).

## Settled ✅

| Item | Result | Basis |
|---|---|---|
| Host | **IU Internationale Hochschule (Germany)**: a legal entity in an EU Member State, so eligible as a host | IfA p. 9–10 |
| PhD window | PhD 2016 falls inside the CoG-2027 window (defence 1 Jan 2012 – 31 Dec 2021). StG-2027 is *not* possible (its window starts 2017), so the CoG is the right scheme. | IfA p. 11 |
| Backyard Brains | Affiliation confirmed. Handled openly → [`coi_backyard_brains.md`](coi_backyard_brains.md) | — |
| DFG | Sequential: ERC-2027-CoG first; DFG Sachbeihilfe only if the ERC fails. The 2026 DFG draft was never submitted, so nothing is pending → [`dfg_backup_strategy.md`](dfg_backup_strategy.md) | — |
| Experiments | At **MPI for Biological Intelligence** (Fenk lab: physiology) and **LMU** (Merrill lab: DNA analysis of where the third muscle comes from). Proposed form: each hosts one HOVER PhD student as an **additional beneficiary**. | IfA p. 24 fn 48, p. 30 |

## With IU's research / grants office ⏳ (start this week)

1. **Legal name, PIC and LEAR.** Exact legal entity (e.g. "IU Internationale Hochschule GmbH"; confirm),
   its PIC in the F&T Participant Register, and who the LEAR is. The correct PIC is needed when you
   create the draft proposal.
2. **Gender Equality Plan.** As a *private higher-education establishment*, IU needs a GEP or
   equivalent meeting four requirements: published and signed by top management; dedicated
   resources; sex/gender-disaggregated staff and student data with reporting at least every two
   years; training. It must be in place at grant signature (IfA p. 10, 25). Ask whether IU's current
   equality or diversity documents meet these, or whether IU must adopt one.
3. **Host Institution Support Letter.** Mandatory ERC wording on IU letterhead, signed by IU's legal
   representative. The text is ready in [`../admin/host_support_letter.md`](../admin/host_support_letter.md).
   Target: signed by **18 Dec 2026**.
4. **Budget inputs.** IU personnel cost rates (PhD, postdoc, engineer); whether the PI's salary is
   charged to the grant; depreciation rules for equipment. Also confirm whether IU has handled
   Horizon Europe grants before (financial capacity is checked at granting).
5. **Conditions the panel will judge from B2 and Resources** (the letter does not cover them):
   - lab space for fly rearing and an eye-tracking/EMG rig;
   - GPU/HPC access;
   - a teaching reduction that makes ≥ 40 % on HOVER real;
   - **a doctoral route**: does IU have doctoral rights? If not, enrol all four HOVER PhD students at
     LMU under a co-supervision agreement (natural now that LMU is a partner);
   - EU-grant administration.

   Put these in an internal agreement with IU.

## PI actions ⏳

1. **PhD document.** The certificate must show the **defence date** (*Tag der mündlichen Prüfung*).
   If it only shows the award date, ask your awarding university to complete the Annex 4.9 template
   (IfA p. 68). Request it now, before the Christmas closure.
2. **Written consent before 12 Jan 2027** (IfA p. 24, 26). Keep the e-mails as proof.
   - From every researcher you name: L. Fenk, R. Merrill, neuromorphic platform hosts, any advisory board.
   - Agree in writing with L. Fenk how HOVER (*Eristalis*, models, machines) and her ERC CoG
     *FlyActiveComp* (*Drosophila* eye-movement mechanisms) divide the field; B2 §6 states this.
   - From the **participating organisations**, the MPG (MPI-BI administration) and LMU (research
     office), to join as additional beneficiaries. Get each one's PIC, a contact person, cost rates and
     the budget for its own Part A section. Fill in "Links with other proposal participating
     organisations" in Part A (IfA p. 25).
   - ERC support letters are *not* submitted and would be disregarded (IfA p. 33).
3. **Time commitment.** ≥ 40 % on HOVER and ≥ 50 % of *all* working time in the EU/AC, counting the
   Backyard Brains role (IfA p. 11). Write down your split: IU %, BYB %, HOVER %.
4. **Independence.** This is the CoG benchmark (IfA p. 9) and the weakest point of the current CV.
   Your key preprints have a former mentor as last author.
   - Evidence you have now: MESH (sole developer, `CITATION.cff`); the 2023 open-citizen-science
     paper; outreach programmes; the professorship; supervised students.
   - Before January, if possible: post a preprint with you as senior/corresponding author (e.g.
     ALIstim / controversial stimuli, or the HOVER SNN preliminary results), and collect a list of
     students and theses you supervised and any funds you raised as PI.
   - Do not list former supervisors as team members. Present them as collaborators with a defined,
     limited role. The HOVER postdoc sits in the Fenk lab, so B2 must show that you select, fund and direct
     this person and that Fenk co-supervises locally.
5. **Excluded reviewers.** You may name up to 3, with name, institution, town, country and web page
   (IfA p. 26).
6. **DFG eligibility of IU staff** (for the backup): ask IU's research office now; see [`dfg_backup_strategy.md`](dfg_backup_strategy.md) §4.

## Decisions ❓

1. **Panel.** Recommended: LS5 primary, PE6 secondary (reasoning below).
2. **Partner set-up.** Decided 3 Nov 2026: the MPG and LMU as additional beneficiaries; a **36-month
   postdoc** in the Fenk lab (physiology in a non-genetic insect needs an experienced person) and a
   **PhD student** in the Merrill lab (budget in `proposal/PartA_budget_resources.md`). Personnel
   cannot be covered by ERC additional funding, so the team fits under the €2.0 M cap. Confirm with
   Fenk and Merrill; get the MPG and LMU research offices' consent and PICs.
3. **Start date.** Grant preparation follows the 17 Dec 2027 results. Plan a start around
   **Sep 2028** (placeholder in `proposal/gantt.md`).

## Panel choice: LS5 or PE6?

| | LS5 (neuroscience) | PE6 (computer science) |
|---|---|---|
| Track-record fit | Strong (Nat Neurosci 2023, Neuron, Curr Biol, connectomics preprints) | Weaker: few CV/ML-venue papers yet |
| Fit with the professorship | Neutral | Strong |
| Risk | CV/robotics aims may look like an add-on | Fly work may look like "just biology"; high bar for CV baselines |

**LS5 primary, PE6 secondary.** Frame HOVER as computational neuroscience with a computer-vision
test of generality. Step-1 panel members act as generalists (IfA p. 28), so the B1 must be readable
by a molecular neuroscientist as well as a modeller. Revisit if you have CV-venue papers before
January.
