/**
 * Tehuti teaching client.
 *
 * Talks to the Tehuti Scholar model over an OpenAI-compatible chat-completions
 * endpoint (Ollama by default). The model's Maat/UKMT system prompt and safety
 * disposition live in the model itself, so callers only supply the learner-facing
 * question plus optional teaching context.
 */

export interface TehutiConfig {
  baseUrl: string;
  model: string;
  apiKey: string;
}

export interface TeachContext {
  /** Optional learner stage code (e.g. UKMT pipeline stage) for tailoring depth. */
  stageCode?: string | null;
  /** Optional free-form context (cohort, subject, prior notes). */
  notes?: string | null;
}

export interface TeachResult {
  answer: string;
  model: string;
}

export function loadTehutiConfig(): TehutiConfig {
  return {
    baseUrl: process.env.TEHUTI_BASE_URL ?? "http://127.0.0.1:11435/v1",
    model: process.env.TEHUTI_MODEL ?? "tehuti-scholar:v10",
    apiKey: process.env.TEHUTI_API_KEY ?? "ollama-local",
  };
}

function buildUserPrompt(question: string, context?: TeachContext): string {
  const parts: string[] = [];
  if (context?.stageCode) {
    parts.push(`Learner stage: ${context.stageCode}. Calibrate depth to this stage.`);
  }
  if (context?.notes) {
    parts.push(`Context: ${context.notes}`);
  }
  parts.push(question);
  return parts.join("\n\n");
}

/**
 * Ask Tehuti to teach. Returns the model's answer text.
 * Throws on transport/HTTP errors so the route can map them to a clean status.
 */
export async function teach(
  question: string,
  context?: TeachContext,
  config: TehutiConfig = loadTehutiConfig(),
  signal?: AbortSignal,
): Promise<TeachResult> {
  const url = `${config.baseUrl.replace(/\/$/, "")}/chat/completions`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({
      model: config.model,
      messages: [{ role: "user", content: buildUserPrompt(question, context) }],
      stream: false,
    }),
    signal,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`Tehuti request failed: ${response.status} ${response.statusText} ${detail}`.trim());
  }

  const data = (await response.json()) as {
    choices?: Array<{ message?: { content?: string } }>;
  };
  const answer = data.choices?.[0]?.message?.content?.trim();
  if (!answer) {
    throw new Error("Tehuti returned an empty response");
  }

  return { answer, model: config.model };
}
