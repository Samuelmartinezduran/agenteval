import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type RunSummary, type Suite } from "../api";
import { ScoreBadge, StatusChip, getFeedbackColors } from "./Score";

// Formateador de tiempo relativo simple para la fecha
function timeAgo(dateString: string) {
  const date = new Date(dateString);
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
  let interval = seconds / 31536000;
  if (interval > 1) return Math.floor(interval) + " años";
  interval = seconds / 2592000;
  if (interval > 1) return Math.floor(interval) + " meses";
  interval = seconds / 86400;
  if (interval > 1) return Math.floor(interval) + " días";
  interval = seconds / 3600;
  if (interval > 1) return Math.floor(interval) + " horas";
  interval = seconds / 60;
  if (interval > 1) return Math.floor(interval) + " min";
  return Math.floor(seconds) + " seg";
}

export function RunList() {
  const navigate = useNavigate();
  const onOpen = (id: number) => navigate(`/runs/${id}`);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [suites, setSuites] = useState<Suite[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState<number | null>(null);

  const refresh = () => {
    api.listRuns().then(setRuns).catch((e) => setError(String(e)));
    api.listSuites().then(setSuites).catch(() => {});
  };

  useEffect(refresh, []);

  // Mientras haya runs en curso, refresca la lista para ver cuándo terminan.
  const anyRunning = runs.some((r) => r.status === "running");
  useEffect(() => {
    if (!anyRunning) return;
    const timer = setInterval(refresh, 2000);
    return () => clearInterval(timer);
  }, [anyRunning]);

  const triggerRun = async (suiteId: number) => {
    setRunning(suiteId);
    try {
      // La API responde al instante con el run en "running"; el detalle hace polling.
      const run = await api.createRun(suiteId);
      onOpen(run.id);
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(null);
    }
  };

  return (
    <main className="flex-grow w-full px-margin-mobile md:px-gutter max-w-container-max mx-auto py-stack-lg flex flex-col gap-12">
      {error && (
        <div className="bg-error-container text-on-error-container p-4 rounded-lg font-body-md shadow-sm">
          {error}
        </div>
      )}

      {suites.length > 0 && (
        <section className="flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Lanzar evaluación</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {suites.map((s) => (
              <div key={s.id} className="bg-surface-container-lowest rounded-2xl p-6 shadow-level-1 card-gradient-stroke flex flex-col justify-between hover:shadow-level-2 transition-shadow duration-300">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center text-primary">
                        <span className="material-symbols-outlined text-xl">terminal</span>
                      </div>
                      <h3 className="font-headline-md text-headline-md font-mono-code text-mono-code text-on-surface">{s.name}</h3>
                    </div>
                  </div>
                  <p className="font-body-md text-body-md text-on-surface-variant mb-6 min-h-[60px]">
                    {s.description || "Evaluación de capacidades del agente."}
                  </p>
                </div>
                <button
                  disabled={running === s.id}
                  onClick={() => triggerRun(s.id)}
                  className="w-full py-2 px-4 bg-primary-container text-on-primary rounded-lg font-label-sm text-label-sm hover:bg-primary transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="material-symbols-outlined text-sm">
                    {running === s.id ? "hourglass_empty" : "play_arrow"}
                  </span>
                  {running === s.id ? "Ejecutando..." : "Ejecutar"}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Ejecuciones recientes</h2>
        </div>

        {runs.length === 0 ? (
          <div className="text-center py-12 text-on-surface-variant font-body-md text-body-md border border-dashed border-outline-variant rounded-2xl bg-surface-container-lowest">
            <span className="material-symbols-outlined text-4xl mb-2 text-outline">inbox</span>
            <p>Aún no hay ejecuciones</p>
          </div>
        ) : (
          <div className="bg-surface-container-lowest rounded-2xl shadow-level-1 border border-outline-variant overflow-hidden">
            <div className="overflow-x-auto w-full">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-outline-variant bg-surface-container-low">
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold w-1/4">Suite</th>
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Estado</th>
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Tool accuracy</th>
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Response quality</th>
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Safety</th>
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-center">Score</th>
                    <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Fecha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant">
                  {runs.map((r) => {
                    const rowColors = getFeedbackColors(r.avg_score);
                    const pending = r.status !== "completed";
                    return (
                      <tr
                        key={r.id}
                        onClick={() => onOpen(r.id)}
                        className="table-row-hover cursor-pointer transition-colors group"
                      >
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${rowColors.dot}`}></div>
                            <span className="font-mono-code text-mono-code text-on-surface font-medium group-hover:text-primary transition-colors">
                              {r.suite_name}
                            </span>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <StatusChip status={r.status} />
                        </td>
                        <td className="py-4 px-6 text-right font-mono-code text-mono-code text-on-surface-variant">{pending ? "—" : r.avg_tool_accuracy.toFixed(0)}</td>
                        <td className="py-4 px-6 text-right font-mono-code text-mono-code text-on-surface-variant">{pending ? "—" : r.avg_response_quality.toFixed(0)}</td>
                        <td className="py-4 px-6 text-right font-mono-code text-mono-code text-on-surface-variant">{pending ? "—" : r.avg_safety.toFixed(0)}</td>
                        <td className="py-4 px-6 text-center">
                          {pending ? <span className="text-on-surface-variant font-mono-code text-mono-code">—</span> : <ScoreBadge score={r.avg_score} />}
                        </td>
                        <td className="py-4 px-6 text-right font-body-md text-body-md text-on-surface-variant whitespace-nowrap">
                          Hace {timeAgo(r.created_at)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
