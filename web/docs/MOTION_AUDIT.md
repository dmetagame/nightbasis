# NightBasis motion audit

Audit date: 2026-09-16. Scope: `/web` only. The frozen research data,
prices, labels, fixtures, and Python implementation are out of scope.

## Evidence reviewed

- Local Vite build and `https://nightbasis.vercel.app` on `/`, `/desk`,
  `/method`, and `/motion`.
- Desktop at 1280 × 900 and mobile at 390 × 844, including full-page captures.
- Programmatic overflow, console, touch-target, Lenis, pin-spacer, and forced
  `prefers-reduced-motion` checks.
- Source inventory of every Lenis, GSAP, and ScrollTrigger instance.

Local and production matched. All eight route/viewport combinations had no
horizontal overflow and no console errors. Home and Desk replay clocks exceed
44px. Motion clocks measure 41.7px and fail the touch-target floor. Under
forced reduced motion, Lenis classes remain on every route and `/motion` keeps
two pin spacers, so the current teardown is incomplete.

## Route audit

| Route | 1280 first screen | 390 first screen | Type and layout finding |
| --- | --- | --- | --- |
| Home | One clear object: the serif thesis. The replay begins after the first viewport. | One clear object: the thesis; the replay follows immediately. | Hierarchy is correct. The kicker, title, copy, and buttons currently animate as four competing beats; only the title earns motion. |
| Desk | One clear object: the editorial intro. The console follows as the product surface. | Intro then full-width console; no overflow. | `No trade` is correctly the dominant object in the decision column. Snapshot changes need one restrained ink response, not more parallax. |
| Method | One clear object: the frozen-rule statement. | The same hierarchy survives the narrow viewport. | Policy reads as a definition list and should remain nearly static. Several narrative text blocks fall below the 16px body floor. |
| Motion | One clear intro, followed by the verdict beat. | Stacked, tappable structure with no horizontal overflow. | The pin and horizontal traverse are useful narrative devices. The technique-card batch turns the ending into a GSAP catalog and should be removed. |

## Motion inventory

| Location | Instance | Verdict |
| --- | --- | --- |
| `App.tsx` | Lenis driven by `gsap.ticker`; `lenis.on("scroll", ScrollTrigger.update)`; `lagSmoothing(0)` | Craft in principle, defective lifecycle. It is not route-owned, uses a low 0.85 wheel multiplier, and leaves root classes under reduced motion. |
| `App.tsx` | Route scroll reset plus `ScrollTrigger.refresh()` | Incomplete. It refreshes without first killing route-owned triggers. Font readiness is not part of the contract. |
| `OverviewPage.tsx` | One `gsap.from()` over kicker, title, copy, and actions | Carnival. Four page-load beats compete with the thesis and the `from()` path can flash before setup. Replace with a word-level title reveal only. |
| `MotionPage.tsx` | Document progress `scaleX` scrub | Craft. Keep as the single global scroll indicator; use scrub `0.2`. |
| `MotionPage.tsx` | `No trade` clip-path scrub | Craft and subject-specific. Keep the outline/fill construction and tighten the specified 75% → 30% range. |
| `MotionPage.tsx` | Pinned rGOOGL filing with four progress states | Craft. It maps scroll to actual snapshot order; add refresh invalidation and retain desktop-only pinning. |
| `MotionPage.tsx` | Horizontal three-night pin | Craft if desktop-only. It expresses the frozen research order; retain linear motion and refresh invalidation. |
| `MotionPage.tsx` | `ScrollTrigger.batch()` technique-card reveal | Carnival. It animates documentation about animation and adds no product meaning. Remove it. |
| `MotionPage.tsx` | Manual `requestAnimationFrame(ScrollTrigger.refresh)` | Redundant. Replace with the central font-aware refresh contract. |
| `ReplayPanel.tsx` | Recharts 280ms line update and 1.8s autoplay | Product state, not decorative scroll motion. Keep; autoplay already pauses for reduced motion and has a visible control. |
| CSS | Button/link color and transform transitions | Craft at their current small scale. Keep focus and state feedback; never introduce bounce or elastic easing. |

## Locked implementation list — eight fixes

1. Centralize the Lenis/ScrollTrigger contract: duration 1.1, wheel multiplier
   1, ticker ownership, scroll update hook, lag smoothing disabled, route
   teardown, trigger kill, font-ready refresh, and mobile-resize configuration.
2. Replace the Home four-block entrance with a word-split `h1` reveal only:
   24px, 0.8s, 0.05 stagger, `power3.out`, no blur, static under reduced motion.
3. Keep one document progress hairline and rebuild the `No trade` outline/fill
   beat at the specified scale and scroll range.
4. Keep only the two earned desktop scenes: the rGOOGL four-clock pin and the
   horizontal three-night traverse; both start below the header, anticipate
   pinning, and invalidate on refresh. Mobile remains stacked and unpinned.
5. Remove the technique-card batch reveal and the manual refresh loop. Keep the
   technique catalog quiet at the end, with no engineering chrome above fold.
6. Add a 200ms opacity-only ink response to the Desk `No trade` mark when a
   snapshot changes. No bounce, scale, or background parallax.
7. Add one restrained heading reveal on Method and leave every policy row and
   metric static.
8. Raise Motion clock targets to at least 44px, use a solid sticky header, and
   normalize narrative body copy to at least 16px while preserving compact
   utility labels and tabular data. Recheck 390px overflow and metric-label
   wrapping.

## Motion budget

The signature is the verdict: word-level thesis on entry, red ink filling
`No trade`, then evidence advancing through four clocks. Everything else is
static structure. Reduced motion receives the final layout immediately: no
Lenis, pins, scrubs, split-text animation, translation, blur, or autoplay.

## Post-implementation verification

- Local 1280px and 390px checks: all four routes have zero horizontal overflow,
  no reproducible console errors, and clock targets at or above 44px.
- Forced reduced motion: `matchMedia` resolves true, Lenis adds no root class,
  `/motion` has zero pin spacers, the progress hairline is hidden, and all three
  nights render in normal document flow without overflow.
- Route lifecycle: `/motion` creates exactly two desktop pin spacers, navigating
  away removes both, and returning creates exactly two—not a duplicated set.
- Visual captures confirm the Home replay remains immediately after the hero,
  Desk keeps `No trade` as the decision-column object, Method stays static apart
  from its heading, and Motion keeps technique language below the narrative.
