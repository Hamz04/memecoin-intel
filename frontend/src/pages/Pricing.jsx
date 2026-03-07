import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const PLANS = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    tier: "FREE",
    features: [
      "Top 5 insider wallets",
      "Score 85+ only (Legendary)",
      "10 early buyers per coin",
      "Limited alerts feed",
    ],
    excluded: [
      "Overlap map",
      "Telegram alerts",
      "Behavioral flags",
      "API access",
    ],
    cta: "Current Plan",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$49",
    period: "/month",
    tier: "PRO",
    features: [
      "Unlimited insider wallets",
      "Score 50+ (Notable & above)",
      "100 early buyers per coin",
      "Full alerts feed",
      "Overlap map visualization",
    ],
    excluded: [
      "Telegram alerts",
      "Behavioral flags",
      "API access",
    ],
    cta: "Upgrade to Pro",
    highlighted: true,
  },
  {
    name: "Elite",
    price: "$199",
    period: "/month",
    tier: "ELITE",
    features: [
      "Unlimited insider wallets",
      "Score 30+ (all tiers)",
      "500 early buyers per coin",
      "Full alerts feed",
      "Overlap map visualization",
      "Real-time Telegram alerts",
      "Behavioral flags & analysis",
      "Full API access",
    ],
    excluded: [],
    cta: "Go Elite",
    highlighted: false,
  },
];

export default function Pricing() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState("");

  const handleCheckout = async (tier) => {
    if (!email) {
      alert("Please enter your email first");
      return;
    }
    if (tier === "FREE") return;

    setLoading(tier);
    try {
      const resp = await fetch(`${API}/api/subscribe/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          tier,
          success_url: `${window.location.origin}/`,
          cancel_url: `${window.location.origin}/pricing`,
        }),
      });
      const data = await resp.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert(data.error || "Checkout failed");
      }
    } catch (e) {
      alert("Network error");
    } finally {
      setLoading("");
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Track the Smart Money</h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Find the wallets that keep showing up early in every memecoin mega-runner.
          From PEPE to TRUMP to WIF -- same insiders, different coins.
        </p>
      </div>

      {/* Email input */}
      <div className="max-w-md mx-auto mb-10">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email to get started"
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-center focus:outline-none focus:border-emerald-500"
        />
      </div>

      {/* Pricing cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={`rounded-2xl p-6 border ${
              plan.highlighted
                ? "border-emerald-500/50 bg-emerald-500/5 ring-1 ring-emerald-500/20"
                : "border-gray-800 bg-gray-900"
            }`}
          >
            {plan.highlighted && (
              <div className="text-center mb-3">
                <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-xs font-semibold">
                  Most Popular
                </span>
              </div>
            )}

            <h3 className="text-xl font-bold">{plan.name}</h3>
            <div className="mt-2 mb-6">
              <span className="text-4xl font-bold">{plan.price}</span>
              <span className="text-gray-500 ml-1">{plan.period}</span>
            </div>

            <button
              onClick={() => handleCheckout(plan.tier)}
              disabled={plan.tier === "FREE" || loading === plan.tier}
              className={`w-full py-3 rounded-lg font-medium text-sm transition-colors mb-6 ${
                plan.highlighted
                  ? "bg-emerald-600 hover:bg-emerald-500 text-white"
                  : plan.tier === "FREE"
                  ? "bg-gray-800 text-gray-500 cursor-default"
                  : "bg-gray-800 hover:bg-gray-700 text-white"
              }`}
            >
              {loading === plan.tier ? "Loading..." : plan.cta}
            </button>

            <div className="space-y-3">
              {plan.features.map((f) => (
                <div key={f} className="flex items-start gap-2 text-sm">
                  <svg className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{f}</span>
                </div>
              ))}
              {plan.excluded.map((f) => (
                <div key={f} className="flex items-start gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
