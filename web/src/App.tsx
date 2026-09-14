import { lazy, Suspense, useEffect } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "./hooks/useReducedMotion";

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

function SmoothScroll() {
  const reduced = useReducedMotion();

  useEffect(() => {
    if (reduced) return;

    const lenis = new Lenis({
      duration: 1.05,
      smoothWheel: true,
      wheelMultiplier: 0.85,
    });
    const updateScrollTrigger = () => ScrollTrigger.update();
    const raf = (time: number) => lenis.raf(time * 1000);

    lenis.on("scroll", updateScrollTrigger);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    return () => {
      gsap.ticker.remove(raf);
      lenis.off("scroll", updateScrollTrigger);
      lenis.destroy();
      document.documentElement.style.removeProperty("scroll-behavior");
    };
  }, [reduced]);

  return null;
}

function ScrollReset() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
    ScrollTrigger.refresh();
  }, [pathname]);

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
      <SmoothScroll />
      <ScrollReset />
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
