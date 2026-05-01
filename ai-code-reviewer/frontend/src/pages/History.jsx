import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listReviews } from "../api.js";

export default function History() {
  const [reviews, setReviews] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listReviews()
      .then(setReviews)
      .catch((e) => setError(e.response?.data?.detail || e.message));
  }, []);

  if (error) {
    return (
      <div className="text-red-300 bg-red-500/10 border border-red-500/30 rounded-md p-4">
        {error}
      </div>
    );
  }
  if (!reviews) {
    return <div className="text-slate-400 animate-pulse">Loading…</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">Past reviews</h2>
      {reviews.length === 0 ? (
        <p className="text-slate-500 text-sm">No reviews yet. Run one from the home page.</p>
      ) : (
        <ul className="space-y-2">
          {reviews.map((r) => (
            <li key={r.id}>
              <Link
                to={`/reviews/${r.id}`}
                className="block border border-slate-800 hover:border-emerald-500/40 hover:bg-slate-900/60 rounded-lg p-4 transition"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div className="font-medium truncate">
                      {r.owner}/{r.repo}
                    </div>
                    <div className="text-xs text-slate-500 truncate">{r.repo_url}</div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs text-slate-400">
                      {new Date(r.created_at).toLocaleString()}
                    </span>
                    <span className="text-emerald-400 font-mono text-sm">
                      {r.overall_score ?? "?"}/10
                    </span>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
