import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type RunComparison } from "../api";
import { ScoreBadge } from "./Score";

function DeltaBadge({ delta }: { delta: number | null }) {
  if (delta === null) {
    return <span className="font-mono-code text-mono-code text-on-surface-variant">—</span>;
  }
  const colors =
    delta > 0
      ? "bg-feedback-green-bg text-feedback-green-text"
      : delta < 0
        ? "bg-feedback-red-bg text-feedback-red-text"
        : "bg-surface-container text-on-surface-variant";
  const icon = delta > 0 ? "trending_up" : delta < 0 ? "trending_down" : "trending_flat";
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full ${colors} font-mono-code text-mono-code font-bold`}>
      <span className="material-symbols-outlined text-[14px]">{icon}</span>
      {delta > 0 ? "+" : ""}
      {delta.toFixed(1)}
    </span>
  );
}

export function RunCompare() {
  const navigate = useNavigate();
  const { id, otherId } = useParams();
  const [comparison, setComparison] = useState<RunComparison | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .compareRuns(Number(id), Number(otherId))
      .then(setComparison)
      .catch((e) => setError(String(e)));
  }, [id, otherId]);

  if (error) {
    return (
      <main className="max-w-container-max mx-auto px-margin-mobile md:px-gutter py-stack-lg flex flex-col gap-stack-lg">
        <div className="bg-error-container text-on-error-container p-4 rounded-lg font-body-md shadow-sm">{error}</div>
        <button onClick={() => navigate("/")} className="self-start mt-4 px-4 py-2 bg-surface-container rounded-lg font-label-sm text-on-surface">
          Volver
        </button>
      </main>
    );
  }

  if (!comparison) {
    return (
      <main className="max-w-container-max mx-auto px-margin-mobile md:px-gutter py-stack-lg flex flex-col gap-stack-lg items-center justify-center min-h-[50vh]">
        <div className="font-body-md text-on-surface-variant">Cargando...</div>
      </main>
    );
  }

  const { run_a, run_b, cases } = comparison;
  const deltaAvg = run_b.avg_score - run_a.avg_score;

  return (
    <main className="max-w-container-max mx-auto px-margin-mobile md:px-gutter py-stack-lg flex flex-col gap-stack-lg w-full flex-grow">
      <nav aria-label="Back">
        <button
          onClick={() => navigate(`/runs/${run_a.id}`)}
          className="inline-flex items-center gap-1.5 text-on-surface-variant hover:text-primary transition-colors duration-200 font-label-sm text-label-sm bg-surface-container-lowest px-3 py-1.5 rounded-full border border-outline-variant shadow-sm w-fit group"
        >
          <span className="material-symbols-outlined text-[16px] group-hover:-translate-x-0.5 transition-transform">arrow_back</span>
          Volver al run #{run_a.id}
        </button>
      </nav>

      <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-stack-md border-b border-outline-variant pb-stack-lg">
        <div className="flex flex-col gap-3">
          <h1 className="font-headline-lg-mobile md:font-headline-xl text-headline-lg-mobile md:text-headline-xl text-on-surface">
            {run_a.suite_name}
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Run #{run_a.id} ({new Date(run_a.created_at).toLocaleString()}) vs run #{run_b.id} (
            {new Date(run_b.created_at).toLocaleString()})
          </p>
        </div>
        <div className="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant shadow-sm flex items-center gap-4">
          <div className="flex flex-col items-center">
            <span className="font-label-sm text-label-sm text-on-surface-variant">Run #{run_a.id}</span>
            <ScoreBadge score={run_a.avg_score} />
          </div>
          <span className="material-symbols-outlined text-on-surface-variant">arrow_forward</span>
          <div className="flex flex-col items-center">
            <span className="font-label-sm text-label-sm text-on-surface-variant">Run #{run_b.id}</span>
            <ScoreBadge score={run_b.avg_score} />
          </div>
          <DeltaBadge delta={Math.round(deltaAvg * 10) / 10} />
        </div>
      </header>

      <section className="bg-surface-container-lowest rounded-2xl shadow-level-1 border border-outline-variant overflow-hidden">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Caso</th>
                <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Run #{run_a.id}</th>
                <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Run #{run_b.id}</th>
                <th className="py-4 px-6 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-center">Δ score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {cases.map((c) => (
                <tr key={c.case_name}>
                  <td className="py-4 px-6 font-mono-code text-mono-code text-on-surface font-medium">{c.case_name}</td>
                  <td className="py-4 px-6 text-right font-mono-code text-mono-code text-on-surface-variant">
                    {c.a ? c.a.score.toFixed(1) : "solo en el otro run"}
                  </td>
                  <td className="py-4 px-6 text-right font-mono-code text-mono-code text-on-surface-variant">
                    {c.b ? c.b.score.toFixed(1) : "solo en el otro run"}
                  </td>
                  <td className="py-4 px-6 text-center">
                    <DeltaBadge delta={c.delta_score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
