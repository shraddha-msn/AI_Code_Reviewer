import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createReview } from "../api.js";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    try {
      const review = await createReview(url.trim());
      navigate(`/reviews/${review.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || "Something went wrong";
      setError(typeof detail === "string" ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto text-center pt-12">
      <h1 className="text-4xl font-bold tracking-tight mb-3">
        Review any GitHub repo with AI
      </h1>
      <p className="text-slate-400 mb-8">
        Paste a public repository URL — Gemini will analyze the code and surface
        bugs, quality issues, and concrete fixes.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <input
          type="url"
          required
          placeholder="https://github.com/owner/repo"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="flex-1 px-4 py-3 rounded-md bg-slate-900 border border-slate-700 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 rounded-md bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-slate-950 transition"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </form>

      {loading && (
        <p className="mt-6 text-slate-400 text-sm animate-pulse">
          Fetching files and running review — this can take 20–40 seconds.
        </p>
      )}

      {error && (
        <div className="mt-6 text-left bg-red-500/10 border border-red-500/30 text-red-300 rounded-md px-4 py-3 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
