import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";

const RawPayload = z.object({
  eventType: z.string(),
  payload: z.record(z.any()),
  source: z.string().optional(),
});

export async function sensesRoutes(app: FastifyInstance) {
  app.post("/senses/attendance", { onRequest: [app.authenticate] }, async (request, reply) => {
    await prisma.eventLog.create({
      data: { eventType: "senses.attendance", payload: (request.body as object) ?? {}, source: "senses" },
    });
    return reply.code(202).send({ accepted: true });
  });

  app.post("/senses/assessments/import", { onRequest: [app.authenticate] }, async (request, reply) => {
    await prisma.eventLog.create({
      data: { eventType: "senses.assessments.import", payload: (request.body as object) ?? {}, source: "senses" },
    });
    return reply.code(202).send({ accepted: true });
  });

  app.post("/senses/reports/council", { onRequest: [app.authenticate] }, async (request, reply) => {
    await prisma.eventLog.create({
      data: { eventType: "senses.reports.council", payload: (request.body as object) ?? {}, source: "senses" },
    });
    return reply.code(202).send({ accepted: true });
  });

  app.post("/senses/reports/industry", { onRequest: [app.authenticate] }, async (request, reply) => {
    await prisma.eventLog.create({
      data: { eventType: "senses.reports.industry", payload: (request.body as object) ?? {}, source: "senses" },
    });
    return reply.code(202).send({ accepted: true });
  });

  app.post("/senses/events", { onRequest: [app.authenticate] }, async (request, reply) => {
    const parsed = RawPayload.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    await prisma.eventLog.create({
      data: {
        eventType: parsed.data.eventType,
        payload: parsed.data.payload,
        source: parsed.data.source ?? "senses",
      },
    });
    return reply.code(202).send({ accepted: true });
  });
}
