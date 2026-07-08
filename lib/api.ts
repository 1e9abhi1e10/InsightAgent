export type Turn = { role: "user" | "assistant"; content: string };

export type AskResponse = {
  answer: string;
  sql: string | null;
  columns: string[];
  rows: (string | number | null)[][];
  chart_type: "bar" | "line" | "pie" | "table" | "none" | null;
  chart_config: {
    x_column?: string | null;
    y_column?: string | null;
    title?: string;
  } | null;
  clarification: boolean;
  blocked: boolean;
  error: string | null;
  timings: Record<string, number>;
  groundedness: number | null;
  groundedness_label: string | null;
  repair_attempts: number;
  cached: boolean;
};

export type EvalResult = {
  question: string;
  category: string;
  passed: boolean;
  groundedness: number | null;
  latency_ms: number;
  sql: string | null;
  answer: string;
  error: string | null;
};

export type EvalReport = {
  pass_rate: number;
  passed: number;
  total: number;
  avg_latency_ms: number;
  avg_groundedness: number;
  by_category: Record<string, [number, number]>;
  results: EvalResult[];
};

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  kpis: () => jsonFetch<Record<string, string>>("/api/kpis"),
  samples: () => jsonFetch<{ samples: string[] }>("/api/samples"),
  schema: () => jsonFetch<{ schema: string }>("/api/schema"),
  ask: (question: string, history: Turn[]) =>
    jsonFetch<AskResponse>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ question, history }),
    }),
  runEval: () => jsonFetch<EvalReport>("/api/eval", { method: "POST" }),
};
