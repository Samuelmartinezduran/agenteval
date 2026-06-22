import { useState } from "react";
import { RunList } from "./components/RunList";
import { RunDetail } from "./components/RunDetail";

export default function App() {
  const [openRun, setOpenRun] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-4xl px-6 py-4">
          <h1 className="text-lg font-bold">
            agent<span className="text-blue-600">eval</span>
          </h1>
          <p className="text-sm text-gray-500">
            Evaluación de agentes LLM con function calling
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-8">
        {openRun === null ? (
          <RunList onOpen={setOpenRun} />
        ) : (
          <RunDetail runId={openRun} onBack={() => setOpenRun(null)} />
        )}
      </main>
    </div>
  );
}
