/**
 * Injects GITMAAT-CONTEXT.md into agent bootstrap so every turn sees current tasks (Maat: query first).
 * Workspace hook for Tehuti Lab; runs on agent:bootstrap.
 */
import fs from "node:fs/promises";
import path from "node:path";

const GITMAAT_FILENAME = "GITMAAT-CONTEXT.md";

export default async function gitmaatBootstrapHook(event) {
  if (event?.type !== "agent" || event?.action !== "bootstrap") return;
  const ctx = event.context;
  if (!ctx?.workspaceDir || !Array.isArray(ctx.bootstrapFiles)) return;

  const filePath = path.join(ctx.workspaceDir, GITMAAT_FILENAME);
  let content;
  try {
    content = await fs.readFile(filePath, "utf-8");
  } catch {
    return;
  }
  const trimmed = content.trim();
  if (!trimmed) return;

  const entry = {
    name: GITMAAT_FILENAME,
    path: filePath,
    content: trimmed,
    missing: false,
  };
  ctx.bootstrapFiles.unshift(entry);
}
