import { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: string;
  accent: string;
  icon: LucideIcon;
};

export function MetricTile({ label, value, accent, icon: Icon }: Props) {
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-dashboard">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-600">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
        </div>
        <div className="grid h-10 w-10 place-items-center rounded-lg" style={{ background: accent }}>
          <Icon aria-hidden className="h-5 w-5 text-white" />
        </div>
      </div>
    </section>
  );
}
