import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";

const PainBody = z.object({
  organ: z.string().min(1),
  subdomain: z.string().optional(),
  severity: z.enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
  institutionId: z.string().optional(),
  cohortId: z.string().optional(),
  nomeId: z.string().optional(),
  description: z.string().min(1),
  evidence: z.record(z.any()).optional(),
});

export async function kaRoutes(app: FastifyInstance) {
  app.get("/ka/health", async () => {
    const [painOpen, institutions, nomes] = await Promise.all([
      prisma.painEvent.count({ where: { healed: false } }),
      prisma.institution.count({ where: { status: "ACTIVE" } }),
      prisma.nome.count(),
    ]);
    return {
      organs: {
        soul: { ok: (await prisma.constitution.count({ where: { isActive: true } })) > 0 },
        skeleton: { stageCount: await prisma.stageDefinition.count(), nomeCount: nomes },
        memory: { learners: await prisma.learner.count() },
        blood: { eventCount: await prisma.eventLog.count() },
      },
      pain: { openEvents: painOpen },
      institutionsActive: institutions,
      timestamp: new Date().toISOString(),
    };
  });

  app.get("/ka/pain", async (request) => {
    const q = request.query as { institutionId?: string; nomeId?: string; limit?: string };
    const take = Math.min(parseInt(q.limit ?? "50", 10) || 50, 200);
    return prisma.painEvent.findMany({
      where: {
        ...(q.institutionId ? { institutionId: q.institutionId } : {}),
        ...(q.nomeId ? { nomeId: q.nomeId } : {}),
      },
      orderBy: { createdAt: "desc" },
      take,
    });
  });

  app.post("/ka/pain", { onRequest: [app.authenticate] }, async (request, reply) => {
    const parsed = PainBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const ev = await prisma.painEvent.create({ data: { ...parsed.data, evidence: parsed.data.evidence ?? undefined } });
    await prisma.eventLog.create({
      data: {
        eventType: "pain.detected",
        payload: { painId: ev.id, ...parsed.data },
        source: "ka",
      },
    });
    return reply.code(201).send(ev);
  });

  app.post("/ka/heal/run", { onRequest: [app.authenticate] }, async (request, reply) => {
    const body = request.body as { painId?: string } | undefined;
    if (!body?.painId) return reply.code(400).send({ error: "painId required" });
    const pain = await prisma.painEvent.findUnique({ where: { id: body.painId } });
    if (!pain) return reply.code(404).send({ error: "NOT_FOUND" });
    const updated = await prisma.painEvent.update({
      where: { id: pain.id },
      data: { healed: true, attempts: pain.attempts + 1, method: "manual_ack" },
    });
    await prisma.eventLog.create({
      data: { eventType: "healing.applied", payload: { painId: updated.id }, source: "ka" },
    });
    return updated;
  });

  app.get("/ka/alerts", async () => {
    const critical = await prisma.painEvent.findMany({
      where: { healed: false, severity: "CRITICAL" },
      orderBy: { createdAt: "desc" },
      take: 20,
    });
    return { critical };
  });

  app.post("/ka/restoration/trigger", { onRequest: [app.authenticate] }, async (request, reply) => {
    return reply.code(501).send({
      error: "PHASE_4",
      message: "Restoration workflows — implement in Phase 4 with HealingRule engine.",
      received: request.body,
    });
  });

  app.get("/ka/drift", async (request, reply) => {
    return reply.code(501).send({
      error: "PHASE_5",
      message: "Drift assessment API — Phase 5 (analytics + Maat component inputs).",
      query: request.query,
    });
  });
}
