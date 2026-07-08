"use client";

import { AskResponse } from "@/lib/api";
import { Badges } from "./Badges";
import { ChartView } from "./ChartView";
import { SqlBlock } from "./SqlBlock";

export type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  data?: AskResponse;
};

function csvFromRes(res: AskResponse): string {
  const header = res.columns.join(",");
  const body = res.rows
    .map((r) => r.map((c) => (c === null ? "" : JSON.stringify(c))).join(","))
    .join("\n");
  return `${header}\n${body}`;
}

export function MessageCard({ msg }: { msg: ChatMessage }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end animate-fade-up">
        <div className="max-w-[80%] break-words rounded-2xl rounded-br-sm bg-indigo-500 px-4 py-2.5 text-white shadow-sm">
          {msg.content}
        </div>
      </div>
    );
  }

  const res = msg.data;

  const downloadCsv = () => {
    if (!res) return;
    const blob = new Blob([csvFromRes(res)], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "query_results.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-3 animate-fade-up">
      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 text-sm text-white">
        ✦
      </div>
      <div className="min-w-0 flex-1">
        <div className="card min-w-0 p-4">
          <p className="whitespace-pre-wrap break-words leading-relaxed text-slate-700">
            {msg.content}
          </p>
          {res && (
            <div className="mt-3 space-y-3">
              <Badges res={res} />
              <ChartView res={res} />
              {res.sql && <SqlBlock sql={res.sql} />}
              {res.rows.length > 0 && (
                <div>
                  <button
                    onClick={downloadCsv}
                    className="text-xs text-slate-500 transition hover:text-slate-800"
                  >
                    ⬇ Download results (CSV)
                  </button>
                </div>
              )}
              {res.timings && Object.keys(res.timings).length > 1 && (
                <details className="text-xs text-slate-400">
                  <summary className="cursor-pointer hover:text-slate-600">
                    Latency breakdown
                  </summary>
                  <div className="mt-1 max-w-xs space-y-0.5 font-mono">
                    {Object.entries(res.timings).map(([k, v]) => (
                      <div key={k} className="flex justify-between gap-4">
                        <span className="text-slate-500">{k.replace("_ms", "")}</span>
                        <span>{Math.round(v)} ms</span>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
