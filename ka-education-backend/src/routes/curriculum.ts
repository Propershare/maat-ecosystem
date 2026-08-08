import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { StageCode } from "@prisma/client";
import { prisma } from "../lib/prisma.js";
import { buildRequireConstitution } from "../guards/constitution.js";

const ModuleBody = z.object({
  code: z.string().min(1),
  title: z.string().min(1),
  stageCode: z.nativeEnum(StageCode),
  credits: z.number().optional(),
  sequence: z.number().optional(),
  summary: z.string().optional(),
});

const AssessmentBody = z.object({
  title: z.string().min(1),
  type: z.string().min(1),
  moduleId: z.string().optional(),
});

const ResultBody = z.object({
  learnerId: z.string(),
  score: z.number().optional(),
  passed: z.boolean().optional(),
  evidenceUrl: z.string().optional(),
  explainJson: z.record(z.any()).optional(),
});

export async function curriculumRoutes(app: FastifyInstance) {
  const requireConstitution = buildRequireConstitution(prisma);

  app.get("/stages", async () => {
    const stages = await prisma.stageDefinition.findMany({ orderBy: { code: "asc" } });
    return stages;
  });

  app.get("/stages/:id", async (request, reply) => {
    const { id } = request.params as { id: string };
    const stage = await prisma.stageDefinition.findUnique({ where: { id } });
    if (!stage) return reply.code(404).send({ error: "NOT_FOUND" });
    return stage;
  });

  app.get("/curriculum/modules", async (request) => {
    const q = request.query as { stageCode?: string };
    return prisma.curriculumModule.findMany({
      where: q.stageCode ? { stageCode: q.stageCode as StageCode } : {},
      orderBy: [{ stageCode: "asc" }, { sequence: "asc" }],
    });
  });

  app.post("/curriculum/modules", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = ModuleBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    try {
      const mod = await prisma.curriculumModule.create({
        data: {
          code: parsed.data.code,
          title: parsed.data.title,
          stageCode: parsed.data.stageCode,
          credits: parsed.data.credits,
          sequence: parsed.data.sequence ?? 0,
          summary: parsed.data.summary,
        },
      });
      return reply.code(201).send(mod);
    } catch (e) {
      return reply.code(400).send({ error: "CREATE_FAILED", message: String(e) });
    }
  });

  app.post("/assessments", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = AssessmentBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const a = await prisma.assessment.create({ data: parsed.data });
    return reply.code(201).send(a);
  });

  app.post("/assessments/:id/results", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const parsed = ResultBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const { learnerId, score, passed, evidenceUrl, explainJson } = parsed.data;
    const res = await prisma.assessmentResult.create({
      data: {
        assessmentId: id,
        learnerId,
        score,
        passed,
        evidenceUrl,
        explainJson,
      },
    });
    return reply.code(201).send(res);
  });
}
