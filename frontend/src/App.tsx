import { useEffect, useState } from "react";
import { getHealth, predict, type Health, type Prediction } from "./api";

// A working start: shows the API's health and sends lines of text to /predict.
// Replace this page with the real app; keep api.ts as the only place that talks to the API.

const SAMPLE = "Water pipe leaking near the bus stand\nStreet light not working on 5th cross";

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [text, setText] = useState(SAMPLE);
  const [results, setResults] = useState<Prediction[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  async function run() {
    setBusy(true);
    setError("");
    try {
      const items = text
        .split("\n")
        .map((line, i) => ({ id: String(i + 1), text: line.trim() }))
        .filter((item) => item.text);
      setResults(await predict(items));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl p-6 font-sans text-gray-900">
      <header className="mb-6 flex items-baseline justify-between gap-4">
        <h1 className="text-2xl font-semibold">Team app</h1>
        <span
          className={`rounded-full px-3 py-1 text-sm ${
            !health
              ? "bg-red-100 text-red-800"
              : health.model === "real"
                ? "bg-green-100 text-green-800"
                : "bg-amber-100 text-amber-800"
          }`}
          title={health?.note}
        >
          {!health ? "API down (hk run)" : `API ok · model: ${health.model}`}
        </span>
      </header>

      <label className="block text-sm font-medium text-gray-700" htmlFor="items">
        One item per line
      </label>
      <textarea
        id="items"
        className="mt-1 w-full rounded-lg border border-gray-300 p-3 font-mono text-sm"
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={run}
        disabled={busy}
        className="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {busy ? "Predicting…" : "Predict"}
      </button>
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}

      {results.length > 0 && (
        <table className="mt-6 w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-500">
              <th className="py-2">#</th>
              <th className="py-2">Label</th>
              <th className="py-2">Score</th>
              <th className="py-2">Why</th>
            </tr>
          </thead>
          <tbody>
            {results.map((p) => (
              <tr key={p.id} className="border-b border-gray-100">
                <td className="py-2 font-mono">{p.id}</td>
                <td className="py-2 font-medium">{p.label}</td>
                <td className="py-2">{(p.score * 100).toFixed(0)}%</td>
                <td className="py-2 text-gray-600">{p.reasons.join("; ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
