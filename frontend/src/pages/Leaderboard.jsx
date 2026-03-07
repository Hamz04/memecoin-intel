import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TIER_COLORS = {
  LEGENDARY: "bg-amber-500/20 text-amber-400",
  ELITE: "bg-purple-500/20 text-purple-400",
  NOTABLE: "bg-blue-500/20 text-blue-400",
  WATCHLIST: "bg-gray-600/20 text-gray-400",
  NOISE: "bg-gray-800 text-gray-600",
};

export default function Leaderboard() {
  const [wallets, setWallets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [tierFilter, setTierFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const limit = 25;

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ limit, offset: page * limit });
    if (tierFilter) params.set("tier", tierFilter);

    fetch(`${API}/api/insiders/leaderboard?${params}`)
      .then((r) => r.json())
      .then((data) => {
        setWallets(data.wallets || []);
        setTotal(data.total || 0);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page, tierFilter]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Insider Leaderboard</h1>
          <p className="text-gray-500 mt-1">{total} wallets ranked by insider score</p>
        </div>
        <select
          value={tierFilter}
          onChange={(e) => { setTierFilter(e.target.value); setPage(0); }}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">All Tiers</option>
          <option value="LEGENDARY">Legendary</option>
          <option value="ELITE">Elite</option>
          <option value="NOTABLE">Notable</option>
          <option value="WATCHLIST">Watchlist</option>
        </select>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 bg-gray-900/50">
              <th className="p-4">Rank</th>
              <th className="p-4">Wallet</th>
              <th className="p-4">Chain</th>
              <th className="p-4">Score</th>
              <th className="p-4">Tier</th>
              <th className="p-4">Coins Hit</th>
              <th className="p-4">Win Rate</th>
              <th className="p-4">Avg Entry</th>
              <th className="p-4">Flags</th>
            </tr>
          </thead>
          <tbody>
            {wallets.map((w, i) => (
              <tr key={w.address} className="border-t border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                <td className="p-4 font-mono text-gray-500">#{page * limit + i + 1}</td>
                <td className="p-4">
                  <a href={`/wallet?address=${w.address}`} className="font-mono text-emerald-400 hover:text-emerald-300 text-xs">
                    {w.address?.slice(0, 8)}...{w.address?.slice(-6)}
                  </a>
                </td>
                <td className="p-4 text-gray-400">{w.chain}</td>
                <td className="p-4 font-bold text-lg">{w.score?.toFixed(1)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${TIER_COLORS[w.tier] || TIER_COLORS.NOISE}`}>
                    {w.tier}
                  </span>
                </td>
                <td className="p-4">{w.coins_list?.length || 0}</td>
                <td className="p-4">{w.win_rate_score ? `${w.win_rate_score.toFixed(0)}%` : "-"}</td>
                <td className="p-4 text-gray-400">{w.entry_speed_score ? `${w.entry_speed_score.toFixed(0)} min` : "-"}</td>
                <td className="p-4">
                  <div className="flex gap-1 flex-wrap">
                    {(w.behavioral_flags || []).slice(0, 3).map((f) => (
                      <span key={f} className="px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded text-xs">{f}</span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {wallets.length === 0 && !loading && (
          <p className="text-center text-gray-600 py-12">No insider wallets found</p>
        )}

        {/* Pagination */}
        <div className="flex items-center justify-between p-4 border-t border-gray-800">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-4 py-2 bg-gray-800 rounded-lg text-sm disabled:opacity-50 hover:bg-gray-700 transition-colors"
          >Previous</button>
          <span className="text-sm text-gray-500">
            Page {page + 1} of {Math.ceil(total / limit) || 1}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={(page + 1) * limit >= total}
            className="px-4 py-2 bg-gray-800 rounded-lg text-sm disabled:opacity-50 hover:bg-gray-700 transition-colors"
          >Next</button>
        </div>
      </div>
    </div>
  );
}
