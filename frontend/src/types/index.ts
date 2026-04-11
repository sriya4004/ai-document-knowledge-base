export type Document = {
  id: number;
  title: string;
  category: string;
  source: string;
  file_name?: string | null;
  stored_file_path?: string | null;
  /** Original upload format: pdf or txt when uploaded from file */
  file_type?: string | null;
  has_original_file?: boolean;
  content: string;
  department: string;
  owner_id: number;
  created_at: string;
};

export type SourceChunk = {
  document_id: number;
  title: string;
  snippet: string;
  category: string;
  /** Legacy preview field; mirrors snippet when provided by the API */
  content?: string;
  score: number;
  metadata: Record<string, string | number | boolean | null>;
};

export type QueryResponse = {
  answer: string;
  sources: SourceChunk[];
};

export type SearchHistoryItem = {
  id: number;
  query_text: string;
  response_text: string;
  created_at: string;
};

export type AnalyticsItem = {
  label: string;
  count: number;
};

export type DashboardAnalytics = {
  most_searched_queries: AnalyticsItem[];
  top_documents: AnalyticsItem[];
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type User = {
  id: number;
  email: string;
  role: "admin" | "employee";
  department: string;
  created_at: string;
};
