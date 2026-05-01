const STYLES = {
  critical: "bg-red-500/15 text-red-300 border-red-500/30",
  warning: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  info: "bg-sky-500/15 text-sky-300 border-sky-500/30",
};

export default function SeverityBadge({ severity }) {
  const key = (severity || "info").toLowerCase();
  const style = STYLES[key] || STYLES.info;
  return (
    <span className={`inline-block text-xs uppercase tracking-wide px-2 py-0.5 rounded border ${style}`}>
      {key}
    </span>
  );
}
