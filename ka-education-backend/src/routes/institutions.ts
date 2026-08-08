import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { BloodEventBus } from "../blood/event-bus.js";

const CreateInstitution = z.object({
  name: z.string().min(1),
  institutionTypeId: z.string(),
  nomeId: z.string(),
  charterSummary: z.string().optional(),
});

const PatchInstitution = z.object({
  name: z.string().optional(),
  status: z.enum(["ACTIVE", "INACTIVE", "ARCHIVED", "SUSPENDED"]).optional(),
  charterSummary: z.string().optional(),
});

export async function institutionRoutes(app: FastifyInstance) {
  const bus = new BloodEventBus(prisma);

  app.get("/institutions", async () => prisma.institution.findMany({ include: { type: true, nome: true } }));

  app.post("/institutions", { onRequest: [app.authenticate] }, async (request, reply) => {
    const parsed = CreateInstitution.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const inst = await prisma.institution.create({ data: parsed.data });
    await bus.publish("institution.created", { institutionId: inst.id });
    return reply.code(201).send(inst);
  });

  app.get("/institutions/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    const inst = await prisma.institution.findUnique({
      where: { id },
      include: { type: true, nome: true, faculty: true, cohorts: true },
    });
    if (!inst) return reply.code(404).send({ error: "NOT_FOUND" });
    return inst;
  });

  app.patch("/institutions/:id", { onRequest: [app.authenticate] }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const parsed = PatchInstitution.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    try {
      const inst = await prisma.institution.update({ where: { id }, data: parsed.data });
      await bus.publish("institution.updated", { institutionId: id });
      return inst;
    } catch {
      return reply.code(404).send({ error: "NOT_FOUND" });
    }
  });

  app.get("/institutions/:id/health", async (request, reply) => {
    const { id } = request.params as { id: string };
    const inst = await prisma.institution.findUnique({ where: { id } });
    if (!inst) return reply.code(404).send({ error: "NOT_FOUND" });
    const pains = await prisma.painEvent.findMany({
      where: { institutionId: id },
      orderBy: { createdAt: "desc" },
      take: 10,
    });
    return {
      institutionId: id,
      status: inst.status,
      recentPain: pains,
    };
  });
}
