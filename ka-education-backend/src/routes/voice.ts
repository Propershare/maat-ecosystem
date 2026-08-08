import type { FastifyInstance } from "fastify";
import { prisma } from "../lib/prisma.js";

export async function voiceRoutes(app: FastifyInstance) {
  app.get("/voice/dashboard/overview", async () => {
    const [learners, institutions, enrollments, pains] = await Promise.all([
      prisma.learner.count(),
      prisma.institution.count(),
      prisma.enrollment.count(),
      prisma.painEvent.count({ where: { healed: false } }),
    ]);
    return {
      summary: {
        learners,
        institutions,
        enrollments,
        openPainEvents: pains,
      },
      layers: {
        structuralNomes: await prisma.nome.count(),
        stageDefinitions: await prisma.stageDefinition.count(),
        evaluationPrinciples: await prisma.maatPrinciple.count(),
      },
      note: "nomes count = structural layer; maat_principles = evaluation layer — do not conflate.",
    };
  });

  app.get("/voice/dashboard/nomes/:nomeId", async (request, reply) => {
    const { nomeId } = request.params as { nomeId: string };
    const nome = await prisma.nome.findUnique({
      where: { id: nomeId },
      include: {
        institutions: { include: { type: true } },
        learners: { take: 50 },
      },
    });
    if (!nome) return reply.code(404).send({ error: "NOT_FOUND" });
    return nome;
  });

  app.get("/voice/dashboard/stages", async () => {
    const stages = await prisma.stageDefinition.findMany({ orderBy: { code: "asc" } });
    const enrolleds = await Promise.all(
      stages.map((s) => prisma.enrollment.count({ where: { stageCode: s.code } })),
    );
    return {
      stages: stages.map((s, i) => ({
        code: s.code,
        title: s.title,
        enrolled: enrolleds[i] ?? 0,
      })),
    };
  });

  app.get("/voice/dashboard/research", async (request, reply) => {
    return reply.code(501).send({ error: "PHASE_3", message: "Research dashboard — Phase 3." });
  });

  app.get("/voice/dashboard/maat", async () => {
    const principles = await prisma.maatPrinciple.findMany({ orderBy: [{ pillar: "asc" }, { sortOrder: "asc" }] });
    return {
      type: "evaluation_components",
      notAggregatedScore: true,
      principles: principles.map((p) => ({
        pillar: p.pillar,
        name: p.name,
        description: p.description,
        source: "seed + governance",
        calculationMethod: "defined per metric in Phase 5 — MVP lists inputs only",
      })),
    };
  });

  app.get("/voice/learners/:id/transcript", async (request, reply) => {
    const { id } = request.params as { id: string };
    const learner = await prisma.learner.findUnique({
      where: { id },
      include: {
        nome: true,
        enrollments: { include: { institution: true, cohort: true } },
        assessments: { include: { assessment: true } },
        progress: { orderBy: { decidedAt: "desc" } },
      },
    });
    if (!learner) return reply.code(404).send({ error: "NOT_FOUND" });
    return {
      learner: {
        id: learner.id,
        name: `${learner.firstName} ${learner.lastName}`,
        currentStageCode: learner.currentStageCode,
      },
      enrollments: learner.enrollments,
      assessments: learner.assessments,
      progression: learner.progress,
    };
  });

  app.get("/voice/institutions/:id/profile", async (request, reply) => {
    const { id } = request.params as { id: string };
    const inst = await prisma.institution.findUnique({
      where: { id },
      include: { nome: true, type: true, cohorts: true, faculty: true },
    });
    if (!inst) return reply.code(404).send({ error: "NOT_FOUND" });
    return inst;
  });

  app.get("/voice/reports/system-health", async () => {
    return {
      ka: {
        openPain: await prisma.painEvent.count({ where: { healed: false } }),
        recentEvents: await prisma.eventLog.findMany({ orderBy: { createdAt: "desc" }, take: 15 }),
      },
      boot: {
        constitution: !!(await prisma.constitution.findFirst({ where: { isActive: true } })),
        stages: await prisma.stageDefinition.count(),
      },
    };
  });
}
