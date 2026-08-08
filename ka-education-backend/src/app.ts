import Fastify from "fastify";
import cors from "@fastify/cors";
import jwt from "@fastify/jwt";
import swagger from "@fastify/swagger";
import swaggerUi from "@fastify/swagger-ui";
import type { Env } from "./config/env.js";
import { prisma } from "./lib/prisma.js";
import { authRoutes } from "./routes/auth.js";
import { healthRoutes } from "./routes/health.js";
import { manifestRoutes } from "./routes/manifest.js";
import { soulRoutes } from "./routes/soul.js";
import { skeletonRoutes } from "./routes/skeleton.js";
import { institutionRoutes } from "./routes/institutions.js";
import { learnerRoutes } from "./routes/learners.js";
import { memoryRoutes } from "./routes/memory.js";
import { kaRoutes } from "./routes/ka.js";
import { voiceRoutes } from "./routes/voice.js";
import { brainRoutes } from "./routes/brain.js";
import { progressionRoutes } from "./routes/progression.js";
import { enrollmentRoutes } from "./routes/enrollment.js";
import { curriculumRoutes } from "./routes/curriculum.js";
import { cohortRoutes } from "./routes/cohorts.js";
import { facultyRoutes } from "./routes/faculty.js";
import { handsRoutes } from "./routes/hands.js";
import { sensesRoutes } from "./routes/senses.js";

export async function buildApp(env: Env) {
  const app = Fastify({ logger: true });

  await app.register(cors, { origin: true });
  await app.register(jwt, { secret: env.JWT_SECRET });

  app.decorate("authenticate", async function (request, reply) {
    try {
      await request.jwtVerify();
    } catch {
      return reply.code(401).send({ error: "UNAUTHORIZED" });
    }
  });

  await app.register(swagger, {
    openapi: {
      info: {
        title: "Ka Education Body API",
        description: "Constitutional education backend — organ-aligned modules",
        version: "0.1.0",
      },
    },
  });
  await app.register(swaggerUi, { routePrefix: "/docs" });

  await app.register(healthRoutes);
  await app.register(manifestRoutes);
  await app.register(authRoutes);
  await app.register(soulRoutes);
  await app.register(skeletonRoutes);
  await app.register(institutionRoutes);
  await app.register(learnerRoutes);
  await app.register(memoryRoutes);
  await app.register(kaRoutes);
  await app.register(voiceRoutes);
  await app.register(brainRoutes);
  await app.register(progressionRoutes);
  await app.register(enrollmentRoutes);
  await app.register(curriculumRoutes);
  await app.register(cohortRoutes);
  await app.register(facultyRoutes);
  await app.register(handsRoutes);
  await app.register(sensesRoutes);

  app.addHook("onClose", async () => {
    await prisma.$disconnect();
  });

  return app;
}
