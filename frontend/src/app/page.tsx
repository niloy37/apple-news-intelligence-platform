"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  Cable,
  Newspaper,
  Search,
  Share2,
  Smile,
  Tags
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { GraphPanel } from "@/components/GraphPanel";
import { MetricTile } from "@/components/MetricTile";
import { loadDashboardData, loadProductGraph, semanticSearch, type GraphData, type Headline } from "@/lib/api";

type DashboardData = Awaited<ReturnType<typeof loadDashboardData>>;

const tabs = [
  { id: "overview", label: "Overview", icon: Activity },
  { id: "headlines", label: "Latest Headlines", icon: Newspaper },
  { id: "trends", label: "Trends", icon: BarChart3 },
  { id: "social", label: "Social Buzz", icon: Share2 },
  { id: "search", label: "Semantic Search", icon: Search },
  { id: "graph", label: "Graph Explorer", icon: Cable }
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState<DashboardData | null>(null);
  const [query, setQuery] = useState("Apple Intelligence and iPhone supply chain");
  const [results, setResults] = useState<Array<{ score: number; payload: Headline }>>([]);
  const [graph, setGraph] = useState<GraphData | null>(null);

  useEffect(() => {
    loadDashboardData().then(setData).catch(() => setData(null));
  }, []);

  useEffect(() => {
    loadProductGraph("iPhone").then(setGraph).catch(() => setGraph({ nodes: [], edges: [] }));
  }, []);

  const sentimentValue = useMemo(() => {
    if (!data?.sentiment.length) return "0.00";
    const total = data.sentiment.reduce((sum, row) => sum + row.average_sentiment, 0);
    return (total / data.sentiment.length).toFixed(2);
  }, [data]);

  async function runSearch() {
    const searchResults = await semanticSearch(query);
    setResults(searchResults);
  }

  if (!data) {
    return (
      <main className="grid min-h-screen place-items-center bg-panel p-6">
        <div className="rounded-lg border border-line bg-white p-6 shadow-dashboard">Loading intelligence workspace...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-panel">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 border-r border-line bg-white p-5 lg:block">
          <div className="mb-7">
            <p className="text-sm font-medium text-apple">Apple News Intelligence</p>
            <h1 className="mt-2 text-2xl font-semibold text-ink">Signal Console</h1>
          </div>
          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex h-11 w-full items-center gap-3 rounded-lg px-3 text-left text-sm ${
                    active ? "bg-apple text-white" : "text-slate-700 hover:bg-panel"
                  }`}
                  aria-label={tab.label}
                >
                  <Icon className="h-4 w-4" aria-hidden />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        <section className="flex-1 p-4 md:p-6">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm text-slate-600">Batch, streaming, graph, and vector signals</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink md:text-3xl">
                {tabs.find((tab) => tab.id === activeTab)?.label}
              </h2>
            </div>
            <div className="flex gap-2 overflow-x-auto lg:hidden">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`grid h-10 w-10 place-items-center rounded-lg border ${
                      activeTab === tab.id ? "border-apple bg-apple text-white" : "border-line bg-white"
                    }`}
                    title={tab.label}
                    aria-label={tab.label}
                  >
                    <Icon className="h-4 w-4" />
                  </button>
                );
              })}
            </div>
          </div>

          {activeTab === "overview" && (
            <div className="space-y-5">
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <MetricTile label="Articles" value={String(data.latest.length)} accent="#1d6f99" icon={Newspaper} />
                <MetricTile label="Social Signals" value={String(data.social.length)} accent="#2f7d5c" icon={Share2} />
                <MetricTile label="Products" value={String(data.products.length)} accent="#b7791f" icon={Tags} />
                <MetricTile label="Sentiment" value={sentimentValue} accent="#b0445a" icon={Smile} />
              </div>
              <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
                <section className="rounded-lg border border-line bg-white p-4 shadow-dashboard">
                  <h3 className="mb-4 text-lg font-semibold">News and Social Volume</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={data.timeseries}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#d8dfd8" />
                        <XAxis dataKey="timestamp" hide />
                        <YAxis />
                        <Tooltip />
                        <Area type="monotone" dataKey="article_volume" stackId="1" stroke="#1d6f99" fill="#1d6f99" />
                        <Area type="monotone" dataKey="social_volume" stackId="1" stroke="#2f7d5c" fill="#2f7d5c" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </section>
                <section className="rounded-lg border border-line bg-white p-4 shadow-dashboard">
                  <h3 className="mb-4 text-lg font-semibold">Top Products</h3>
                  <div className="space-y-3">
                    {data.products.slice(0, 8).map((item) => (
                      <div key={item.product} className="flex items-center justify-between gap-3">
                        <span className="text-sm text-slate-700">{item.product}</span>
                        <span className="rounded-lg bg-panel px-2 py-1 text-sm font-medium">{item.mentions}</span>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            </div>
          )}

          {activeTab === "headlines" && <HeadlineList headlines={data.latest} />}

          {activeTab === "trends" && (
            <div className="grid gap-5 xl:grid-cols-2">
              <section className="rounded-lg border border-line bg-white p-4 shadow-dashboard">
                <h3 className="mb-4 text-lg font-semibold">Publisher Coverage</h3>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.publishers}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#d8dfd8" />
                      <XAxis dataKey="publisher" hide />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="article_count" fill="#1d6f99" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>
              <section className="rounded-lg border border-line bg-white p-4 shadow-dashboard">
                <h3 className="mb-4 text-lg font-semibold">Sentiment Timeline</h3>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.sentiment}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#d8dfd8" />
                      <XAxis dataKey="timestamp" hide />
                      <YAxis domain={[-1, 1]} />
                      <Tooltip />
                      <Line type="monotone" dataKey="average_sentiment" stroke="#b0445a" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>
            </div>
          )}

          {activeTab === "social" && (
            <section className="rounded-lg border border-line bg-white shadow-dashboard">
              <div className="grid divide-y divide-line">
                {data.social.slice(0, 25).map((post, index) => (
                  <div key={`${post.platform}-${index}`} className="grid gap-3 p-4 md:grid-cols-[1fr_120px_120px]">
                    <p className="text-sm text-slate-800">{post.text}</p>
                    <span className="text-sm text-slate-600">{post.platform}</span>
                    <span className="text-sm font-medium text-apple">{Math.round(post.engagement_score)} signals</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {activeTab === "search" && (
            <section className="space-y-4">
              <div className="flex gap-3">
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  className="h-11 flex-1 rounded-lg border border-line bg-white px-3 outline-none focus:border-apple"
                  aria-label="Semantic search query"
                />
                <button onClick={runSearch} className="flex h-11 items-center gap-2 rounded-lg bg-apple px-4 text-white">
                  <Search className="h-4 w-4" />
                  Search
                </button>
              </div>
              <div className="grid gap-3">
                {results.map((result) => (
                  <article key={result.payload.article_id} className="rounded-lg border border-line bg-white p-4 shadow-dashboard">
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-semibold">{result.payload.headline}</h3>
                      <span className="rounded-lg bg-panel px-2 py-1 text-sm">{result.score.toFixed(2)}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{result.payload.summary}</p>
                  </article>
                ))}
              </div>
            </section>
          )}

          {activeTab === "graph" && (
            <section className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {["iPhone", "Apple Intelligence", "Vision Pro", "MacBook", "App Store"].map((product) => (
                  <button
                    key={product}
                    onClick={() => loadProductGraph(product).then(setGraph)}
                    className="rounded-lg border border-line bg-white px-3 py-2 text-sm hover:border-apple"
                  >
                    {product}
                  </button>
                ))}
              </div>
              <GraphPanel graph={graph} />
            </section>
          )}
        </section>
      </div>
    </main>
  );
}

function HeadlineList({ headlines }: { headlines: Headline[] }) {
  return (
    <section className="rounded-lg border border-line bg-white shadow-dashboard">
      <div className="grid divide-y divide-line">
        {headlines.map((article) => (
          <article key={article.article_id} className="grid gap-3 p-4 md:grid-cols-[1fr_180px_120px]">
            <div>
              <a href={article.url} className="font-semibold text-ink hover:text-apple" target="_blank" rel="noreferrer">
                {article.headline}
              </a>
              <p className="mt-2 text-sm text-slate-600">{article.summary}</p>
            </div>
            <span className="text-sm text-slate-600">{article.publisher}</span>
            <span className="text-sm font-medium text-apple">{article.sentiment_score.toFixed(2)}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
