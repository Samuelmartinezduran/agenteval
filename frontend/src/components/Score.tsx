// Componentes de visualización de puntuaciones.

function colorClasses(score: number): string {
  if (score >= 80) return "bg-green-100 text-green-800";
  if (score >= 50) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

function barColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 50) return "bg-yellow-500";
  return "bg-red-500";
}

export function ScoreBadge({ score }: { score: number }) {
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-sm font-semibold ${colorClasses(score)}`}>
      {score.toFixed(1)}
    </span>
  );
}

export function DimensionBar({ label, score }: { label: string; score: number }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm text-gray-600">
        <span>{label}</span>
        <span className="font-medium">{score.toFixed(0)}</span>
      </div>
      <div className="h-2 w-full rounded bg-gray-200">
        <div
          className={`h-2 rounded ${barColor(score)}`}
          style={{ width: `${Math.max(0, Math.min(100, score))}%` }}
        />
      </div>
    </div>
  );
}
