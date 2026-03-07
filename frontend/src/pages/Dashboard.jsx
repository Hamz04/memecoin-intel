import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function StatCard({ label, value, sub, color = "emerald" }) {
  const colors = {
    emerald: "from-emerald-500/10 to-emerald-500/5 border-emerald-500/20",
    purple: "from-purple-500/10 to-purple-500/5 border-purple-500/20",
    amber: "from-amber-500/10 to-amber-500/5 border-amber-500/20",
    red: "from-red-500/10 to-red-500/5 border-red-500/20",
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-5`}>
      <p className="text-sm text-gray-400">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [topInsiders, setTopInsiders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/stats`).then((r) => r.json()),
      fetch(`${API}/api/insiders/leaderboard?limit=5`).then((r) => r.json()),
    ])
      .then(([statsData, insidersData]) => {
        setStats(statsData);
        setTopInsiders(insidersData.wallets || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500 mt-1">Memecoin insider intelligence overview</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Coins Tracked" value={stats?.total_coins_tracked || 0} sub="Across 4 chains" color="emerald" />
        <StatCard label="Wallets Scanned" value={(stats?.total_wallets || 0).toLocaleString()} sub="Unique addresses" color="purple" />
        <StatCard label="Legendary Insiders" value={stats?.legendary_insiders || 0} sub="Score 85+" color="amber" />
        <StatCard label="Alerts (24h)" value={stats?.alerts?.last_24h || 0} sub={`${stats?.alerts?.critical_24h || 0} critical`} color="red" />
      </div>

      {/* Top insiders preview */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Top Insiders</h2>
          <a href="/leaderboard" className="text-sm text-emerald-400 hover:text-emerald-300">View all &rarr;</a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-800">
                <th className="pb-3 pr-4">Rank</th>
                <th className="pb-3 pr-4">Wallet</th>
                <th className="pb-3 pr-4">Score</th>
                <th className="pb-3 pr-4">Tier</th>
                <th className="pb-3 pr-4">Coins Hit</th>
                <th className="pb-3">Flags</th>
              </tr>
            </thead>
            <tbody>
              {topInsiders.map((w, i) => (
                <tr key={w.address} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                  <td className="py-3 pr-4 font-mono text-gray-500">#{i + 1}</td>
                  <td className="py-3 pr-4">
                    <a href={`/wallet?address=${w.address}`} className="font-mono text-emerald-400 hover:text-emerald-300">
                      {w.address?.slice(0, 6)}...{w.address?.slice(-4)}
                    </a>
                  </td>
                  <td className="py-3 pr-4 font-bold">{w.score?.toFixed(1)}</td>
                  <td className="py-3 pr-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      w.tier === "LEGENDARY" ? "bg-amber-500/20 text-amber-400" :
                      w.tier === "ELITE" ? "bg-purple-500/20 text-purple-400" :
                      "bg-gray-700 text-gray-300"
                    }`}>{w.tier}</span>
                  </td>
                  <td className="py-3 pr-4">{w.coins_list?.length || 0}</td>
                  <td className="py-3">
                    <div className="flex gap-1 flex-wrap">
                      {(w.behavioral_flags || []).map((f) => (
                        <span key={f} className="px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded text-xs">{f}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
              {topInsiders.length === 0 && (
                <tr><td colSpan={6} className="py-8 text-center text-gray-600">No insider data yet. Run a scan first.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
