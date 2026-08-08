import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { buildRequireConstitution } from "../guards/constitution.js";

const CreateFaculty = z.object({
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  email: z.string().email().optional(),
  institutionId: z.string(),
  positionTitle: z.string().optional(),
});

export async function facultyRoutes(app: FastifyInstance) {
  const requireConstitution = buildRequireConstitution(prisma);

  app.get("/faculty", async () => prisma.faculty.findMany({ include: { institution: true } }));

  app.post("/faculty", { onRequest: [app.authenticate, requireConstitution] }, async (request, reply) => {
    const parsed = CreateFaculty.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const f = await prisma.faculty.create({ data: parsed.data });
    return reply.code(201).send(f);
  });
}
