# UKMT education pipeline — step-by-step summary table

**Title (source):** STEP-BY-STEP SUMMARY TABLE THAT RUNS THE SYSTEM FROM UNIVERSITY OF KMT PRESCHOOL / K–12 THROUGH POST-PHD.

This document is the **text mirror** of the primary UKMT canon table. Authoritative graphic: `UKMT_PIPELINE_TABLE.png` (same folder). Database seeds use version tag **`UKMT_EDUCATION_PIPELINE_TABLE_V1`**.

| Stage (ages / grades) | Ancient-Kmt inspired institution (translit → English) | Core purpose (Maat function) | Curriculum & pedagogy (key content) | Teacher / cadre (ancient → modern) | Step-by-step build actions |
|------------------------|--------------------------------------------------------|--------------------------------|--------------------------------------|--------------------------------------|----------------------------|
| Pre-K / Early childhood (3–5) | **hwt-mꜣꜥt** → House of Maat / community preschool | Socializing children into Maat (honesty, cooperation); neurodevelopmental foundation | (Per source table) | Sesh / facilitators | 1. Legislate universal pre-K. 2. Set Maat learning outcomes. 3. Partner with local councils. 4. Train facilitators. 5. Monitor readiness. |
| Primary (K–6) (6–12) | **pr-mꜣꜥt** → Primary House of Maat | Literacies and civic formation; factual truth-seeking | National core + Maat modules; culturally grounded materials; science corners | Sesh → credentialed primary teachers | National core curriculum with Maat modules; culturally grounded textbooks; cascade teacher training; equip science corners. |
| Lower secondary (7–9) | **pr-ꜥnḫ** → local Per-Ankh branch / junior learning + small research labs | Scientific literacy; interdisciplinary thinking; early career counseling | Mini-research; Per-Ankh labs in nome nodes | Sesh + lab supervisors; exchanges | Create Per-Ankh labs in every sepat node; mandatory mini-research; teacher exchanges. |
| Upper secondary (10–12) | Per-Ankh Lyceum | Specialization (STEM/trades); applied projects tied to state plans | Applied capstone; exam reform alignment | Master teachers + industry mentors | Applied capstones; national exam reform; internships with state enterprises. |
| Vocational & technical (post-12) | Per-Ankh Technical Institutes (state polytechnics) | Skilled technicians for state industry; collective ownership consciousness | Apprenticeship-integrated competencies | Journeyman / technician pathways | National apprenticeship law; wage/subsidy guarantees; industry-training agreements. |
| Undergraduate (BSc / BA) | University Per-Ankh Faculties | Professional scientists/engineers; research integrated into teaching | Major/minor + ethics core; research studios | Doctoral faculty + lab leads | Centralize research funding; per-nome admission quotas; fellowships. |
| Masters (MSc / MA) | Postgraduate Per-Ankh Institutes | Specialization; policy–research linkage; leadership | Coursework + thesis/project + public deliverables | Faculty + practitioner fellows | Targeted fellowships; public internship deliverables; link to Council of Sesh. |
| PhD (Doctoral) | Per-Ankh Research Academy (**pr-ꜥnḫ-wr**, great House of Life) | Train PIs; original research for state R&D | Candidacy + dissertation; open data where possible | Supervisory committee + external examiners | Cohort doctoral funding tied to priorities; open-data requirements; rotational placements. |
| Postdoc & National R&D | National Per-Ankh Institutes & **Council of Sesh** | Translational R&D; tech transfer; national capability | Portfolio + milestones + consortia | PI eligibility + Maat oversight boards | National labs by sector; integrate with state planning; institutionalize Maat oversight. |

## Engineering note

- The **nine rows** are **`StageCode` enums** in `ka-education-backend` (application layer).  
- The **42 nomes** are a **separate structural layer** in the same backend (`Nome` model).  
- Do not use either count as a stand-in for **MaatBench** or aggregate **Maat score** without explicit metric definitions.
