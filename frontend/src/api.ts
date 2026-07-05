// Cliente ligero de la API de agenteval.

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type RunStatus = "running" | "completed" | "failed";

export interface RunSummary {
  id: number;
  suite_id: number | null;
  suite_name: string;
  status: RunStatus;
  error: string | null;
  avg_tool_accuracy: number;
  avg_response_quality: number;
  avg_safety: number;
  avg_score: number;
  created_at: string;
  finished_at: string | null;
}

export interface CaseResult {
  id: number;
  case_name: string;
  tool_accuracy: number;
  response_quality: number;
  safety: number;
  score: number;
  reasoning: string;
  agent_content: string;
  error: string | null;
}

export interface RunDetail extends RunSummary {
  results: CaseResult[];
}

export interface Suite {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export interface CaseScores {
  tool_accuracy: number;
  response_quality: number;
  safety: number;
  score: number;
}

export interface CaseComparison {
  case_name: string;
  a: CaseScores | null;
  b: CaseScores | null;
  delta_score: number | null;
}

export interface RunComparison {
  run_a: RunSummary;
  run_b: RunSummary;
  cases: CaseComparison[];
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}

export const api = {
  listRuns: () => get<RunSummary[]>("/runs"),
  getRun: (id: number) => get<RunDetail>(`/runs/${id}`),
  compareRuns: (a: number, b: number) => get<RunComparison>(`/runs/${a}/compare/${b}`),
  listSuites: () => get<Suite[]>("/suites"),
  createRun: async (suiteId: number): Promise<RunDetail> => {
    const res = await fetch(`${BASE}/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ suite_id: suiteId }),
    });
    if (!res.ok) throw new Error(`POST /runs -> ${res.status}`);
    return res.json();
  },
};
