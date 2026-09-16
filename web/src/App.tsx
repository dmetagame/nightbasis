import { lazy, Suspense, useLayoutEffect } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { useReducedMotion } from "./hooks/useReducedMotion";
import { mountScrollContract } from "./motion/scrollContract";

const OverviewPage = lazy(() =>
  import("./pages/OverviewPage").then((module) => ({ default: module.OverviewPage })),
);
const DeskPage = lazy(() =>
  import("./pages/DeskPage").then((module) => ({ default: module.DeskPage })),
);
const MethodPage = lazy(() =>
  import("./pages/MethodPage").then((module) => ({ default: module.MethodPage })),
);
const MotionPage = lazy(() =>
  import("./pages/MotionPage").then((module) => ({ default: module.MotionPage })),
);

const nav = [
  { to: "/", label: "Overview" },
  { to: "/desk", label: "Desk" },
  { to: "/method", label: "Method" },
  { to: "/motion", label: "Motion" },
];

function MotionContract() {
  const { pathname } = useLocation();
  const reduced = useReducedMotion();

  useLayoutEffect(() => {
    window.scrollTo(0, 0);
    return mountScrollContract(reduced);
  }, [pathname, reduced]);

  return null;
}

function Header() {
  return (
    <header className="site-header">
      <div className="header-inner">
        <NavLink className="wordmark" to="/" aria-label="NightBasis Desk home">
          <span className="wordmark-name">NightBasis</span>
          <span className="wordmark-desk">Desk</span>
        </NavLink>
        <nav className="main-nav" aria-label="Primary navigation">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => (isActive ? "nav-link is-active" : "nav-link")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <Link className="header-cta" to="/desk">Replay</Link>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <span className="footer-brand">NightBasis</span>
      <span aria-hidden="true">·</span>
      <a href="https://github.com/dmetagame/nightbasis/blob/main/LICENSE">MIT</a>
      <span aria-hidden="true">·</span>
      <a href="https://github.com/dmetagame/nightbasis">github.com/dmetagame/nightbasis</a>
    </footer>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <MotionContract />
      <Header />
      <main id="main-content">
        <Suspense fallback={<div className="route-loading">Loading frozen record…</div>}>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/desk" element={<DeskPage />} />
            <Route path="/method" element={<MethodPage />} />
            <Route path="/motion" element={<MotionPage />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
