// src/client-config.ts (or wherever you init your app)
import { client } from "@/client/client.gen";

// dedupe concurrent refreshes — if 5 requests 401 at once, only refresh once
let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = fetch(`${import.meta.env.VITE_API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include", // sends the httpOnly refresh cookie, receives new cookies via Set-Cookie
    })
      .then((res) => res.ok)
      .catch(() => false)
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL,
  credentials: "include",
});

// On 401, refresh once, then retry the original request
client.interceptors.response.use(async (response, request) => {
  if (response.status !== 401) return response;

  // avoid infinite loop: don't try to refresh a failed refresh request itself
  if (request.url.includes("/auth/refresh")) return response;

  // avoid re-retrying a request we already retried once
  if (request.headers.get("X-Retried") === "true") return response;

  const refreshed = await refreshAccessToken();
  if (!refreshed) {
    return response; // refresh failed — surface original 401 (redirect to login etc.)
  }

  // Buffer + clone: request.body is a stream and can only be read once,
  // so GET/DELETE (no body) can be retried directly, but POST/PUT/PATCH
  // need the body re-attached explicitly.
  const retryRequest = new Request(request.url, {
    method: request.method,
    headers: new Headers(request.headers),
    body: request.body ? await request.clone().blob() : undefined,
    credentials: request.credentials,
  });
  retryRequest.headers.set("X-Retried", "true");

  return fetch(retryRequest); // new access-token cookie is sent automatically
});
