import { NavLink } from "react-router-dom";

export default function Header({ isDemo }) {
  return (
    <header className="site-header">
      <div className="brand">
        <h1>Solar Market Reality</h1>
        <p>Off-Grid Solar Market Intelligence</p>
      </div>
      <nav aria-label="Main">
        <NavLink to="/" end>Map</NavLink>
        <NavLink to="/model">Model performance</NavLink>
        <NavLink to="/data">Data sources</NavLink>
        <NavLink to="/limitations">Limitations</NavLink>
      </nav>
      {isDemo && <span className="demo-badge">DEMO DATA</span>}
    </header>
  );
}

export function DemoBanner({ meta }) {
  if (!meta?.is_demo) return null;
  return (
    <div className="demo-banner" role="note">
      <strong>DEMO DATA.</strong> Every value shown here is synthetic and was generated to exercise the
      pipeline. Do not read it as a real-world finding about {meta.country_name}.
    </div>
  );
}
