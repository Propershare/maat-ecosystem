import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { StageCode } from "@prisma/client";
import { prisma } from "../lib/prisma.js";
import { buildRequireConstitution } from "../guards/constitution.js";
import { BloodEventBus } from "../blood/event-bus.js";

const EnrollBody = z.object({
  learnerId: z.string(),
  cohortId: z.string(),
  institutionId: z.string(),
  stageCode: z.nativeEnum(StageCode),
});

export async function enrollmentRoutes(app: FastifyInstance) {
  const requireConstitution = buildRequireConstitution(prisma);
  const bus = new BloodEventBus(prisma);

  app.post("/enrollments", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = EnrollBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    try {
      const enrollment = await prisma.enrollment.create({
        data: {
          learnerId: parsed.data.learnerId,
          cohortId: parsed.data.cohortId,
          institutionId: parsed.data.institutionId,
          stageCode: parsed.data.stageCode,
        },
      });
      await prisma.learner.update({
        where: { id: parsed.data.learnerId },
        data: { currentStageCode: parsed.data.stageCode },
      });
      await bus.publish("learner.enrolled", { enrollmentId: enrollment.id });
      return reply.code(201).send(enrollment);
    } catch (e) {
      return reply.code(400).send({ error: "ENROLL_FAILED", message: String(e) });
    }
  });
}
