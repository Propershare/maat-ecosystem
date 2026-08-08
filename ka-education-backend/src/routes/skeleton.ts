import type { FastifyInstance } from "fastify";
import { prisma } from "../lib/prisma.js";

export async function skeletonRoutes(app: FastifyInstance) {
  app.get("/skeleton/stages", async () => {
    const stages = await prisma.stageDefinition.findMany({ orderBy: { code: "asc" } });
    return {
      count: stages.length,
      stages: stages.map((s) => ({
        id: s.id,
        code: s.code,
        title: s.title,
        canonReference: s.canonReference,
        version: s.version,
        ageRangeMin: s.ageRangeMin,
        ageRangeMax: s.ageRangeMax,
        institutionalForm: s.institutionalForm,
        corePurpose: s.corePurpose,
        curriculumModel: s.curriculumModel,
        pedagogyModel: s.pedagogyModel,
        credentialModel: s.credentialModel,
        transitionRequirementsIn: s.transitionRequirementsIn,
        transitionRequirementsOut: s.transitionRequirementsOut,
        expectedOutputs: s.expectedOutputs,
        maatObligations: s.maatObligations,
        publicServiceObligations: s.publicServiceObligations,
        stepwiseBuildActions: s.stepwiseBuildActions,
        effectiveFrom: s.effectiveFrom,
      })),
    };
  });

  app.get("/skeleton/stages/:code", async (request, reply) => {
    const { code } = request.params as { code: string };
    const s = await prisma.stageDefinition.findUnique({ where: { code: code as never } });
    if (!s) return reply.code(404).send({ error: "STAGE_NOT_FOUND" });
    return s;
  });

  app.get("/skeleton/institution-types", async () => {
    return prisma.institutionType.findMany({ orderBy: { name: "asc" } });
  });

  app.get("/skeleton/schema/:name", async (request, reply) => {
    const { name } = request.params as { name: string };
    const schemas: Record<string, object> = {
      Learner: {
        type: "object",
        required: ["firstName", "lastName", "nomeId"],
        properties: {
          firstName: { type: "string" },
          lastName: { type: "string" },
          nomeId: { type: "string" },
          dateOfBirth: { type: "string", format: "date" },
          currentStageCode: { type: "string" },
        },
      },
      Institution: {
        type: "object",
        required: ["name", "institutionTypeId", "nomeId"],
        properties: {
          name: { type: "string" },
          institutionTypeId: { type: "string" },
          nomeId: { type: "string" },
          charterSummary: { type: "string" },
        },
      },
      PainEvent: {
        type: "object",
        required: ["organ", "severity", "description"],
        properties: {
          organ: { type: "string" },
          subdomain: { type: "string" },
          severity: { enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"] },
          institutionId: { type: "string" },
          nomeId: { type: "string" },
          description: { type: "string" },
          evidence: { type: "object" },
        },
      },
    };
    const schema = schemas[name];
    if (!schema) return reply.code(404).send({ error: "UNKNOWN_SCHEMA", name });
    return { name, schema };
  });
}
