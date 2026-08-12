const BASE_URL = "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

export const widgetsApi = {
  list: () => request("/widgets"),
  create: (title) =>
    request("/widgets", { method: "POST", body: JSON.stringify({ title }) }),
  toggle: (id) => request(`/widgets/${id}/toggle`, { method: "POST" }),
};

export const notesApi = {
  list: () => request("/notes"),
  create: (title, body) =>
    request("/notes", { method: "POST", body: JSON.stringify({ title, body }) }),
  updateBody: (id, body) =>
    request(`/notes/${id}`, { method: "POST", body: JSON.stringify({ body }) }),
};

export const bookmarksApi = {
  list: () => request("/bookmarks"),
  create: (url, title) =>
    request("/bookmarks", { method: "POST", body: JSON.stringify({ url, title }) }),
  rename: (id, title) =>
    request(`/bookmarks/${id}`, { method: "POST", body: JSON.stringify({ title }) }),
};
