import axios, { AxiosError } from "axios";
import toast from "react-hot-toast";
import { clearAccessToken, getAccessToken } from "../utils/auth";

const rawBase =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || "http://localhost:8000/api/v1";
const API_BASE_URL = rawBase.replace(/\/+$/, "");

function formatApiDetail(detail: unknown): string | undefined {
  if (detail == null) return undefined;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (item && typeof item === "object" && "msg" in item) {
        return String((item as { msg?: string }).msg ?? JSON.stringify(item));
      }
      return JSON.stringify(item);
    });
    return parts.join("; ");
  }
  if (typeof detail === "object") return JSON.stringify(detail);
  return String(detail);
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.debug("[api]", response.config.method?.toUpperCase(), response.config.url, response.status);
    }
    return response;
  },
  (error: AxiosError<{ detail?: unknown }>) => {
    const status = error.response?.status;
    const detail = formatApiDetail(error.response?.data?.detail);

    if (import.meta.env.DEV) {
      console.error("[api error]", status, error.config?.method, error.config?.url, detail ?? error.message);
    }

    if (status === 401) {
      clearAccessToken();
      toast.error("Session expired. Please sign in again.");
    } else if (detail) {
      toast.error(detail);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
