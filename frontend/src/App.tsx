import { Navigate, Route, Routes } from "react-router-dom";
import { RunList } from "./components/RunList";
import { RunDetail } from "./components/RunDetail";
import { RunCompare } from "./components/RunCompare";

export default function App() {
  return (
    <>
      <header className="bg-surface-container-lowest border-b border-outline-variant shadow-sm w-full sticky top-0 z-50">
        <div className="flex justify-between items-center h-16 w-full px-gutter max-w-container-max mx-auto">
          <div className="flex items-center gap-2">
            <div className="font-headline-lg text-headline-lg flex tracking-tight">
              <span className="text-on-surface font-extrabold">agent</span>
              <span className="text-primary font-extrabold">eval</span>
            </div>
            <span className="hidden md:inline-block ml-4 text-outline font-label-sm text-label-sm border-l border-outline-variant pl-4">
              Evaluación de agentes LLM con function calling
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="text-on-surface-variant hover:bg-surface-container-low transition-all duration-200 p-2 rounded-full active:scale-95 flex items-center justify-center">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="text-on-surface-variant hover:bg-surface-container-low transition-all duration-200 p-2 rounded-full active:scale-95 flex items-center justify-center">
              <span className="material-symbols-outlined">help_outline</span>
            </button>
          </div>
        </div>
      </header>

      <Routes>
        <Route path="/" element={<RunList />} />
        <Route path="/runs/:id" element={<RunDetail />} />
        <Route path="/runs/:id/compare/:otherId" element={<RunCompare />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <footer className="bg-surface-container border-t border-outline-variant w-full mt-auto">
        <div className="flex flex-col md:flex-row justify-between items-center w-full px-gutter max-w-container-max mx-auto py-stack-lg gap-6">
          <div className="flex flex-col items-center md:items-start gap-2">
            <div className="font-headline-md text-headline-md font-bold flex tracking-tight">
              <span className="text-on-surface">agent</span><span className="text-primary">eval</span>
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant text-center md:text-left">
              © {new Date().getFullYear()} agenteval. Evaluación de agentes LLM con function calling.
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
