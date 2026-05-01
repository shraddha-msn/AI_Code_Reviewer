import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getReview } from "../api.js";
import ReviewCard from "../components/ReviewCard.jsx";

const TABS = [
  { key: "bugs", label: "Bugs" },
  { key: "quality_issues", label: "Quality" },
  { key: "suggestions", label: "Suggestions" },
];

function ScoreBadge({ score }) {
  const tone =
    score >= 8 ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10"
    : score >= 5 ? "text-amber-400 border-amber-500/40 bg-amber-500/10"
    : "text-red-400 border-red-500/40 bg-red-500/10";
  return (
    <div className={`px-4 py-2 rounded-lg border ${tone} text-center`}>
      <div className="text-3xl font-bold leading-none">{score ?? "?"}</div>
      <div className="text-xs uppercase tracking-wide">/ 10</div>
    </div>
  );
}

export default function Results() {
  const { id } = useParams();
  const [review, setReview] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("bugs");

  useEffect(() => {
    getReview(id)
      .then(setReview)
      .catch((e) => setError(e.response?.data?.detail || e.message));
  }, [id]);

  if (error) {
    return (
      <div className="text-red-300 bg-red-500/10 border border-red-500/30 rounded-md p-4">
        {error}
      </div>
    );
  }
  if (!review) {
    return <div className="text-slate-400 animate-pulse">Loading…</div>;
  }

  const r = review.result || {};
  const items = r[tab] || [];
  const kindByTab = { bugs: "bug", quality_issues: "quality", suggestions: "suggestion" };

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <Link to="/" className="text-xs text-slate-500 hover:text-slate-300">← New review</Link>
          <h2 className="text-2xl font-semibold mt-1">
            {review.owner}/{review.repo}
          </h2>
          <a
            href={review.repo_url}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-emerald-400 hover:underline break-all"
          >
            {review.repo_url}
          </a>
        </div>
        <ScoreBadge score={r.overall_score} />
      </div>

      {r.summary && (
        <p className="text-slate-300 bg-slate-900/50 border border-slate-800 rounded-lg p-4 mb-6">
          {r.summary}
        </p>
      )}

      <div className="flex gap-1 border-b border-slate-800 mb-4">
        {TABS.map((t) => {
          const count = (r[t.key] || []).length;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 text-sm border-b-2 transition ${
                tab === t.key
                  ? "border-emerald-500 text-emerald-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              {t.label}{" "}
              <span className="text-xs text-slate-500">({count})</span>
            </button>
          );
        })}
      </div>

      <div className="space-y-3">
        {items.length === 0 ? (
          <p className="text-slate-500 text-sm italic">Nothing here — clean code.</p>
        ) : (
          items.map((item, i) => (
            <ReviewCard key={i} item={item} kind={kindByTab[tab]} />
          ))
        )}
      </div>
    </div>
  );
}
