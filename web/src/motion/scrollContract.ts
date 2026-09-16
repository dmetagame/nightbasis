import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const LENIS_CLASSES = ["lenis", "lenis-smooth", "lenis-scrolling", "lenis-stopped"];

gsap.registerPlugin(ScrollTrigger);
ScrollTrigger.config({ ignoreMobileResize: true });

function clearLenisState() {
  for (const element of [document.documentElement, document.body]) {
    element.classList.remove(...LENIS_CLASSES);
    element.style.removeProperty("scroll-behavior");
  }
}

function killRouteMotion() {
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
  ScrollTrigger.refresh();
}

export function mountScrollContract(reduced: boolean) {
  let disposed = false;
  let frame = 0;

  const refresh = () => {
    if (!disposed) ScrollTrigger.refresh();
  };

  void document.fonts.ready.then(() => {
    frame = window.requestAnimationFrame(refresh);
  });

  if (reduced) {
    clearLenisState();
    frame = window.requestAnimationFrame(refresh);

    return () => {
      disposed = true;
      window.cancelAnimationFrame(frame);
      clearLenisState();
      killRouteMotion();
    };
  }

  const lenis = new Lenis({
    duration: 1.1,
    smoothWheel: true,
    wheelMultiplier: 1,
  });
  const updateScrollTrigger = () => ScrollTrigger.update();
  const raf = (time: number) => lenis.raf(time * 1000);

  lenis.on("scroll", updateScrollTrigger);
  gsap.ticker.add(raf);
  gsap.ticker.lagSmoothing(0);

  return () => {
    disposed = true;
    window.cancelAnimationFrame(frame);
    gsap.ticker.remove(raf);
    lenis.off("scroll", updateScrollTrigger);
    lenis.destroy();
    clearLenisState();
    killRouteMotion();
  };
}
