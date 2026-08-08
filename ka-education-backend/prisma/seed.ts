/**
 * Seed: roles, 42 nomes, 9 stage definitions, constitution, Maat principles, admin user.
 * Run: npx prisma db seed
 */
import { PrismaClient, StageCode, MaatPillar, AuditAction } from "@prisma/client";
import bcrypt from "bcryptjs";

const prisma = new PrismaClient();

/**
 * University of KMT — primary canon: step-by-step pipeline table (Preschool / K–12 through Post-PhD).
 * Institutional names: Ancient Egyptian transliteration → English (Per-Ankh, Sesh, nome/sepat node model).
 */
const STAGE_SEEDS: Array<{
  code: StageCode;
  title: string;
  ageMin?: number;
  ageMax?: number;
  institutionalForm: string;
  corePurpose: string;
  curriculumModel: string;
  pedagogyModel: string;
  credentialModel: string;
  transitionIn: string;
  transitionOut: string;
  outputs: string;
  maatObligations: string;
  publicService: string;
  stepwiseBuildActions: string;
}> = [
  {
    code: StageCode.PRE_K,
    title: "Pre-K / Early childhood (ages 3–5)",
    ageMin: 3,
    ageMax: 5,
    institutionalForm:
      "hwt-mꜣꜥt (House of Maat / community preschool) — Ancient-Kmt inspired nome-anchored early learning.",
    corePurpose:
      "Socializing children into Maat (honesty, cooperation); neurodevelopmental foundation; ethical habit formation.",
    curriculumModel:
      "Maat-aligned early learning outcomes; play- and story-rich content; sensory and movement integration.",
    pedagogyModel:
      "Facilitator-led circles; family and local council visibility; readiness observance without single high-stakes gating.",
    credentialModel:
      "Sesh / scribe-facilitator cadre for early childhood — nome-certified facilitators (modern: licensed ECE + UKMT Maat facilitators).",
    transitionIn: "Family registration; developmental and health baseline; nome assignment.",
    transitionOut: "Holistic readiness for Primary (pr-mꜣꜥt) — portfolio-based gate.",
    outputs: "Learner portfolio; nome early-learning report; council partnership record.",
    maatObligations: "Truth in developmental records; balance in child workload; reciprocity with families and councils.",
    publicService: "Parent education; nome reading circles tied to local priorities.",
    stepwiseBuildActions: `1. Legislate universal pre-K.
2. Set Maat learning outcomes for the stage.
3. Partner with local councils (nome / sepat nodes).
4. Train and certify facilitators (Sesh cadre).
5. Monitor readiness with evidence, not a single test.`,
  },
  {
    code: StageCode.PRIMARY,
    title: "Primary (K–6, ages 6–12)",
    ageMin: 6,
    ageMax: 12,
    institutionalForm: "pr-mꜣꜥt (Primary House of Maat).",
    corePurpose: "Literacies and civic formation; factual truth-seeking grounded in Maat.",
    curriculumModel:
      "National core curriculum with dedicated Maat ethics / civics modules; culturally grounded instructional materials.",
    pedagogyModel:
      "Structured literacy and numeracy; cooperative projects; science corners and inquiry starters in every nome school.",
    credentialModel:
      "Sesh (teacher-scribe) cadre — primary educators with cascade training and Maat-aligned certification.",
    transitionIn: "Pre-K completion or equivalent readiness portfolio.",
    transitionOut: "Placement to Lower secondary (pr-ꜥnḫ branch) per nome policy.",
    outputs: "Transcript; Maat civics portfolio; nome assessment summary; service log.",
    maatObligations: "Justice in access; order in progression; truth in grading with evidence.",
    publicService: "Community service hours aligned to nome priorities.",
    stepwiseBuildActions: `1. Adopt national core curriculum including Maat modules.
2. Publish culturally grounded textbooks and instructional guides.
3. Run cascade teacher training (Sesh development).
4. Equip science corners and inquiry labs in primary sites.`,
  },
  {
    code: StageCode.LOWER_SECONDARY,
    title: "Lower secondary (grades 7–9)",
    ageMin: 12,
    ageMax: 14,
    institutionalForm:
      "pr-ꜥnḫ — local Per-Ankh branch (junior learning + small research labs in every nome / sepat node).",
    corePurpose: "Scientific literacy; interdisciplinary thinking; early career counseling and pathway honesty.",
    curriculumModel:
      "Integrated STEM + humanities strands; mandatory mini-research projects; lab access in nome nodes.",
    pedagogyModel:
      "Guided inquiry; formative assessment; cross-subject projects; peer and Sesh mentoring.",
    credentialModel:
      "Subject-qualified Sesh + lab supervisors; nome exchange qualification for faculty rotation.",
    transitionIn: "Primary transcript; nome placement; pathway advisory.",
    transitionOut: "Upper secondary (Per-Ankh Lyceum) or vocational track entry.",
    outputs: "Competency map; mini-research portfolio; counseling record.",
    maatObligations: "Balance of theory and practice; reciprocity through peer tutoring and nome service.",
    publicService: "Nome maintenance and apprenticeship-preview projects.",
    stepwiseBuildActions: `1. Create Per-Ankh labs in every nome (sepat) node.
2. Institute mandatory mini-research projects for all learners.
3. Establish teacher exchanges between nome branches.`,
  },
  {
    code: StageCode.UPPER_SECONDARY,
    title: "Upper secondary (grades 10–12)",
    ageMin: 15,
    ageMax: 17,
    institutionalForm: "Per-Ankh Lyceum (specialized secondary).",
    corePurpose:
      "Specialization (STEM, trades, humanities) with applied projects tied to state and nome development plans.",
    curriculumModel:
      "Track-based programs with applied capstone; alignment to national exam reform where applicable.",
    pedagogyModel: "Seminars; labs; mentorship from industry and senior Sesh; internship integration.",
    credentialModel: "Master teachers; industry co-mentors; assessment authorities with public criteria.",
    transitionIn: "Lower secondary transcript; track selection with transparent justice review.",
    transitionOut: "Undergraduate, accredited vocational diploma, national service, or workforce bridge.",
    outputs: "Capstone deliverables; national assessment record; internship and mentorship logs.",
    maatObligations: "Order and transparency in assessments; justice in track assignment.",
    publicService: "Extended nome service; industry shadowing with reciprocity obligations.",
    stepwiseBuildActions: `1. Implement applied capstone projects tied to state plans.
2. Execute national exam reform aligned to Maat evidence standards.
3. Create internships with state enterprises and nome partners.`,
  },
  {
    code: StageCode.VOCATIONAL_TECHNICAL,
    title: "Vocational & technical (post–grade 12)",
    ageMin: 18,
    ageMax: 22,
    institutionalForm: "Per-Ankh Technical Institutes (state polytechnics).",
    corePurpose:
      "Supply state industry with skilled technicians; embed collective ownership and ethical practice in trades.",
    curriculumModel:
      "National competence framework; shop and lab intensive modules; apprenticeship-integrated assessment.",
    pedagogyModel: "Co-teaching with industry; workplace assessors; safety-first ritual (Maat order).",
    credentialModel: "Journeyman / technician pathways; nome and national assessor boards.",
    transitionIn: "Upper secondary completion or approved workforce bridge.",
    transitionOut: "Employment, stackable credentials, or bridge to undergraduate Per-Ankh faculties.",
    outputs: "Skills passport; apprenticeship completion; collective-governance participation record.",
    maatObligations: "Truth in skill verification; balance in workload and safety; reciprocity with industry and community.",
    publicService: "Public infrastructure practicum projects.",
    stepwiseBuildActions: `1. Enact national apprenticeship law with Maat oversight.
2. Guarantee wages / subsidies for learners per policy.
3. Sign industry–training agreements at nome and national levels.`,
  },
  {
    code: StageCode.UNDERGRAD,
    title: "Undergraduate (BSc / BA)",
    ageMin: 18,
    ageMax: 22,
    institutionalForm: "University Per-Ankh Faculties (national & nome campuses).",
    corePurpose:
      "Educate professional scientists, engineers, and civic leaders; integrate research literacy into teaching.",
    curriculumModel:
      "Major/minor structures; Maat ethics / governance core; undergraduate research studios per faculty.",
    pedagogyModel:
      "Lecture + lab + research studio; nome extension mandates for applied learning.",
    credentialModel:
      "Doctoral-qualified Sesh faculty; certified lab leads; external examiners where required.",
    transitionIn: "Secondary or vocational bridge per transparent admission rules; per-nome quotas reserved.",
    transitionOut: "Honours, Masters, or workforce with stackable credits.",
    outputs: "Degree audit; optional thesis; service transcript; research portfolio.",
    maatObligations: "Integrity of credit; equitable advising; reciprocity via peer teaching and nome extension.",
    publicService: "Nome extension programs; open lab days for communities.",
    stepwiseBuildActions: `1. Centralize and publish research funding rules with Maat accountability.
2. Reserve per-nome admission quotas and monitor justice metrics.
3. Establish fellowship programs tied to national priorities.`,
  },
  {
    code: StageCode.MASTERS,
    title: "Masters (MSc / MA)",
    ageMin: 23,
    ageMax: 35,
    institutionalForm: "Postgraduate Per-Ankh Institutes.",
    corePurpose:
      "Advanced specialization; policy–research linkage; leadership training for nome and national service.",
    curriculumModel:
      "Coursework plus applied project or thesis; policy clinic modules where applicable.",
    pedagogyModel:
      "Seminar-led depth; industry and government co-supervision; public deliverables.",
    credentialModel:
      "Terminal-degree faculty; practitioner fellows; national review boards.",
    transitionIn: "Undergraduate degree or equivalent demonstrated practice.",
    transitionOut: "Doctoral academy, executive leadership, or specialist practice.",
    outputs: "Thesis or applied project; policy brief; portfolio defense record.",
    maatObligations: "Transparency in authorship; justice in committee composition; balance in workload.",
    publicService: "Mandatory public internship deliverables benefiting nomes.",
    stepwiseBuildActions: `1. Fund targeted fellowships aligned to national plans.
2. Require public internship deliverables with audit trail.
3. Link institutes to Council of Sesh and policy bodies.`,
  },
  {
    code: StageCode.PHD,
    title: "PhD (Doctoral)",
    ageMin: 24,
    ageMax: 40,
    institutionalForm:
      "Per-Ankh Research Academy — pr-ꜥnḫ-wr (great House of Life): principal-investigator formation.",
    corePurpose:
      "Train principal investigators; produce original research aligned to state R&D priorities.",
    curriculumModel:
      "Minimal coursework; candidacy examination; dissertation with open methods where Maat permits.",
    pedagogyModel:
      "Supervisory panel; public proposal and defense; cohort seminars; rotational placements.",
    credentialModel:
      "Credentialed supervisory committee + external examiners; national doctoral board recognition.",
    transitionIn: "Masters or exceptional undergraduate pipeline with evidence.",
    transitionOut: "Postdoc / national R&D placement; faculty; policy fellow.",
    outputs: "Dissertation; publications; open data commitments where applicable; public engagement log.",
    maatObligations:
      "Research integrity (truth); attribution (justice); balanced supervisory load; reciprocity to nome schools.",
    publicService: "Open data defaults; nome briefing requirement.",
    stepwiseBuildActions: `1. Tie cohort-based doctoral funding to national R&D priorities.
2. Mandate open-data requirements where ethically and legally possible.
3. Require rotational placements across nome and national labs.`,
  },
  {
    code: StageCode.POSTDOC_NATIONAL_RD,
    title: "Postdoc & National R&D",
    institutionalForm:
      "National Per-Ankh Institutes & Council of Sesh — federated research system across strategic sectors.",
    corePurpose:
      "High-impact translational R&D; technology transfer; national capability building under Maat oversight.",
    curriculumModel:
      "Project portfolio aligned to state plans; milestone reviews; sector consortia.",
    pedagogyModel:
      "PI-led consortia; cross-institutional teams; knowledge transfer offices.",
    credentialModel:
      "PI eligibility; national fellowship and council review; Maat oversight boards.",
    transitionIn: "Doctoral completion matched to national priority slots.",
    transitionOut: "National faculty; lab director; policy fellow; return obligations to nome system.",
    outputs: "Sector deliverables; patents; translated curricula for schools; policy papers.",
    maatObligations:
      "Stewardship of public funds; equity in team formation; reciprocity through mandated school/nome translation.",
    publicService: "Institutionalized Maat oversight of major programs.",
    stepwiseBuildActions: `1. Create national labs per strategic sector with nome hooks.
2. Integrate R&D planning with national planning commission processes.
3. Institutionalize Maat oversight and public reporting on outcomes.`,
  },
];

