import { AskResponse } from "@/lib/api";

export function Badges({ res }: { res: AskResponse }) {
  const badges: React.ReactNode[] = [];
  const total = res.timings?.total_ms;

  if (total) {
    badges.push(
      <span key="lat" className="badge border-indigo-200 bg-indigo-50 text-indigo-700">
        ⚡ {(total / 1000).toFixed(1)}s
      </span>
    );
  }

  if (res.groundedness_label && res.groundedness != null) {
    const label = res.groundedness_label;
    const color =
      label === "High"
        ? "border-emerald-200 bg-emerald-50 text-emerald-700"
        : label === "Medium"
        ? "border-amber-200 bg-amber-50 text-amber-700"
        : "border-red-200 bg-red-50 text-red-700";
    badges.push(
      <span key="ground" className={`badge ${color}`}>
        ◆ Groundedness: {label} ({Math.round(res.groundedness * 100)}%)
      </span>
    );
  }

  if (res.cached) {
    badges.push(
      <span key="cache" className="badge border-cyan-200 bg-cyan-50 text-cyan-700">
        ⚡ Cached
      </span>
    );
  }

  if (res.repair_attempts > 0) {
    badges.push(
      <span key="repair" className="badge border-amber-200 bg-amber-50 text-amber-700">
        🔧 Auto-repaired ({res.repair_attempts}×)
      </span>
    );
  }

  if (badges.length === 0) return null;
  return <div className="flex flex-wrap gap-2">{badges}</div>;
}
