import { useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import NavBar from "./components/layout/NavBar";
import DashboardPage from "./pages/DashboardPage";
import MapPage from "./pages/MapPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import FacilitiesPage from "./pages/FacilitiesPage";
import FacilityDetailPage from "./pages/FacilityDetailPage";
import AlertsPage from "./pages/AlertsPage";

function TitleUpdater() {
  const location = useLocation();

  useEffect(() => {
    const path = location.pathname;
    if (path === "/" || path === "") {
      document.title = "Dashboard | IGNIS";
    } else if (path.startsWith("/map")) {
      document.title = "Live Fire Map | IGNIS";
    } else if (path.startsWith("/analytics")) {
      document.title = "Risk Analytics | IGNIS";
    } else if (path.startsWith("/facilities/")) {
      document.title = "Facility Inspection | IGNIS";
    } else if (path.startsWith("/facilities")) {
      document.title = "Industrial Facilities | IGNIS";
    } else if (path.startsWith("/alerts")) {
      document.title = "Active Alerts | IGNIS";
    } else {
      document.title = "IGNIS | Industrial Thermal Anomaly Monitoring";
    }
  }, [location]);

  return null;
}

function App() {
  return (
    <BrowserRouter>
      <TitleUpdater />
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
