import type { FastifyReply, FastifyRequest } from "fastify";
import type { PrismaClient } from "@prisma/client";

/**
 * Soul boots first: progression and promotion cannot run without an active constitution.
 */
export function buildRequireConstitution(prisma: PrismaClient) {
  return async function requireConstitution(_request: FastifyRequest, reply: FastifyReply) {
    const active = await prisma.constitution.findFirst({ where: { isActive: true } });
    if (!active) {
      return reply.code(503).send({
        error: "CONSTITUTION_REQUIRED",
        message: "No active constitution version — soul layer not booted.",
      });
    }
  };
}
