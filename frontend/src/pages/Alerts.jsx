import { useState, useEffect, useRef } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SEVERITY_STYLES = {
  CRITICAL: "border-red-500/30 bg-red-500/5",
  HIGH: "border-amber-500/30 bg-amber-500/5",
  MEDIUM: "border-blue-500/30 bg-blue-500/5",
  LOW: "border-gray-700 bg-gray-900",
};

const SEVERITY_BADGES = {
  CRITICAL: "bg-red-500/20 text-red-400",
  HIGH: "bg-amber-500/20 text-amber-400",
  MEDIUM: "bg-blue-500/20 text-blue-400",
  LOW: "bg-gray-700 text-gray-400",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef(null);

  const loadAlerts = () => {
    const params = filter ? `?severity=${filter}` : "";
    fetch(`${API}/api/alerts/feed${params}`)
      .then((r) => r.json())
      .then((data) => {
        setAlerts(data.alerts || []);
        setStats(data.stats || null);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
    // Auto-refresh every 30 seconds
    intervalRef.current = setInterval(loadAlerts, 30000);
    return () => clearInterval(intervalRef.current);
  }, [filter]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Live Alerts</h1>
          <p className="text-gray-500 mt-1">
            Auto-refreshes every 30s &bull; {stats?.total_alerts || 0} total alerts
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <button
            onClick={loadAlerts}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >Refresh</button>
        </div>
      </div>

      {/* Stats bar */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-400">Total Alerts</p>
            <p className="text-2xl font-bold">{stats.total_alerts}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-400">Last 24h</p>
            <p className="text-2xl font-bold">{stats.last_24h}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-400">Critical (24h)</p>
            <p className="text-2xl font-bold text-red-400">{stats.critical_24h}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-400">By Type</p>
            <div className="text-xs text-gray-400 mt-1">
              {Object.entries(stats.by_type || {}).map(([k, v]) => (
                <span key={k} className="mr-2">{k}: {v}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Alert feed */}
      <div className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`border rounded-xl p-5 transition-colors ${SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.LOW}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${SEVERITY_BADGES[alert.severity] || SEVERITY_BADGES.LOW}`}>
                    {alert.severity}
                  </span>
                  <span className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-400">
                    {alert.alert_type}
                  </span>
                </div>
                <h3 className="font-semibold">{alert.title}</h3>
                <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
              </div>
              <div className="text-right ml-4">
                <p className="text-xs text-gray-500">{alert.created_at?.replace("T", " ").slice(0, 19)}</p>
                {alert.wallet_address && (
                  <a href={`/wallet?address=${alert.wallet_address}`} className="text-xs text-emerald-400 hover:text-emerald-300">
                    View wallet
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}

        {alerts.length === 0 && !loading && (
          <div className="text-center text-gray-600 py-16 bg-gray-900 border border-gray-800 rounded-xl">
            <p className="text-lg">No alerts yet</p>
            <p className="text-sm mt-2">Alerts appear when tracked insiders make moves</p>
          </div>
        )}
      </div>
    </div>
  );
}
