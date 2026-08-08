import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { StageCode } from "@prisma/client";
import { prisma } from "../lib/prisma.js";
import { buildRequireConstitution } from "../guards/constitution.js";
import { BloodEventBus } from "../blood/event-bus.js";

const EvaluateBody = z.object({ learnerId: z.string() });

const PromoteBody = z.object({
  learnerId: z.string(),
  toStageCode: z.nativeEnum(StageCode),
  evidence: z.string().min(1),
  explainability: z.record(z.any()),
});

export async function progressionRoutes(app: FastifyInstance) {
  const requireConstitution = buildRequireConstitution(prisma);
  const bus = new BloodEventBus(prisma);

  app.post("/progression/evaluate", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = EvaluateBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const learner = await prisma.learner.findUnique({
      where: { id: parsed.data.learnerId },
      include: { enrollments: true, assessments: true },
    });
    if (!learner) return reply.code(404).send({ error: "NOT_FOUND" });
    const enrollmentCount = learner.enrollments.length;
    const ready = Boolean(learner.currentStageCode && enrollmentCount > 0);
    return {
      learnerId: learner.id,
      readyToProgress: ready,
      explainability: {
        factors: {
          currentStage: learner.currentStageCode,
          enrollmentCount,
          assessmentResults: learner.assessments.length,
        },
        message: ready
          ? "MVP rule: learner has stage + ≥1 enrollment — extend with assessment gates in Phase 2."
          : "Requires current stage and active enrollment.",
      },
      blackBox: false,
    };
  });

  app.post("/progression/promote", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = PromoteBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const { learnerId, toStageCode, evidence, explainability } = parsed.data;
    const learner = await prisma.learner.findUnique({ where: { id: learnerId } });
    if (!learner?.currentStageCode) {
      return reply.code(400).send({ error: "LEARNER_STAGE_UNKNOWN" });
    }
    const record = await prisma.progressRecord.create({
      data: {
        learnerId,
        fromStageCode: learner.currentStageCode,
        toStageCode,
        evidence,
        explainability,
        promoted: true,
        decidedByUserId: (request.user as { sub?: string })?.sub ?? null,
      },
    });
    await prisma.learner.update({ where: { id: learnerId }, data: { currentStageCode: toStageCode } });
    await bus.publish("stage.progressed", { learnerId, toStageCode, recordId: record.id });
    await prisma.auditTrail.create({
      data: {
        entityType: "Learner",
        entityId: learnerId,
        action: "PROGRESSION",
        actorId: (request.user as { sub?: string })?.sub ?? undefined,
        diff: { toStageCode, recordId: record.id },
      },
    });
    return reply.code(201).send({ record, learnerId, newStage: toStageCode });
  });

  app.post("/progression/intervene", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    return reply.code(501).send({ error: "PHASE_2", body: request.body });
  });
}
