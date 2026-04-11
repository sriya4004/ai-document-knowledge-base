import { DashboardAnalytics, QueryResponse, SearchHistoryItem } from "../types";
import apiClient from "./apiClient";

export async function askQuestion(question: string, topK = 5): Promise<QueryResponse> {
  // FastAPI registers this route as /api/v1/query/ (trailing slash); omitting it breaks POST on some stacks.
  const { data } = await apiClient.post<QueryResponse>("/query/", { question, top_k: topK });
  return data;
}

export async function getSearchHistory(): Promise<SearchHistoryItem[]> {
  const { data } = await apiClient.get<SearchHistoryItem[]>("/query/history");
  return data;
}

export async function getDashboardAnalytics(): Promise<DashboardAnalytics> {
  const { data } = await apiClient.get<DashboardAnalytics>("/query/analytics");
  return data;
}
