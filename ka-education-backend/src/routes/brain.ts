import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { buildRequireConstitution } from "../guards/constitution.js";
import { teach } from "../lib/tehuti.js";

const ProgressionEvaluate = z.object({
  learnerId: z.string(),
});

const TeachBody = z.object({
  question: z.string().min(1),
  learnerId: z.string().optional(),
  stageCode: z.string().optional(),
  notes: z.string().optional(),
});

export async function brainRoutes(app: FastifyInstance) {
  const requireConstitution = buildRequireConstitution(prisma);

  // Tehuti teaching brain: answers a learner-facing question through the
  // Maat/UKMT-governed Tehuti Scholar model. Read-only with respect to domain
  // state; emits a Blood event so the teaching trail is auditable (and can feed
  // the self-learning loop).
  app.post("/brain/teach", { onRequest: [app.authenticate] }, async (request, reply) => {
    const parsed = TeachBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }

    let stageCode = parsed.data.stageCode ?? null;
    if (parsed.data.learnerId) {
      const learner = await prisma.learner.findUnique({ where: { id: parsed.data.learnerId } });
      if (!learner) return reply.code(404).send({ error: "LEARNER_NOT_FOUND" });
      stageCode = stageCode ?? learner.currentStageCode ?? null;
    }

    let result: { answer: string; model: string };
    try {
      result = await teach(parsed.data.question, { stageCode, notes: parsed.data.notes ?? null });
    } catch (error) {
      request.log.error({ err: error }, "Tehuti teach failed");
      return reply.code(502).send({
        error: "TEHUTI_UNAVAILABLE",
        message: error instanceof Error ? error.message : "Tehuti teaching model is unreachable",
      });
    }

    await prisma.eventLog.create({
      data: {
        eventType: "brain.teach",
        payload: {
          model: result.model,
          learnerId: parsed.data.learnerId ?? null,
          stageCode,
          question: parsed.data.question,
        },
        source: "brain",
      },
    });

    return {
      learnerId: parsed.data.learnerId ?? null,
      stageCode,
      model: result.model,
      answer: result.answer,
    };
  });

  app.post(
    "/brain/progression/evaluate",
    { onRequest: [app.authenticate, requireConstitution] },
    async (request, reply) => {
      const parsed = ProgressionEvaluate.safeParse(request.body);
      if (!parsed.success) {
        return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
      }
      const learner = await prisma.learner.findUnique({
        where: { id: parsed.data.learnerId },
        include: { enrollments: true, assessments: true },
      });
      if (!learner) return reply.code(404).send({ error: "LEARNER_NOT_FOUND" });

      const factors = {
        currentStage: learner.currentStageCode,
        enrollmentCount: learner.enrollments.length,
        assessmentResults: learner.assessments.length,
        hasNome: !!learner.nomeId,
      };

      const ready = Boolean(learner.currentStageCode && factors.enrollmentCount > 0);
      return {
        learnerId: learner.id,
        readyToProgress: ready,
        explainability: {
          factors,
          message: ready
            ? "MVP rule: enrolled + stage set — replace with curriculum gates in Phase 2."
            : "Missing enrollment or stage — not ready.",
        },
        blackBox: false,
      };
    },
  );

  app.post("/brain/curriculum/recommend", { onRequest: [app.authenticate] }, async (request, reply) => {
    return reply.code(501).send({ error: "PHASE_2", body: request.body });
  });

  app.post("/brain/interventions/suggest", { onRequest: [app.authenticate] }, async (request, reply) => {
    return reply.code(501).send({ error: "PHASE_5", body: request.body });
  });

  app.post("/brain/research/match", { onRequest: [app.authenticate] }, async (request, reply) => {
    return reply.code(501).send({ error: "PHASE_3", body: request.body });
  });
}
