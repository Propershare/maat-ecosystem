import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { StageCode } from "@prisma/client";
import { prisma } from "../lib/prisma.js";
import { buildRequireConstitution } from "../guards/constitution.js";

const CreateCohort = z.object({
  name: z.string().min(1),
  institutionId: z.string(),
  stageCode: z.nativeEnum(StageCode),
  startDate: z.string(),
  endDate: z.string().optional(),
});

export async function cohortRoutes(app: FastifyInstance) {
  const requireConstitution = buildRequireConstitution(prisma);

  app.post("/cohorts", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = CreateCohort.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const cohort = await prisma.cohort.create({
      data: {
        name: parsed.data.name,
        institutionId: parsed.data.institutionId,
        stageCode: parsed.data.stageCode,
        startDate: new Date(parsed.data.startDate),
        endDate: parsed.data.endDate ? new Date(parsed.data.endDate) : undefined,
      },
    });
    return reply.code(201).send(cohort);
  });

  app.get("/cohorts", async () => prisma.cohort.findMany({ include: { institution: true } }));
}
