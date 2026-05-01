import { Link, NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Results from "./pages/Results.jsx";
import History from "./pages/History.jsx";

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `px-3 py-1.5 rounded-md text-sm transition ${
          isActive
            ? "bg-slate-800 text-white"
            : "text-slate-400 hover:text-white hover:bg-slate-800/60"
        }`
      }
    >
      {children}
    </NavLink>
  );
}

export default function App() {
  return (
    <div className="min-h-full flex flex-col">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            <span className="text-emerald-400">{"</>"}</span> AI Code Reviewer
          </Link>
          <nav className="flex gap-1">
            <NavItem to="/">Home</NavItem>
            <NavItem to="/history">History</NavItem>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/reviews/:id" element={<Results />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>

      <footer className="border-t border-slate-800 text-center text-xs text-slate-500 py-4">
        Powered by Gemini · FastAPI · React
      </footer>
    </div>
  );
}
