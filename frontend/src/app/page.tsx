"use client";

import { useState } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line
} from "recharts";
import { Search, Loader2, Database, AlertCircle, Code, Table as TableIcon, BarChart3 } from "lucide-react";

interface QueryResponse {
  sql?: string;
  data?: any[];
  columns?: string[];
  error?: string;
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: "Failed to connect to the backend. Is FastAPI running?" });
    } finally {
      setIsLoading(false);
    }
  };

  const renderChart = () => {
    if (!result?.data || result.data.length === 0 || !result.columns) return null;

    const data = result.data;
    const columns = result.columns;
    
    // Simple heuristic: find categorical and numeric columns
    const firstRow = data[0];
    const numericCols = columns.filter(c => typeof firstRow[c] === 'number');
    const catCols = columns.filter(c => typeof firstRow[c] === 'string');

    if (numericCols.length === 0) return null;

    if (catCols.length >= 1 && numericCols.length >= 1) {
      // Bar Chart for categorical vs numeric
      const xAxis = catCols[0];
      const yAxis = numericCols[0];

      return (
        <div className="h-80 w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey={xAxis} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}`} />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Bar dataKey={yAxis} fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    } else if (numericCols.length >= 2) {
      // Line Chart for multiple numeric
      const xAxis = numericCols[0];
      const yAxis = numericCols[1];

      return (
        <div className="h-80 w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey={xAxis} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Line type="monotone" dataKey={yAxis} stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100">
      <main className="max-w-5xl mx-auto px-4 py-12 md:py-20">
        
        {/* Header */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-3 bg-blue-100 rounded-2xl mb-6 shadow-sm ring-1 ring-blue-50">
            <Database className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 mb-4">
            Chat with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Structured Data</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Ask natural language questions about your retail database (Customers, Products, Orders) and get instant SQL insights.
          </p>
        </header>

        {/* Input Section */}
        <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-2 ring-1 ring-slate-100 mb-12">
          <form onSubmit={handleSubmit} className="flex relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. What were the total sales by product category?"
              className="w-full bg-transparent border-0 pl-12 pr-32 py-4 text-lg focus:ring-0 placeholder:text-slate-400 outline-none rounded-2xl text-slate-800"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-slate-900 hover:bg-slate-800 text-white px-6 py-2.5 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running
                </>
              ) : (
                "Run Query"
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {result && (
          <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Error State */}
            {result.error && (
              <div className="bg-red-50 border border-red-100 text-red-700 p-6 rounded-2xl flex items-start gap-4">
                <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold mb-1">Query Failed</h3>
                  <p className="text-red-600/90">{result.error}</p>
                </div>
              </div>
            )}

            {/* Generated SQL */}
            {result.sql && !result.error && (
              <div className="bg-slate-900 rounded-2xl overflow-hidden shadow-lg border border-slate-800">
                <div className="bg-slate-800/50 px-4 py-3 flex items-center gap-2 border-b border-slate-700/50">
                  <Code className="w-4 h-4 text-slate-400" />
                  <span className="text-sm font-medium text-slate-300">Generated SQL</span>
                </div>
                <div className="p-4 overflow-x-auto">
                  <pre className="text-blue-300 font-mono text-sm">
                    <code>{result.sql}</code>
                  </pre>
                </div>
              </div>
            )}

            {/* Data Table & Chart */}
            {result.data && result.data.length > 0 && (
              <div className="grid lg:grid-cols-2 gap-6">
                
                {/* Table */}
                <div className="bg-white rounded-2xl p-6 shadow-xl shadow-slate-200/50 ring-1 ring-slate-100 flex flex-col">
                  <div className="flex items-center gap-2 mb-6">
                    <TableIcon className="w-5 h-5 text-indigo-500" />
                    <h3 className="font-semibold text-slate-800">Data Results</h3>
                  </div>
                  <div className="overflow-x-auto flex-1">
                    <table className="w-full text-left text-sm whitespace-nowrap">
                      <thead>
                        <tr className="border-b border-slate-200">
                          {result.columns?.map((col) => (
                            <th key={col} className="pb-3 pr-6 font-medium text-slate-500">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.data.slice(0, 100).map((row, i) => (
                          <tr key={i} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50">
                            {result.columns?.map((col) => (
                              <td key={col} className="py-3 pr-6 text-slate-700">
                                {row[col] !== null ? String(row[col]) : "-"}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {result.data.length > 100 && (
                    <div className="text-xs text-slate-400 mt-4 text-center">
                      Showing first 100 rows
                    </div>
                  )}
                </div>

                {/* Chart */}
                {renderChart() && (
                  <div className="bg-white rounded-2xl p-6 shadow-xl shadow-slate-200/50 ring-1 ring-slate-100 flex flex-col">
                    <div className="flex items-center gap-2 mb-2">
                      <BarChart3 className="w-5 h-5 text-blue-500" />
                      <h3 className="font-semibold text-slate-800">Visualization</h3>
                    </div>
                    <div className="flex-1 flex items-center justify-center">
                      {renderChart()}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
