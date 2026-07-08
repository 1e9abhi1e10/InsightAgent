"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Chat } from "@/components/Chat";
import { EvalPanel } from "@/components/EvalPanel";
import { KpiCards } from "@/components/KpiCards";

const GUARDRAILS = ["Read-only SQL", "Table whitelist", "Injection filter", "Ambiguity checks"];

export default function Home() {
  const [kpis, setKpis] = useState<Record<string, string>>({});
  const [samples, setSamples] = useState<string[]>([]);
  const [schema, setSchema] = useState("");
  const [tab, setTab] = useState<"chat" | "eval">("chat");
  const [ready, setReady] = useState(false);
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    Promise.all([api.kpis(), api.samples(), api.schema()])
      .then(([k, s, sc]) => {
        setKpis(k);
        setSamples(s.samples);
        setSchema(sc.schema);
        setReady(true);
      })
      .catch(() => setApiError(true));
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 lg:px-8">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-100 via-cyan-50 to-violet-100 p-8">
        <div className="pointer-events-none absolute -right-16 -top-24 h-72 w-72 rounded-full bg-cyan-300/30 blur-3xl" />
        <span className="badge border-cyan-200 bg-white/70 uppercase tracking-wider text-cyan-700">
          AI-Powered Analytics
        </span>
        <h1 className="mt-3 bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-4xl font-extrabold text-transparent md:text-5xl">
          Ask your data anything.
        </h1>
        <p className="mt-2 max-w-2xl text-slate-600">
          Natural language in, SQL out — grounded answers and live charts from a multi-table
          retail database. Self-correcting queries, groundedness scoring, and an evaluation
          harness built in.
        </p>
      </section>

      {apiError && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Cannot reach the API. Start the backend (uvicorn) or check your deployment.
        </div>
      )}

      {/* KPIs */}
      {ready && (
        <div className="mt-6">
          <KpiCards kpis={kpis} />
        </div>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        {/* Main column */}
        <div className="min-w-0">
          {/* Tabs */}
          <div className="mb-5 inline-flex rounded-full border border-slate-200 bg-white p-1 shadow-sm">
            {(["chat", "eval"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`rounded-full px-5 py-1.5 text-sm font-medium transition ${
                  tab === t
                    ? "bg-indigo-500 text-white shadow-sm"
                    : "text-slate-500 hover:text-slate-800"
                }`}
              >
                {t === "chat" ? "Chat" : "Evaluation"}
              </button>
            ))}
          </div>

          {tab === "chat" ? <Chat samples={samples} /> : <EvalPanel />}
        </div>

        {/* Sidebar */}
        <aside className="space-y-5">
          <div className="card p-5">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Security
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {GUARDRAILS.map((g) => (
                <span
                  key={g}
                  className="badge border-emerald-200 bg-emerald-50 text-emerald-700"
                >
                  {g}
                </span>
              ))}
            </div>
          </div>

          <div className="card p-5">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Schema (5 tables)
            </div>
            <pre className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap text-[11px] leading-relaxed text-slate-500">
              {schema}
            </pre>
          </div>
        </aside>
      </div>

      <footer className="mt-10 border-t border-slate-200 pt-5 text-center text-xs text-slate-400">
        InsightAgent · NL → SQL → grounded answer → chart · FastAPI + Next.js on Vercel
      </footer>
    </main>
  );
}
