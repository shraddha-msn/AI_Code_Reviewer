import SeverityBadge from "./SeverityBadge.jsx";

export default function ReviewCard({ item, kind }) {
  return (
    <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/50">
      <div className="flex items-start justify-between gap-3 mb-2">
        <h4 className="font-medium text-slate-100">{item.title}</h4>
        {item.severity && <SeverityBadge severity={item.severity} />}
      </div>

      {(item.file || item.line) && (
        <div className="text-xs text-slate-400 font-mono mb-2">
          {item.file}
          {item.line ? `:${item.line}` : ""}
        </div>
      )}

      {item.description && (
        <p className="text-sm text-slate-300 mb-2 whitespace-pre-wrap">{item.description}</p>
      )}

      {kind === "bug" && item.suggested_fix && (
        <div className="mt-2">
          <div className="text-xs font-semibold text-emerald-400 mb-1">Suggested fix</div>
          <p className="text-sm text-slate-300 whitespace-pre-wrap">{item.suggested_fix}</p>
        </div>
      )}

      {kind === "suggestion" && (item.before || item.after) && (
        <div className="mt-2 grid md:grid-cols-2 gap-2">
          {item.before && (
            <div>
              <div className="text-xs font-semibold text-red-400 mb-1">Before</div>
              <pre className="text-xs bg-slate-950/70 border border-slate-800 rounded p-2 overflow-x-auto"><code>{item.before}</code></pre>
            </div>
          )}
          {item.after && (
            <div>
              <div className="text-xs font-semibold text-emerald-400 mb-1">After</div>
              <pre className="text-xs bg-slate-950/70 border border-slate-800 rounded p-2 overflow-x-auto"><code>{item.after}</code></pre>
            </div>
          )}
        </div>
      )}

      {kind === "suggestion" && item.explanation && (
        <p className="text-sm text-slate-400 mt-2 italic">{item.explanation}</p>
      )}
    </div>
  );
}
