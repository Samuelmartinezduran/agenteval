import { useEffect, useState } from "react";
import { api, type RunSummary, type Suite } from "../api";
import { ScoreBadge } from "./Score";

export function RunList({ onOpen }: { onOpen: (id: number) => void }) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [suites, setSuites] = useState<Suite[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const refresh = () => {
    api.listRuns().then(setRuns).catch((e) => setError(String(e)));
    api.listSuites().then(setSuites).catch(() => {});
  };

  useEffect(refresh, []);

  const triggerRun = async (suiteId: number) => {
    setRunning(true);
    try {
      const run = await api.createRun(suiteId);
      onOpen(run.id);
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      {error && <p className="mb-4 text-red-600">{error}</p>}

      {suites.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-2 text-sm font-semibold text-gray-500">Lanzar evaluación</h2>
          <div className="flex flex-wrap gap-2">
            {suites.map((s) => (
              <button
                key={s.id}
                disabled={running}
                onClick={() => triggerRun(s.id)}
                className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                ▶ {s.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <h2 className="mb-2 text-sm font-semibold text-gray-500">Ejecuciones</h2>
      {runs.length === 0 ? (
        <p className="text-gray-500">Aún no hay ejecuciones.</p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b text-left text-gray-500">
              <th className="py-2">Suite</th>
              <th className="py-2 text-right">Tool</th>
              <th className="py-2 text-right">Quality</th>
              <th className="py-2 text-right">Safety</th>
              <th className="py-2 text-right">Score</th>
              <th className="py-2 text-right">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr
                key={r.id}
                onClick={() => onOpen(r.id)}
                className="cursor-pointer border-b hover:bg-gray-50"
              >
                <td className="py-2 font-medium">{r.suite_name}</td>
                <td className="py-2 text-right">{r.avg_tool_accuracy.toFixed(0)}</td>
                <td className="py-2 text-right">{r.avg_response_quality.toFixed(0)}</td>
                <td className="py-2 text-right">{r.avg_safety.toFixed(0)}</td>
                <td className="py-2 text-right">
                  <ScoreBadge score={r.avg_score} />
                </td>
                <td className="py-2 text-right text-gray-400">
                  {new Date(r.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
