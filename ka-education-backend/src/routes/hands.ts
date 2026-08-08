import type { FastifyInstance } from "fastify";

export async function handsRoutes(app: FastifyInstance) {
  app.post("/hands/certificates/generate", { onRequest: [app.authenticate] }, async (_request, reply) => {
    return reply.code(501).send({ error: "PHASE_2", message: "Certificate generation — document pipeline not implemented." });
  });
  app.post("/hands/apprenticeships/assign", { onRequest: [app.authenticate] }, async (_request, reply) => {
    return reply.code(501).send({ error: "PHASE_3" });
  });
  app.post("/hands/projects/create", { onRequest: [app.authenticate] }, async (_request, reply) => {
    return reply.code(501).send({ error: "PHASE_3" });
  });
  app.post("/hands/tasks/execute", { onRequest: [app.authenticate] }, async (_request, reply) => {
    return reply.code(501).send({ error: "PHASE_2" });
  });
}
