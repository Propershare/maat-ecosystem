import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { BloodEventBus } from "../blood/event-bus.js";
import { buildRequireConstitution } from "../guards/constitution.js";

const CreateLearner = z.object({
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  nomeId: z.string(),
  dateOfBirth: z.string().optional(),
  currentStageCode: z
    .enum([
      "PRE_K",
      "PRIMARY",
      "LOWER_SECONDARY",
      "UPPER_SECONDARY",
      "VOCATIONAL_TECHNICAL",
      "UNDERGRAD",
      "MASTERS",
      "PHD",
      "POSTDOC_NATIONAL_RD",
    ])
    .optional(),
});

const PatchLearner = CreateLearner.partial();

export async function learnerRoutes(app: FastifyInstance) {
  const bus = new BloodEventBus(prisma);
  const requireConstitution = buildRequireConstitution(prisma);

  app.get("/learners", async () =>
    prisma.learner.findMany({
      include: { nome: true },
      orderBy: { lastName: "asc" },
    }),
  );

  app.post("/learners", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = CreateLearner.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const { dateOfBirth, ...rest } = parsed.data;
    const learner = await prisma.learner.create({
      data: {
        ...rest,
        dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
      },
    });
    await bus.publish("learner.created", { learnerId: learner.id });
    return reply.code(201).send(learner);
  });

  app.get("/learners/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    const learner = await prisma.learner.findUnique({
      where: { id },
      include: { nome: true, enrollments: { include: { cohort: true, institution: true } } },
    });
    if (!learner) return reply.code(404).send({ error: "NOT_FOUND" });
    return learner;
  });

  app.patch("/learners/:id", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const parsed = PatchLearner.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const { dateOfBirth, ...rest } = parsed.data;
    try {
      const learner = await prisma.learner.update({
        where: { id },
        data: {
          ...rest,
          ...(dateOfBirth !== undefined ? { dateOfBirth: new Date(dateOfBirth) } : {}),
        },
      });
      await bus.publish("learner.updated", { learnerId: id });
      return learner;
    } catch {
      return reply.code(404).send({ error: "NOT_FOUND" });
    }
  });

  app.get("/learners/:id/progression", { preHandler: [requireConstitution] }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const learner = await prisma.learner.findUnique({ where: { id } });
    if (!learner) return reply.code(404).send({ error: "NOT_FOUND" });
    const records = await prisma.progressRecord.findMany({
      where: { learnerId: id },
      orderBy: { decidedAt: "desc" },
    });
    return {
      learnerId: id,
      currentStageCode: learner.currentStageCode,
      records,
    };
  });

  app.get("/learners/:id/transcript", { preHandler: [requireConstitution] }, async (request, reply) => {
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
        nome: learner.nome,
        currentStageCode: learner.currentStageCode,
      },
      enrollments: learner.enrollments,
      assessments: learner.assessments,
      progression: learner.progress,
      generatedAt: new Date().toISOString(),
    };
  });
}
