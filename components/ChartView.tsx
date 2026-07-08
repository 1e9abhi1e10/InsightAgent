"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AskResponse } from "@/lib/api";

const COLORS = ["#6366f1", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#3b82f6"];

const AXIS = "#64748b";
const GRID = "rgba(100,116,139,0.15)";

const tooltipStyle = {
  background: "#ffffff",
  border: "1px solid #e2e8f0",
  borderRadius: 12,
  color: "#1e293b",
  fontSize: 12,
  boxShadow: "0 4px 16px rgba(15,23,42,0.08)",
};

function toData(res: AskResponse) {
  return res.rows.map((row) => {
    const obj: Record<string, string | number | null> = {};
    res.columns.forEach((c, i) => (obj[c] = row[i]));
    return obj;
  });
}

export function ChartView({ res }: { res: AskResponse }) {
  if (res.rows.length === 0) return null;

  const type = res.chart_type;
  const graphable = type === "bar" || type === "line" || type === "pie";

  // Non-graphable results: show a table for tabular/multi-row data, nothing for
  // a single scalar answer (the text already states it).
  if (!graphable) {
    return type === "table" || res.rows.length > 1 ? <DataTable res={res} /> : null;
  }

  const data = toData(res);
  const cfg = res.chart_config ?? {};
  const x = cfg.x_column && res.columns.includes(cfg.x_column) ? cfg.x_column : res.columns[0];
  const y =
    cfg.y_column && res.columns.includes(cfg.y_column)
      ? cfg.y_column
      : res.columns[1] ?? res.columns[0];
  const title = cfg.title ?? "Results";

  return (
    <div className="mt-3 min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-slate-50/60 p-3">
      <div className="mb-2 text-sm font-semibold text-slate-700">{title}</div>
      <ResponsiveContainer width="100%" height={300}>
        {type === "bar" ? (
          <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
            <XAxis dataKey={x} tick={{ fill: AXIS, fontSize: 12 }} />
            <YAxis tick={{ fill: AXIS, fontSize: 12 }} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(99,102,241,0.08)" }} />
            <Bar dataKey={y} radius={[6, 6, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        ) : type === "line" ? (
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
            <XAxis dataKey={x} tick={{ fill: AXIS, fontSize: 12 }} />
            <YAxis tick={{ fill: AXIS, fontSize: 12 }} />
            <Tooltip contentStyle={tooltipStyle} />
            {res.columns.filter((c) => c !== x).length > 1 && (
              <Legend wrapperStyle={{ fontSize: 12, color: AXIS }} />
            )}
            {res.columns
              .filter((c) => c !== x)
              .map((col, i) => {
                const isForecast = col.toLowerCase().includes("forecast");
                return (
                  <Line
                    key={col}
                    type="monotone"
                    dataKey={col}
                    stroke={isForecast ? "#f59e0b" : COLORS[i % COLORS.length]}
                    strokeWidth={3}
                    strokeDasharray={isForecast ? "6 4" : undefined}
                    dot={{ r: 3 }}
                    connectNulls={false}
                  />
                );
              })}
          </LineChart>
        ) : (
          <PieChart>
            <Tooltip contentStyle={tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 12, color: AXIS }} />
            <Pie
              data={data}
              dataKey={y}
              nameKey={x}
              cx="50%"
              cy="50%"
              outerRadius={95}
              label={{ fill: "#475569", fontSize: 11 }}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export function DataTable({ res }: { res: AskResponse }) {
  return (
    <div className="mt-3 overflow-x-auto rounded-xl border border-slate-200">
      <table className="w-full text-left text-sm">
        <thead className="bg-indigo-50 text-slate-700">
          <tr>
            {res.columns.map((c) => (
              <th key={c} className="px-3 py-2 font-semibold">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {res.rows.map((row, ri) => (
            <tr key={ri} className={ri % 2 ? "bg-slate-50" : "bg-white"}>
              {row.map((cell, ci) => (
                <td key={ci} className="px-3 py-1.5 text-slate-600">
                  {cell === null ? "—" : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
