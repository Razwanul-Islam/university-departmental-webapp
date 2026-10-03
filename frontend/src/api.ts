export type Item = Record<string, any>;
export type User = {
  id: number;
  email: string;
  name: string;
  user_type: "H" | "T" | "S";
  is_active: boolean;
};
type Tokens = { access: string; refresh: string };

let tokens: Tokens | null = JSON.parse(
  sessionStorage.getItem("tokens") || "null",
);
let refreshing: Promise<void> | null = null;

export function saveTokens(value: Tokens | null) {
  tokens = value;
  if (value) sessionStorage.setItem("tokens", JSON.stringify(value));
  else sessionStorage.removeItem("tokens");
}

export function hasSession() {
  return !!tokens;
}
export function refreshToken() {
  return tokens?.refresh;
}

function explain(value: any): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(explain).join(" ");
  return Object.entries(value || {})
    .map(([key, val]) =>
      key === "detail" || key === "non_field_errors"
        ? explain(val)
        : key.replaceAll("_", " ") + ": " + explain(val),
    )
    .join(" ");
}

export async function api(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<any> {
  const session = tokens;
  const response = await fetch("/api/" + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(tokens ? { Authorization: "Bearer " + tokens.access } : {}),
      ...options.headers,
    },
  });
  if (
    response.status === 401 &&
    session &&
    tokens?.refresh === session.refresh &&
    retry
  ) {
    if (!refreshing) {
      refreshing = (async () => {
        const renewed = await fetch("/api/user/refresh/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh: session.refresh }),
        });
        if (tokens !== session) return;
        if (!renewed.ok) {
          saveTokens(null);
          window.dispatchEvent(new Event("session-expired"));
          throw new Error("Your session expired. Please sign in again.");
        }
        const data = await renewed.json();
        if (tokens === session) saveTokens({ ...session, ...data });
      })().finally(() => {
        refreshing = null;
      });
    }
    await refreshing;
    if (tokens?.refresh !== session.refresh)
      throw new Error("Your session ended. Please sign in again.");
    return api(path, options, false);
  }
  if (response.status === 204) return null;
  const data = await response
    .json()
    .catch(() => ({ detail: "The server could not complete this request." }));
  if (!response.ok) throw new Error(explain(data));
  return data;
}

export function send(path: string, method: string, data?: Item) {
  return api(path, { method, ...(data ? { body: JSON.stringify(data) } : {}) });
}

export async function all(path: string): Promise<Item[]> {
  const items: Item[] = [];
  let page = 1;
  while (true) {
    const data = await api(
      path + (path.includes("?") ? "&" : "?") + "page=" + page,
    );
    if (Array.isArray(data)) return data;
    items.push(...data.results);
    if (!data.next) return items;
    page++;
  }
}