const MAAT_SEED: Array<{ pillar: MaatPillar; name: string; description: string; sortOrder: number }> = [
  { pillar: MaatPillar.TRUTH, name: "Data completeness", description: "Source: registry + assessments; method: required-field coverage ratio.", sortOrder: 1 },
  { pillar: MaatPillar.TRUTH, name: "Evidence-backed decisions", description: "Source: progress records; method: proportion of promotions with attached evidence objects.", sortOrder: 2 },
  { pillar: MaatPillar.JUSTICE, name: "Equitable access by nome", description: "Source: enrollment + capacity; method: disparity index vs national mean.", sortOrder: 3 },
  { pillar: MaatPillar.BALANCE, name: "Learner workload", description: "Source: curriculum assignments; method: hours vs stage guidelines.", sortOrder: 4 },
  { pillar: MaatPillar.ORDER, name: "Policy compliance", description: "Source: audit trail; method: violations / decisions.", sortOrder: 5 },
  { pillar: MaatPillar.RECIPROCITY, name: "Public service completion", description: "Source: service obligations; method: completed / assigned hours.", sortOrder: 6 },
];

async function main() {
  await prisma.auditTrail.deleteMany();
  await prisma.assessmentResult.deleteMany();
  await prisma.assessment.deleteMany();
  await prisma.progressRecord.deleteMany();
  await prisma.enrollment.deleteMany();
  await prisma.cohort.deleteMany();
  await prisma.learner.deleteMany();
  await prisma.faculty.deleteMany();
  await prisma.institution.deleteMany();
  await prisma.institutionType.deleteMany();
  await prisma.nome.deleteMany();
  await prisma.curriculumModule.deleteMany();
  await prisma.stageDefinition.deleteMany();
  await prisma.constitution.deleteMany();
  await prisma.maatPrinciple.deleteMany();
  await prisma.governancePolicy.deleteMany();
  await prisma.painEvent.deleteMany();
  await prisma.healingRule.deleteMany();
  await prisma.eventLog.deleteMany();
  await prisma.user.deleteMany();
  await prisma.rolePermission.deleteMany();
  await prisma.permission.deleteMany();
  await prisma.role.deleteMany();

  const soulWrite = await prisma.permission.create({ data: { name: "soul:write" } });
  const memoryWrite = await prisma.permission.create({ data: { name: "memory:write" } });
  const progressionExec = await prisma.permission.create({ data: { name: "progression:execute" } });

  const role = await prisma.role.create({
    data: {
      name: "SUPER_ADMIN",
      description: "Full governance access",
    },
  });
  await prisma.rolePermission.createMany({
    data: [
      { roleId: role.id, permissionId: soulWrite.id },
      { roleId: role.id, permissionId: memoryWrite.id },
      { roleId: role.id, permissionId: progressionExec.id },
    ],
  });

  const passwordHash = await bcrypt.hash("ChangeMe!KaEdu", 10);
  const admin = await prisma.user.create({
    data: {
      email: "admin@ka-education.local",
      passwordHash,
      displayName: "Ka Admin",
      roleId: role.id,
    },
  });

  await prisma.constitution.create({
    data: {
      version: "1.0.0",
      title: "Ka Education Body — Founding Constitution",
      bodyMd: `# Constitution 1.0.0

- Maat before capability.
- No promotion without evidence and audit.
- Evaluation (Maat score / principles) is **not** the same layer as **42 nomes** or **nine pipeline stages**.
- **Primary curricular canon:** \`docs/canon/UKMT_EDUCATION_PIPELINE.md\` and \`UKMT_PIPELINE_TABLE.png\` — University of KMT step-by-step pipeline (Preschool / K–12 through Post-PhD). Database tag: \`UKMT_EDUCATION_PIPELINE_TABLE_V1\`.
`,
      isActive: true,
    },
  });

  for (const m of MAAT_SEED) {
    await prisma.maatPrinciple.create({ data: m });
  }

  for (const s of STAGE_SEEDS) {
    await prisma.stageDefinition.create({
      data: {
        code: s.code,
        title: s.title,
        canonReference: "UKMT_EDUCATION_PIPELINE_TABLE_V1",
        ageRangeMin: s.ageMin,
        ageRangeMax: s.ageMax,
        institutionalForm: s.institutionalForm,
        corePurpose: s.corePurpose,
        curriculumModel: s.curriculumModel,
        pedagogyModel: s.pedagogyModel,
        credentialModel: s.credentialModel,
        transitionRequirementsIn: s.transitionIn,
        transitionRequirementsOut: s.transitionOut,
        expectedOutputs: s.outputs,
        maatObligations: s.maatObligations,
        publicServiceObligations: s.publicService,
        stepwiseBuildActions: s.stepwiseBuildActions,
        version: 1,
      },
    });
  }

  for (let i = 1; i <= 42; i++) {
    const code = `NOME_${String(i).padStart(2, "0")}`;
    await prisma.nome.create({
      data: {
        code,
        name: `Nome ${i}`,
        description: `Structural nome registry entry ${i} of 42 — replace with canonical nome metadata.`,
      },
    });
  }

  const instType = await prisma.institutionType.create({
    data: {
      code: "PRIMARY_SCHOOL",
      name: "Primary School",
      description: "General primary institution type",
    },
  });

  const nome1 = await prisma.nome.findFirst({ where: { code: "NOME_01" } });
  if (!nome1) throw new Error("Nomes missing");

  const exemplar = await prisma.institution.create({
    data: {
      name: "Exemplar Primary — Nome 01",
      institutionTypeId: instType.id,
      nomeId: nome1.id,
      charterSummary: "Pilot institution for Ka Education MVP.",
    },
  });

  await prisma.faculty.create({
    data: {
      firstName: "Nefer",
      lastName: "Senet",
      email: "nefer.senet@exemplar.ka.local",
      institutionId: exemplar.id,
      positionTitle: "Lead Guide",
    },
  });

  await prisma.auditTrail.create({
    data: {
      entityType: "Constitution",
      entityId: "bootstrap",
      action: AuditAction.CREATE,
      actorId: admin.id,
      diff: { message: "Seed completed" },
    },
  });

  console.log("Seed OK. Admin login: admin@ka-education.local / ChangeMe!KaEdu");
}

main()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
