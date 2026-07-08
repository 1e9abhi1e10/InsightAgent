"use client";

import { useState } from "react";
import { api, EvalReport } from "@/lib/api";

export function EvalPanel() {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      setReport(await api.runEval());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Evaluation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">
        Runs a golden dataset scoring SQL correctness, groundedness, ambiguity handling,
        guardrails, and latency. Ground truth is computed live from the database.
      </p>
      <button
        onClick={run}
        disabled={loading}
        className="pill-btn disabled:opacity-50"
      >
        {loading ? "Running evaluation…" : "▶ Run evaluation"}
      </button>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error} — the free-tier API may be rate-limited; wait a minute and retry.
        </div>
      )}

      {report && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <Stat label="Pass Rate" value={`${Math.round(report.pass_rate * 100)}%`} sub={`${report.passed}/${report.total} cases`} />
            <Stat label="Avg Latency" value={`${(report.avg_latency_ms / 1000).toFixed(1)}s`} sub="end-to-end" />
            <Stat label="Avg Groundedness" value={`${Math.round(report.avg_groundedness * 100)}%`} sub="claims supported" />
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-indigo-50 text-slate-700">
                <tr>
                  <th className="px-3 py-2">Result</th>
                  <th className="px-3 py-2">Category</th>
                  <th className="px-3 py-2">Question</th>
                  <th className="px-3 py-2">Latency</th>
                  <th className="px-3 py-2">Grounded</th>
                </tr>
              </thead>
              <tbody>
                {report.results.map((r, i) => (
                  <tr key={i} className={i % 2 ? "bg-slate-50" : "bg-white"}>
                    <td className="px-3 py-1.5">{r.passed ? "✅" : "❌"}</td>
                    <td className="px-3 py-1.5 text-slate-500">{r.category}</td>
                    <td className="px-3 py-1.5 text-slate-600">{r.question}</td>
                    <td className="px-3 py-1.5 text-slate-500">{(r.latency_ms / 1000).toFixed(1)}s</td>
                    <td className="px-3 py-1.5 text-slate-500">
                      {r.groundedness != null ? `${Math.round(r.groundedness * 100)}%` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="card p-4">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-bold text-slate-900">{value}</div>
      <div className="mt-0.5 text-xs text-slate-400">{sub}</div>
    </div>
  );
}
