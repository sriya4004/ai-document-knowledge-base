import { ReactNode } from "react";

type Props = {
  title: string;
  description: string;
  icon?: ReactNode;
};

export default function EmptyState({ title, description, icon }: Props) {
  return (
    <div className="animate-fade-in rounded-2xl border border-dashed border-slate-200 bg-gradient-to-b from-slate-50/80 to-white px-8 py-14 text-center shadow-inner">
      {icon && (
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-slate-400 shadow-card ring-1 ring-slate-100">
          {icon}
        </div>
      )}
      <h4 className="text-base font-semibold tracking-tight text-slate-800">{title}</h4>
      <p className="mx-auto mt-2 max-w-sm text-pretty text-sm leading-relaxed text-slate-500">{description}</p>
    </div>
  );
}
