const META: Record<string, { label: string; sub: string }> = {
  revenue: { label: "Total Revenue", sub: "Completed orders" },
  orders: { label: "Orders", sub: "Successfully fulfilled" },
  customers: { label: "Customers", sub: "Active accounts" },
  products: { label: "Products", sub: "In catalog" },
};

const ORDER = ["revenue", "orders", "customers", "products"];

export function KpiCards({ kpis }: { kpis: Record<string, string> }) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      {ORDER.filter((k) => kpis[k]).map((k) => (
        <div key={k} className="card p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            {META[k]?.label ?? k}
          </div>
          <div className="mt-1 text-2xl font-bold text-slate-900">{kpis[k]}</div>
          <div className="mt-0.5 text-xs text-slate-400">{META[k]?.sub}</div>
        </div>
      ))}
    </div>
  );
}
