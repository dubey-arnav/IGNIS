import { BrowserRouter, Routes, Route } from "react-router-dom";
import NavBar from "./components/layout/NavBar";
import DashboardPage from "./pages/DashboardPage";
import MapPage from "./pages/MapPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import FacilitiesPage from "./pages/FacilitiesPage";
import FacilityDetailPage from "./pages/FacilityDetailPage";
import AlertsPage from "./pages/AlertsPage";

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        <NavBar />
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/facilities" element={<FacilitiesPage />} />
            <Route path="/facilities/:id" element={<FacilityDetailPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
