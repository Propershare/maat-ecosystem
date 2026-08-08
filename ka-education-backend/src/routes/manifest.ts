import type { FastifyInstance } from "fastify";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";

export async function manifestRoutes(app: FastifyInstance) {
  app.get("/manifest", async (_request, reply) => {
    try {
      const raw = readFileSync(join(process.cwd(), "MANIFEST.ka"), "utf-8");
      const parsed = YAML.parse(raw);
      return reply.send({
        format: "ka-manifest",
        raw,
        parsed,
      });
    } catch (e) {
      return reply.code(500).send({ error: "MANIFEST_READ_FAILED", message: String(e) });
    }
  });
}
