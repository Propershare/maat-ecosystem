import { z } from "zod";

const EnvSchema = z.object({
  DATABASE_URL: z.string().min(1),
  JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters"),
  API_PORT: z.coerce.number().default(3001),
  API_HOST: z.string().default("0.0.0.0"),
  // Tehuti teaching model (Ollama OpenAI-compatible endpoint). Defaults target the
  // local offline Tehuti Scholar served by Ollama; override for other hosts.
  TEHUTI_BASE_URL: z.string().default("http://127.0.0.1:11435/v1"),
  TEHUTI_MODEL: z.string().default("tehuti-scholar:v10"),
  TEHUTI_API_KEY: z.string().default("ollama-local"),
});

export type Env = z.infer<typeof EnvSchema>;

export function loadEnv(): Env {
  const parsed = EnvSchema.safeParse(process.env);
  if (!parsed.success) {
    console.error(parsed.error.flatten().fieldErrors);
    throw new Error("Invalid environment variables");
  }
  return parsed.data;
}
