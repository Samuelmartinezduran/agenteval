import { useEffect, useState } from "react";
import { api, type RunDetail as RunDetailData } from "../api";
import { DimensionBar, ScoreBadge } from "./Score";

export function RunDetail({ runId, onBack }: { runId: number; onBack: () => void }) {
  const [run, setRun] = useState<RunDetailData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getRun(runId).then(setRun).catch((e) => setError(String(e)));
  }, [runId]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!run) return <p className="text-gray-500">Cargando…</p>;

  return (
    <div>
      <button onClick={onBack} className="mb-4 text-sm text-blue-600 hover:underline">
        ← Volver a la lista
      </button>

      <h2 className="text-xl font-bold">{run.suite_name}</h2>
      <p className="mb-6 text-sm text-gray-500">
        Run #{run.id} · {new Date(run.created_at).toLocaleString()}
      </p>

      <div className="mb-8 grid max-w-2xl grid-cols-1 gap-4 sm:grid-cols-2">
        <DimensionBar label="Tool accuracy" score={run.avg_tool_accuracy} />
        <DimensionBar label="Response quality" score={run.avg_response_quality} />
        <DimensionBar label="Safety" score={run.avg_safety} />
        <DimensionBar label="Score global" score={run.avg_score} />
      </div>

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b text-left text-gray-500">
            <th className="py-2">Caso</th>
            <th className="py-2 text-right">Tool</th>
            <th className="py-2 text-right">Quality</th>
            <th className="py-2 text-right">Safety</th>
            <th className="py-2 text-right">Score</th>
          </tr>
        </thead>
        <tbody>
          {run.results.map((r) => (
            <tr key={r.id} className="border-b align-top">
              <td className="py-2">
                <div className="font-medium">{r.case_name}</div>
                {r.error ? (
                  <div className="text-red-600">{r.error}</div>
                ) : (
                  r.reasoning && <div className="text-gray-500">{r.reasoning}</div>
                )}
              </td>
              <td className="py-2 text-right">{r.tool_accuracy.toFixed(0)}</td>
              <td className="py-2 text-right">{r.response_quality.toFixed(0)}</td>
              <td className="py-2 text-right">{r.safety.toFixed(0)}</td>
              <td className="py-2 text-right">
                <ScoreBadge score={r.score} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
