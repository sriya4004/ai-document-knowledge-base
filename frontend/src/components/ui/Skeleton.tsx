type Props = {
  className?: string;
};

export default function Skeleton({ className = "" }: Props) {
  return (
    <div className={`relative overflow-hidden rounded-xl bg-slate-200/90 ${className}`}>
      <div
        className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-white/55 to-transparent bg-[length:200%_100%]"
        aria-hidden
      />
    </div>
  );
}
