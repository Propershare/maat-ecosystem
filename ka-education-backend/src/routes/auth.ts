import type { FastifyInstance } from "fastify";
import bcrypt from "bcryptjs";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";

const LoginBody = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export async function authRoutes(app: FastifyInstance) {
  app.post("/auth/login", async (request, reply) => {
    const parsed = LoginBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: "VALIDATION_ERROR", details: parsed.error.flatten() });
    }
    const { email, password } = parsed.data;
    const user = await prisma.user.findUnique({ where: { email }, include: { role: true } });
    if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
      return reply.code(401).send({ error: "INVALID_CREDENTIALS" });
    }
    const token = app.jwt.sign({ sub: user.id, email: user.email, role: user.role.name });
    return { token, user: { id: user.id, email: user.email, role: user.role.name } };
  });

  app.post("/auth/refresh", { onRequest: [app.authenticate] }, async (request, reply) => {
    const sub = (request.user as { sub: string }).sub;
    const user = await prisma.user.findUnique({ where: { id: sub }, include: { role: true } });
    if (!user) return reply.code(401).send({ error: "USER_GONE" });
    const token = app.jwt.sign({ sub: user.id, email: user.email, role: user.role.name });
    return { token };
  });
}
