

export function getFeedbackColors(score: number): { bg: string; text: string; dot: string; border: string; bgSoft: string } {
  if (score >= 80) return { bg: "bg-feedback-green-bg", text: "text-feedback-green-text", dot: "bg-feedback-green-text", border: "border-feedback-green-text", bgSoft: "bg-feedback-green-bg/30" };
  if (score >= 50) return { bg: "bg-feedback-amber-bg", text: "text-feedback-amber-text", dot: "bg-feedback-amber-text", border: "border-feedback-amber-text", bgSoft: "bg-feedback-amber-bg/30" };
  return { bg: "bg-feedback-red-bg", text: "text-feedback-red-text", dot: "bg-feedback-red-text", border: "border-feedback-red-text", bgSoft: "bg-feedback-red-bg/30" };
}

export function ScoreBadge({ score }: { score: number }) {
  const colors = getFeedbackColors(score);
  return (
    <span className={`inline-flex items-center justify-center px-3 py-1 rounded-full ${colors.bg} ${colors.text} font-mono-code text-mono-code font-bold min-w-[3rem]`}>
      {score.toFixed(0)}
    </span>
  );
}

export function DimensionBar({ label, score, isGlobal = false }: { label: string; score: number; isGlobal?: boolean }) {
  const colors = getFeedbackColors(score);
  return (
    <div className={`bg-surface-container-lowest rounded-2xl p-5 border border-outline-variant shadow-sm flex flex-col gap-4 ${isGlobal ? 'relative overflow-hidden' : ''}`}>
      {isGlobal && <div className={`absolute inset-0 bg-gradient-to-br from-feedback-green-bg to-transparent pointer-events-none`}></div>}
      <div className="flex justify-between items-baseline relative z-10">
        <h3 className="font-label-sm text-label-sm text-on-surface-variant">{label}</h3>
        <div className="flex items-baseline gap-0.5">
          <span className={`font-headline-md text-headline-md ${isGlobal ? colors.text : 'text-on-surface'}`}>{score.toFixed(0)}</span>
          <span className="font-label-sm text-label-sm text-on-surface-variant">/100</span>
        </div>
      </div>
      <div className="w-full h-1.5 bg-surface-container-highest rounded-full overflow-hidden relative z-10">
        <div className={`h-full rounded-full ${colors.dot}`} style={{ width: `${Math.max(0, Math.min(100, score))}%` }} />
      </div>
    </div>
  );
}
