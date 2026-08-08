import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";

const SearchBody = z.object({
  query: z.string().min(1),
  limit: z.coerce.number().min(1).max(100).default(20),
});

export async function memoryRoutes(app: FastifyInstance) {
  app.post("/memory/learners/search", { onRequest: [app.authenticate] }, async (request, reply) => {
    const parsed = SearchBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const { query, limit } = parsed.data;
    const parts = query.trim().split(/\s+/).filter(Boolean);
    const learners = await prisma.learner.findMany({
      where: {
        OR: [
          { firstName: { contains: query, mode: "insensitive" } },
          { lastName: { contains: query, mode: "insensitive" } },
          ...(parts.length >= 2
            ? [
                {
                  AND: [
                    { firstName: { contains: parts[0]!, mode: "insensitive" as const } },
                    { lastName: { contains: parts[1]!, mode: "insensitive" as const } },
                  ],
                },
              ]
            : []),
        ],
      },
      take: limit,
      include: { nome: true },
    });
    return { query, count: learners.length, learners };
  });

  app.get("/memory/learners/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    const learner = await prisma.learner.findUnique({
      where: { id },
      include: { nome: true, enrollments: true },
    });
    if (!learner) return reply.code(404).send({ error: "NOT_FOUND" });
    return learner;
  });

  app.get("/memory/institutions/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    const inst = await prisma.institution.findUnique({ where: { id }, include: { nome: true, type: true } });
    if (!inst) return reply.code(404).send({ error: "NOT_FOUND" });
    return inst;
  });

  app.get("/memory/cohorts/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    const cohort = await prisma.cohort.findUnique({
      where: { id },
      include: { institution: true, enrollments: { include: { learner: true } } },
    });
    if (!cohort) return reply.code(404).send({ error: "NOT_FOUND" });
    return cohort;
  });

  app.get("/memory/research/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    return reply.code(501).send({
      error: "PHASE_3",
      message: "Research project store not implemented in Phase 1 — use placeholder id after Phase 3.",
      id,
    });
  });

  app.post("/memory/archive", { onRequest: [app.authenticate] }, async (_request, reply) => {
    return reply.code(501).send({ error: "PHASE_3", message: "Archive workflow scheduled for later phase." });
  });
}
