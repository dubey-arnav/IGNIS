import { NavLink } from "react-router-dom";

const navLinks = [
  { to: "/", label: "Dashboard" },
  { to: "/map", label: "Map" },
  { to: "/analytics", label: "Analytics" },
  { to: "/facilities", label: "Facilities" },
  { to: "/alerts", label: "Alerts" },
];

export default function NavBar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand-group">
        <div className="navbar-brand">
          IGNIS
          <span className="navbar-tagline">Thermal Monitoring</span>
        </div>
      </div>

      <div className="navbar-links">
        {navLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => (isActive ? "active" : "")}
            end={link.to === "/"}
          >
            {link.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
