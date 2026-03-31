/* Lightweight API client for the Assistant-Live-Demo frontend.
 * Reads base URL and JWT token from Vite env variables.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined;
const TOKEN = import.meta.env.VITE_API_TOKEN as string | undefined;

function buildUrl(path: string): string {
  if (!BASE_URL) throw new Error('VITE_API_BASE_URL is not set');
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${BASE_URL}${p}`;
}

function defaultHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
  return headers;
}

export async function apiGet<T = unknown>(path: string): Promise<T> {
  const res = await fetch(buildUrl(path), { headers: defaultHeaders() });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }
  return (await res.json()) as T;
}

export async function apiPost<T = unknown>(path: string, body: unknown): Promise<T> {
  const res = await fetch(buildUrl(path), {
    method: 'POST',
    headers: defaultHeaders(),
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`POST ${path} failed: ${res.status} ${text}`);
  }
  return (await res.json()) as T;
}

// Convenience: health check
export async function apiHealth(): Promise<{ status: string } | unknown> {
  try {
    return await apiGet('/api/health');
  } catch (e) {
    return { error: (e as Error).message };
  }
}
