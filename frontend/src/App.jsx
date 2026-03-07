import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Leaderboard from "./pages/Leaderboard";
import CoinForensics from "./pages/CoinForensics";
import WalletDetail from "./pages/WalletDetail";
import Alerts from "./pages/Alerts";
import Pricing from "./pages/Pricing";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/forensics" element={<CoinForensics />} />
          <Route path="/wallet" element={<WalletDetail />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/pricing" element={<Pricing />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
