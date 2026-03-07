import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const CHAIN_COLORS = {
  ETH: "bg-blue-500/20 text-blue-400",
  SOL: "bg-purple-500/20 text-purple-400",
  BASE: "bg-cyan-500/20 text-cyan-400",
  BSC: "bg-yellow-500/20 text-yellow-400",
};

export default function CoinForensics() {
  const [coins, setCoins] = useState([]);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [forensics, setForensics] = useState(null);
  const [chainFilter, setChainFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = chainFilter ? `?chain=${chainFilter}` : "";
    fetch(`${API}/api/coins${params}`)
      .then((r) => r.json())
      .then((data) => setCoins(data.coins || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [chainFilter]);

  const loadForensics = (symbol) => {
    setSelectedCoin(symbol);
    setForensics(null);
    fetch(`${API}/api/coins/${symbol}/forensics`)
      .then((r) => r.json())
      .then(setForensics)
      .catch(console.error);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Coin Forensics</h1>
          <p className="text-gray-500 mt-1">Analyze early buyers for each memecoin</p>
        </div>
        <select
          value={chainFilter}
          onChange={(e) => setChainFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">All Chains</option>
          <option value="ETH">Ethereum</option>
          <option value="SOL">Solana</option>
          <option value="BASE">Base</option>
          <option value="BSC">BSC</option>
        </select>
      </div>

      {/* Coin grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-8">
        {coins.map((coin) => (
          <button
            key={coin.contract_address}
            onClick={() => loadForensics(coin.symbol)}
            className={`p-3 rounded-xl border text-left transition-all hover:scale-105 ${
              selectedCoin === coin.symbol
                ? "bg-emerald-500/10 border-emerald-500/30"
                : "bg-gray-900 border-gray-800 hover:border-gray-700"
            }`}
          >
            <div className="font-bold text-sm">{coin.symbol}</div>
            <div className="text-xs text-gray-500 mt-1">{coin.name}</div>
            <span className={`inline-block mt-2 px-1.5 py-0.5 rounded text-xs ${CHAIN_COLORS[coin.chain] || "bg-gray-800 text-gray-400"}`}>
              {coin.chain}
            </span>
            <div className="text-xs text-gray-600 mt-1">
              Peak: ${coin.peak_market_cap ? (coin.peak_market_cap / 1e9).toFixed(1) + "B" : "?"}
            </div>
          </button>
        ))}
      </div>

      {/* Forensics panel */}
      {selectedCoin && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">
            {selectedCoin} - Early Buyer Analysis
          </h2>

          {!forensics ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full" />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Total Early Buyers</p>
                  <p className="text-2xl font-bold">{forensics.total_early_buyers}</p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Notable Insiders</p>
                  <p className="text-2xl font-bold text-amber-400">{forensics.notable_insiders}</p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Avg Insider Score</p>
                  <p className="text-2xl font-bold text-emerald-400">{forensics.avg_insider_score}</p>
                </div>
              </div>

              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-800">
                    <th className="pb-3 pr-4">Wallet</th>
                    <th className="pb-3 pr-4">Entry (min)</th>
                    <th className="pb-3 pr-4">Amount</th>
                    <th className="pb-3 pr-4">ROI</th>
                    <th className="pb-3 pr-4">Score</th>
                    <th className="pb-3">Tier</th>
                  </tr>
                </thead>
                <tbody>
                  {(forensics.early_buyers || []).map((b, i) => (
                    <tr key={i} className="border-b border-gray-800/30">
                      <td className="py-2.5 pr-4">
                        <a href={`/wallet?address=${b.address}`} className="font-mono text-xs text-emerald-400 hover:text-emerald-300">
                          {b.address?.slice(0, 8)}...{b.address?.slice(-4)}
                        </a>
                      </td>
                      <td className="py-2.5 pr-4 text-gray-400">{b.minutes_after_launch ?? "-"}</td>
                      <td className="py-2.5 pr-4">{b.amount_usd ? `$${b.amount_usd.toLocaleString()}` : "-"}</td>
                      <td className="py-2.5 pr-4">
                        {b.roi ? (
                          <span className={b.roi > 0 ? "text-emerald-400" : "text-red-400"}>
                            {b.roi > 0 ? "+" : ""}{b.roi.toFixed(1)}x
                          </span>
                        ) : "-"}
                      </td>
                      <td className="py-2.5 pr-4 font-bold">{b.insider_score ?? "-"}</td>
                      <td className="py-2.5">{b.insider_tier || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </div>
  );
}
