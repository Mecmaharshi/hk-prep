// The API, as the frontend sees it. The shapes mirror contracts/api.py: when the lead changes
// that file, update the types here too (see the API tab on http://localhost:8000/board).

export type Item = { id: string; text: string };
export type Prediction = { id: string; label: string; score: number; reasons: string[] };
export type Health = { status: string; model: "real" | "fake" | string; note: string };

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(API_URL + path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText} from ${path}`);
  return response.json() as Promise<T>;
}

export const getHealth = () => call<Health>("/health");

export const predict = (items: Item[]) =>
  call<{ predictions: Prediction[] }>("/predict", {
    method: "POST",
    body: JSON.stringify({ items }),
  }).then((r) => r.predictions);
