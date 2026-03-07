import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function WalletDetail() {
  const [searchParams] = useSearchParams();
  const [address, setAddress] = useState(searchParams.get("address") || "");
  const [input, setInput] = useState(address);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadWallet = (addr) => {
    if (!addr) return;
    setLoading(true);
    setAddress(addr);
    fetch(`${API}/api/insiders/wallet/${addr}`)
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (address) loadWallet(address);
  }, []);

  const score = data?.score;
  const wallet = data?.wallet;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Wallet Deep Dive</h1>

      {/* Search */}
      <div className="flex gap-3 mb-8">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && loadWallet(input)}
          placeholder="Enter wallet address (0x... or Solana address)"
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm font-mono focus:outline-none focus:border-emerald-500"
        />
        <button
          onClick={() => loadWallet(input)}
          className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium transition-colors"
        >Search</button>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      )}

      {data?.error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center text-red-400">
          {data.error}
        </div>
      )}

      {wallet && !data?.error && (
        <div className="space-y-6">
          {/* Score card */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">Wallet Address</p>
                <p className="font-mono text-emerald-400 mt-1">{wallet.address}</p>
                <p className="text-sm text-gray-500 mt-2">Chain: {wallet.chain}</p>
              </div>
              {score && (
                <div className="text-right">
                  <div className="text-5xl font-bold">{score.score}</div>
                  <span className={`inline-block mt-1 px-3 py-1 rounded text-sm font-semibold ${
                    score.tier === "LEGENDARY" ? "bg-amber-500/20 text-amber-400" :
                    score.tier === "ELITE" ? "bg-purple-500/20 text-purple-400" :
                    score.tier === "NOTABLE" ? "bg-blue-500/20 text-blue-400" :
                    "bg-gray-700 text-gray-300"
                  }`}>{score.tier}</span>
                </div>
              )}
            </div>

            {score && (
              <div className="grid grid-cols-5 gap-4 mt-6">
                {[
                  { label: "Coins Hit (30%)", value: score.coins_hit_score },
                  { label: "Win Rate (25%)", value: score.win_rate_score },
                  { label: "Entry Speed (20%)", value: score.entry_speed_score },
                  { label: "ROI (15%)", value: score.roi_score },
                  { label: "Mcap Impact (10%)", value: score.mcap_impact_score },
                ].map((item) => (
                  <div key={item.label} className="bg-gray-800/50 rounded-lg p-3">
                    <div className="text-xs text-gray-500">{item.label}</div>
                    <div className="mt-1">
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full"
                          style={{ width: `${Math.min(100, item.value)}%` }}
                        />
                      </div>
                      <div className="text-right text-xs text-gray-400 mt-1">{item.value?.toFixed(1)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {score?.behavioral_flags?.length > 0 && (
              <div className="mt-4 flex gap-2 flex-wrap">
                {score.behavioral_flags.map((f) => (
                  <span key={f} className="px-2 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-lg text-xs font-medium">{f}</span>
                ))}
              </div>
            )}
          </div>

          {/* Trade history */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4">Trade History</h2>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-800">
                  <th className="pb-3 pr-4">Coin</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Amount</th>
                  <th className="pb-3 pr-4">Entry (min)</th>
                  <th className="pb-3 pr-4">ROI</th>
                  <th className="pb-3">Date</th>
                </tr>
              </thead>
              <tbody>
                {(data.trades || []).map((t, i) => (
                  <tr key={i} className="border-b border-gray-800/30">
                    <td className="py-2.5 pr-4 font-medium">{t.coin_symbol}</td>
                    <td className="py-2.5 pr-4">
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        t.trade_type === "BUY" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                      }`}>{t.trade_type}</span>
                    </td>
                    <td className="py-2.5 pr-4">{t.amount_usd ? `$${t.amount_usd.toLocaleString()}` : "-"}</td>
                    <td className="py-2.5 pr-4 text-gray-400">{t.minutes_after_launch ?? "-"}</td>
                    <td className="py-2.5 pr-4">
                      {t.roi ? (
                        <span className={t.roi > 0 ? "text-emerald-400" : "text-red-400"}>
                          {t.roi > 0 ? "+" : ""}{t.roi.toFixed(1)}x
                        </span>
                      ) : "-"}
                    </td>
                    <td className="py-2.5 text-gray-500 text-xs">{t.traded_at?.split("T")[0] || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!data.trades || data.trades.length === 0) && (
              <p className="text-center text-gray-600 py-8">No trades found for this wallet</p>
            )}
          </div>

          {/* Connections */}
          {data.connections?.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold mb-4">Connected Wallets</h2>
              <p className="text-sm text-gray-500 mb-3">Wallets that frequently trade the same coins</p>
              <div className="space-y-2">
                {data.connections.map((c, i) => (
                  <div key={i} className="flex items-center justify-between bg-gray-800/50 rounded-lg px-4 py-3">
                    <a href={`/wallet?address=${c.address}`} className="font-mono text-xs text-emerald-400 hover:text-emerald-300">
                      {c.address}
                    </a>
                    <span className="text-sm text-gray-400">{c.shared_coins} shared coins</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
