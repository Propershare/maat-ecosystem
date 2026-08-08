import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";

const PolicyBody = z.object({
  title: z.string().min(1),
  body: z.string().min(1),
});

export async function soulRoutes(app: FastifyInstance) {
  app.get("/soul/constitution", async (_request, reply) => {
    const c = await prisma.constitution.findFirst({ where: { isActive: true } });
    if (!c) return reply.code(404).send({ error: "NO_ACTIVE_CONSTITUTION" });
    return {
      version: c.version,
      title: c.title,
      bodyMd: c.bodyMd,
      effectiveFrom: c.effectiveFrom,
    };
  });

  app.get("/soul/maat/principles", async () => {
    const rows = await prisma.maatPrinciple.findMany({ orderBy: [{ pillar: "asc" }, { sortOrder: "asc" }] });
    return {
      count: rows.length,
      pillarsDistinct: [...new Set(rows.map((r) => r.pillar))].length,
      principles: rows.map((r) => ({
        id: r.id,
        pillar: r.pillar,
        name: r.name,
        description: r.description,
        sortOrder: r.sortOrder,
        evaluationLayer: true,
        notStructuralNome: true,
      })),
    };
  });

  app.get("/soul/nomes", async () => {
    const nomes = await prisma.nome.findMany({ orderBy: { code: "asc" } });
    return {
      count: nomes.length,
      structuralLayer: "42-nome registry (counts are structural, not MaatBench scores)",
      nomes: nomes.map((n) => ({
        id: n.id,
        code: n.code,
        name: n.name,
        description: n.description,
      })),
    };
  });

  app.get("/soul/roles", async () => {
    const roles = await prisma.role.findMany({ include: { permissions: { include: { permission: true } } } });
    return {
      roles: roles.map((r) => ({
        id: r.id,
        name: r.name,
        permissions: r.permissions.map((p) => p.permission.name),
      })),
    };
  });

  app.post("/soul/policies", { onRequest: [app.authenticate] }, async (request, reply) => {
    const parsed = PolicyBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const policy = await prisma.governancePolicy.create({
      data: {
        title: parsed.data.title,
        body: parsed.data.body,
        status: "DRAFT",
        requiresApproval: true,
      },
    });
    return reply.code(201).send(policy);
  });

  app.get("/soul/charters/:institutionId", async (request, reply) => {
    const { institutionId } = request.params as { institutionId: string };
    const inst = await prisma.institution.findUnique({ where: { id: institutionId } });
    if (!inst) return reply.code(404).send({ error: "INSTITUTION_NOT_FOUND" });
    return {
      institutionId: inst.id,
      name: inst.name,
      charterSummary: inst.charterSummary,
      nomeId: inst.nomeId,
    };
  });
}
