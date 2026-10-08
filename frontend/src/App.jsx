import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import AsyncView from "./components/AsyncView";
import Header, { DemoBanner } from "./components/Header";
import { useApi } from "./hooks/useApi";
import DashboardPage from "./pages/DashboardPage";
import DataPage from "./pages/DataPage";
import LimitationsPage from "./pages/LimitationsPage";
import ModelPage from "./pages/ModelPage";
import { api } from "./services/api";

export default function App() {
  const [country, setCountry] = useState("RW");
  const meta = useApi(() => api.meta(country), [country]);
  const countries = useApi(() => api.countries(), []);

  return (
    <>
      <Header isDemo={meta.data?.is_demo} />
      <DemoBanner meta={meta.data} />
      <main className="page">
        <AsyncView state={meta} label="Preparing data. The first start trains the models and can take a minute.">
          {(m) => (
            <Routes>
              <Route path="/" element={
                <DashboardPage country={country} setCountry={setCountry} meta={m} countries={countries.data ?? []} />} />
              <Route path="/model" element={<ModelPage country={country} meta={m} />} />
              <Route path="/data" element={<DataPage meta={m} />} />
              <Route path="/limitations" element={<LimitationsPage />} />
              <Route path="*" element={<p>Page not found.</p>} />
            </Routes>
          )}
        </AsyncView>
      </main>
    </>
  );
}
