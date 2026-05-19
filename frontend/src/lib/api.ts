const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Headline = {
  article_id: string;
  headline: string;
  summary: string;
  url: string;
  publisher: string;
  published_at: string;
  sentiment_score: number;
};

export type TimePoint = {
  timestamp: string;
  article_volume: number;
  social_volume: number;
  average_sentiment: number;
};

export type GraphData = {
  nodes: Array<{ id: string; label: string; name: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${path}`);
  }
  return response.json();
}

export async function loadDashboardData() {
  const [latest, publishers, products, social, timeseries, sentiment] = await Promise.all([
    getJson<Headline[]>("/news/latest?limit=20"),
    getJson<Array<{ publisher: string; article_count: number }>>("/publishers/top"),
    getJson<Array<{ product: string; mentions: number }>>("/products/trending"),
    getJson<Array<{ text: string; platform: string; engagement_score: number; sentiment_score: number }>>("/social/buzz"),
    getJson<TimePoint[]>("/trends/timeseries"),
    getJson<Array<{ timestamp: string; average_sentiment: number }>>("/sentiment/timeline")
  ]);

  return { latest, publishers, products, social, timeseries, sentiment };
}

export async function semanticSearch(query: string) {
  const response = await fetch(`${API_URL}/search/semantic`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit: 8, collection: "article_embeddings" })
  });
  if (!response.ok) {
    throw new Error("Search failed");
  }
  return response.json();
}

export async function loadProductGraph(product: string): Promise<GraphData> {
  return getJson<GraphData>(`/graph/product/${encodeURIComponent(product)}`);
}
