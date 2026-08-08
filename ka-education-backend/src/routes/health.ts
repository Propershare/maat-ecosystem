import type { FastifyInstance } from "fastify";
import { prisma } from "../lib/prisma.js";

export async function healthRoutes(app: FastifyInstance) {
  app.get("/health", async (_request, reply) => {
    try {
      await prisma.$queryRaw`SELECT 1`;
      const constitution = await prisma.constitution.findFirst({ where: { isActive: true } });
      return {
        status: "ok",
        database: "connected",
        soul: { constitutionActive: !!constitution, version: constitution?.version ?? null },
        timestamp: new Date().toISOString(),
      };
    } catch (e) {
      reply.code(503);
      return { status: "error", database: "disconnected", message: String(e) };
    }
  });
}
