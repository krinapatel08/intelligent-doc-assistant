const API_BASE = "https://ominous-cod-v6gwqgpr45q36ggx-8000.app.github.dev";

export async function apiRequest(path, method = "GET", body = null, token = null) {
  try {
    const headers = {};

    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (!(body instanceof FormData)) headers["Content-Type"] = "application/json";

    const config = {
      method,
      headers,
    };

    if (body) config.body = body instanceof FormData ? body : JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, config);
    const data = await res.json();

    if (!res.ok) {
      return { error: data.detail || data.error || "Something went wrong" };
    }

    return { data };
  } catch (err) {
    return { error: err.message || "Network error" };
  }
}

export const authService = {
  login: (username, password) =>
  apiRequest("/api/auth/login/", "POST", { username, password }),


  register: (email, password, username) =>
    apiRequest("/api/auth/register/", "POST", { email, password, username }),

  getToken: () => localStorage.getItem("access_token"),

  setToken: (token) => localStorage.setItem("access_token", token),

  clearToken: () => localStorage.removeItem("access_token"),

  isAuthenticated: () => !!localStorage.getItem("access_token"),
};

export const documentService = {
  upload: (file, token) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest("/api/upload/", "POST", formData, token);
  },

  list: (token) => apiRequest("/api/documents/", "GET", null, token),
};

export const chatService = {
  ask: (documentId, question, token) =>
    apiRequest("/api/ask/", "POST", { document_id: documentId, question }, token),

  getHistory: (documentId, token) =>
    apiRequest(`/api/chats/${documentId}/`, "GET", null, token),
};
