import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type RunDetail as RunDetailData, type RunSummary } from "../api";
import { DimensionBar, StatusChip, getFeedbackColors } from "./Score";

export function RunDetail() {
  const navigate = useNavigate();
  const onBack = () => navigate("/");
  const runId = Number(useParams().id);
  const [run, setRun] = useState<RunDetailData | null>(null);
  const [others, setOthers] = useState<RunSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  const isRunning = run?.status === "running";

  useEffect(() => {
    const fetchRun = () => api.getRun(runId).then(setRun).catch((e) => setError(String(e)));
    fetchRun();
    // Mientras el run esté en curso, refresca hasta que el backend lo cierre.
    if (!isRunning) return;
    const timer = setInterval(fetchRun, 2000);
    return () => clearInterval(timer);
  }, [runId, isRunning]);

  // Otros runs completados de la misma suite, para el selector "Comparar con...".
  // Filtra por suite_id (clave estable); solo cae a suite_name en runs antiguos
  // sin suite_id. Así no se ofrecen suites distintas que comparten nombre.
  useEffect(() => {
    if (!run) return;
    const sameSuite = (r: RunSummary) =>
      run.suite_id != null ? r.suite_id === run.suite_id : r.suite_name === run.suite_name;
    api
      .listRuns()
      .then((all) =>
        setOthers(all.filter((r) => r.id !== run.id && sameSuite(r) && r.status === "completed")),
      )
      .catch(() => {});
  }, [run?.id, run?.suite_id, run?.suite_name]);

  if (error) {
    return (
      <main className="max-w-container-max mx-auto px-margin-mobile md:px-gutter py-stack-lg flex flex-col gap-stack-lg">
        <div className="bg-error-container text-on-error-container p-4 rounded-lg font-body-md shadow-sm">
          {error}
        </div>
        <button onClick={onBack} className="self-start mt-4 px-4 py-2 bg-surface-container rounded-lg font-label-sm text-on-surface">Volver</button>
      </main>
    );
  }

  if (!run) {
    return (
      <main className="max-w-container-max mx-auto px-margin-mobile md:px-gutter py-stack-lg flex flex-col gap-stack-lg items-center justify-center min-h-[50vh]">
        <div className="font-body-md text-on-surface-variant">Cargando...</div>
      </main>
    );
  }

  const globalColors = getFeedbackColors(run.avg_score);

  return (
    <main className="max-w-container-max mx-auto px-margin-mobile md:px-gutter py-stack-lg flex flex-col gap-stack-lg w-full flex-grow">
      {/* Back Navigation Context */}
      <nav aria-label="Back">
        <button 
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-on-surface-variant hover:text-primary transition-colors duration-200 font-label-sm text-label-sm bg-surface-container-lowest px-3 py-1.5 rounded-full border border-outline-variant shadow-sm w-fit group"
        >
          <span className="material-symbols-outlined text-[16px] group-hover:-translate-x-0.5 transition-transform">arrow_back</span>
          Volver
        </button>
      </nav>

      {/* Header Section */}
      <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-stack-md border-b border-outline-variant pb-stack-lg">
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="font-headline-lg-mobile md:font-headline-xl text-headline-lg-mobile md:text-headline-xl text-on-surface">
              {run.suite_name}
            </h1>
            <span className="px-2.5 py-1 bg-surface-container rounded-md border border-outline-variant font-mono-code text-mono-code text-on-surface-variant">
              Run #{run.id}
            </span>
            <StatusChip status={run.status} />
          </div>
          {run.status === "failed" && run.error && (
            <div className="bg-error-container text-on-error-container p-3 rounded-lg font-body-md">
              {run.error}
            </div>
          )}
          {others.length > 0 && (
            <div className="flex items-center gap-2">
              <label htmlFor="compare-select" className="font-label-sm text-label-sm text-on-surface-variant">
                Comparar con...
              </label>
              <select
                id="compare-select"
                defaultValue=""
                onChange={(e) => e.target.value && navigate(`/runs/${run.id}/compare/${e.target.value}`)}
                className="bg-surface-container border border-outline-variant rounded-lg px-3 py-1.5 font-body-md text-body-md text-on-surface"
              >
                <option value="" disabled>
                  Elegir run
                </option>
                {others.map((r) => (
                  <option key={r.id} value={r.id}>
                    Run #{r.id} · score {r.avg_score.toFixed(0)} · {new Date(r.created_at).toLocaleString()}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="flex items-center gap-2 text-on-surface-variant font-body-md text-body-md">
            <span className="material-symbols-outlined text-[16px]">calendar_today</span>
            <time dateTime={run.created_at}>
              {new Date(run.created_at).toLocaleString()}
            </time>
          </div>
        </div>
        {/* Large Score Gauge */}
        <div className="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant shadow-sm flex items-center gap-4 min-w-[200px]">
          <div className="relative w-[64px] h-[64px] flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path className="text-surface-container-highest" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
              <path className={globalColors.text} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray={`${run.avg_score}, 100`} strokeLinecap="round" strokeWidth="3"></path>
            </svg>
            <span className={`absolute font-headline-md text-headline-md ${globalColors.text}`}>
              {run.avg_score.toFixed(0)}
            </span>
          </div>
          <div className="flex flex-col">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Score Global</span>
            <span className={`font-body-md text-body-md ${globalColors.text}`}>
              {run.avg_score >= 80 ? "Excelente" : run.avg_score >= 50 ? "Regular" : "Bajo"}
            </span>
          </div>
        </div>
      </header>

      {/* Metric Cards Row */}
      <section aria-label="Run Metrics" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter">
        <DimensionBar label="Tool accuracy" score={run.avg_tool_accuracy} />
        <DimensionBar label="Response quality" score={run.avg_response_quality} />
        <DimensionBar label="Safety" score={run.avg_safety} />
        <DimensionBar label="Score global" score={run.avg_score} isGlobal />
      </section>

      {/* Cases Section */}
      <section aria-labelledby="cases-heading" className="flex flex-col gap-stack-md mt-stack-sm">
        <div className="flex items-center justify-between border-b border-outline-variant pb-2">
          <h2 className="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface" id="cases-heading">
            Casos
          </h2>
          <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-container px-2 py-1 rounded-md">
            {run.results.length} casos
          </span>
        </div>

        {isRunning && run.results.length === 0 && (
          <div className="text-center py-12 text-on-surface-variant font-body-md text-body-md border border-dashed border-outline-variant rounded-2xl bg-surface-container-lowest">
            <span className="material-symbols-outlined text-4xl mb-2 text-outline animate-spin">progress_activity</span>
            <p>Evaluando la suite... los resultados aparecerán aquí al terminar.</p>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {run.results.map((c) => {
            const hasError = !!c.error;
            const cardColors = getFeedbackColors(c.score);
            const isErrorStyle = hasError || c.score < 50;
            
            return (
              <article key={c.id} className={`bg-surface-container-lowest rounded-2xl border shadow-sm overflow-hidden flex flex-col transition-colors duration-200 group relative ${isErrorStyle ? 'border-error/30 hover:border-error/60' : 'border-outline-variant hover:border-primary-fixed-dim'}`}>
                {isErrorStyle && <div className="absolute left-0 top-0 bottom-0 w-1 bg-error"></div>}
                
                <div className={`p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4 ${isErrorStyle ? 'pl-6' : ''}`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full border flex items-center justify-center flex-shrink-0 ${isErrorStyle ? 'bg-error-container/50 border-error/30 text-error' : 'bg-secondary-container/30 border-secondary-container text-secondary'}`}>
                      <span className="material-symbols-outlined text-[18px]">
                        {isErrorStyle ? "error" : "check_circle"}
                      </span>
                    </div>
                    <h3 className={`font-headline-md text-headline-md transition-colors ${isErrorStyle ? 'text-on-surface group-hover:text-error' : 'text-on-surface group-hover:text-primary'}`}>
                      {c.case_name}
                    </h3>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-4 lg:gap-6">
                    <div className="flex gap-4 sm:gap-6 px-4 py-2 bg-surface-container rounded-lg border border-outline-variant/50">
                      <div className="flex flex-col items-center">
                        <span className="font-label-sm text-label-sm text-on-surface-variant mb-0.5">Tool</span>
                        <span className={`font-mono-code text-mono-code ${c.tool_accuracy < 50 ? 'text-error font-medium' : 'text-on-surface'}`}>{c.tool_accuracy.toFixed(0)}</span>
                      </div>
                      <div className="flex flex-col items-center">
                        <span className="font-label-sm text-label-sm text-on-surface-variant mb-0.5">Quality</span>
                        <span className={`font-mono-code text-mono-code ${c.response_quality < 50 ? 'text-error font-medium' : 'text-on-surface'}`}>{c.response_quality.toFixed(0)}</span>
                      </div>
                      <div className="flex flex-col items-center">
                        <span className="font-label-sm text-label-sm text-on-surface-variant mb-0.5">Safety</span>
                        <span className={`font-mono-code text-mono-code ${c.safety < 50 ? 'text-error font-medium' : 'text-on-surface'}`}>{c.safety.toFixed(0)}</span>
                      </div>
                    </div>
                    <div className={`px-4 py-2 rounded-full border flex items-center gap-2 ${cardColors.bgSoft} ${cardColors.border}`}>
                      <span className={`font-label-sm text-label-sm uppercase ${cardColors.text}`}>Score</span>
                      <span className={`font-headline-md text-headline-md ${cardColors.text}`}>{c.score.toFixed(0)}</span>
                    </div>
                  </div>
                </div>

                <div className={`px-5 py-4 flex gap-3 ${isErrorStyle ? 'bg-[#1e1e24] border-t border-error/20' : 'bg-surface border-t border-outline-variant/50'}`}>
                  <span className={`material-symbols-outlined text-[18px] mt-0.5 flex-shrink-0 ${isErrorStyle ? 'text-error' : 'text-on-surface-variant'}`}>
                    {hasError ? 'terminal' : 'psychology'}
                  </span>
                  {hasError ? (
                    <code className="font-mono-code text-mono-code text-error/90 whitespace-pre-wrap break-all">
                      Error: {c.error}
                    </code>
                  ) : (
                    <p className="font-body-md text-body-md text-on-surface-variant">
                      {c.reasoning || "Sin comentarios."}
                    </p>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}
