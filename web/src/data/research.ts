export const SNAPSHOT_TIMES = ["16:30", "20:00", "00:00", "08:30"] as const;

export type SnapshotTime = (typeof SNAPSHOT_TIMES)[number];

export type DeskSnapshot = {
  time: SnapshotTime;
  yPercent: number;
  z: number;
  signedInfo: number;
  eventId: string | null;
  label: "stand_down";
  reason:
    | "event_price_direction_conflict"
    | "uninformed_but_below_washout"
    | "no_qualifying_event_nonnegative_move";
  memo: string;
};

export type DeskFixture = {
  id: "quiet" | "news" | "washout";
  eyebrow: string;
  title: string;
  symbol: "rGOOGL" | "rTSLA";
  date: string;
  sessionStart: string;
  evidence: string;
  detail: string;
  snapshots: DeskSnapshot[];
};

export const deskFixtures: DeskFixture[] = [
  {
    id: "quiet",
    eyebrow: "Quiet tape",
    title: "A flat night stays flat",
    symbol: "rGOOGL",
    date: "14 Aug 2026",
    sessionStart: "2026-08-13T16:15:00-04:00",
    evidence: "No qualifying event in the frozen point-in-time cache.",
    detail:
      "Small negative residuals remain below 1.25; later observations are nonnegative.",
    snapshots: [
      {
        time: "16:30",
        yPercent: -0.00895,
        z: 0.243097,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "uninformed_but_below_washout",
        memo: "No qualifying event; z=0.243097 is below 1.25.",
      },
      {
        time: "20:00",
        yPercent: -0.008662,
        z: 0.308837,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "uninformed_but_below_washout",
        memo: "No qualifying event; z=0.308837 is below 1.25.",
      },
      {
        time: "00:00",
        yPercent: 0.008661,
        z: 0.489642,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "no_qualifying_event_nonnegative_move",
        memo: "No qualifying event and the observed move is nonnegative.",
      },
      {
        time: "08:30",
        yPercent: 0.250862,
        z: 0.235641,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "no_qualifying_event_nonnegative_move",
        memo: "No qualifying event and the observed move is nonnegative.",
      },
    ],
  },
  {
    id: "news",
    eyebrow: "Material filing",
    title: "The filing and tape disagree",
    symbol: "rGOOGL",
    date: "22–23 Jul 2026",
    sessionStart: "2026-07-22T16:15:00-04:00",
    evidence:
      "Alphabet 8-K accepted at 16:01 ET · accession sec-0001652044-26-000066.",
    detail:
      "$119.8B revenue (+24% YoY), $24.8B Cloud revenue (+82%), 34% operating margin, $9.11 diluted EPS.",
    snapshots: [
      {
        time: "16:30",
        yPercent: -1.965412,
        z: -3.494552,
        signedInfo: 0.855,
        eventId: "sec-0001652044-26-000066",
        label: "stand_down",
        reason: "event_price_direction_conflict",
        memo: "Positive event direction conflicts with the negative observed move.",
      },
      {
        time: "20:00",
        yPercent: -5.138112,
        z: -9.307844,
        signedInfo: 0.855,
        eventId: "sec-0001652044-26-000066",
        label: "stand_down",
        reason: "event_price_direction_conflict",
        memo: "Positive event direction conflicts with the negative observed move.",
      },
      {
        time: "00:00",
        yPercent: -4.407337,
        z: -7.887325,
        signedInfo: 0.855,
        eventId: "sec-0001652044-26-000066",
        label: "stand_down",
        reason: "event_price_direction_conflict",
        memo: "Positive event direction conflicts with the negative observed move.",
      },
      {
        time: "08:30",
        yPercent: -7.08874,
        z: -11.681456,
        signedInfo: 0.855,
        eventId: "sec-0001652044-26-000066",
        label: "stand_down",
        reason: "event_price_direction_conflict",
        memo: "Positive event direction conflicts with the negative observed move.",
      },
    ],
  },
  {
    id: "washout",
    eyebrow: "Uninformed move",
    title: "Large decline, insufficient residual",
    symbol: "rTSLA",
    date: "23 Jun 2026",
    sessionStart: "2026-06-22T16:15:00-04:00",
    evidence: "No qualifying Tesla SEC or IR event in the bounded event window.",
    detail:
      "The bounded result does not claim that no macro, analyst, or social news existed.",
    snapshots: [
      {
        time: "16:30",
        yPercent: -0.038093,
        z: 0.376121,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "uninformed_but_below_washout",
        memo: "No qualifying event; z=0.376121 is below 1.25.",
      },
      {
        time: "20:00",
        yPercent: -0.214151,
        z: 0.348336,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "uninformed_but_below_washout",
        memo: "No qualifying event; z=0.348336 is below 1.25.",
      },
      {
        time: "00:00",
        yPercent: -1.252763,
        z: -1.040159,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "uninformed_but_below_washout",
        memo: "No qualifying event; z=-1.040159 is below 1.25.",
      },
      {
        time: "08:30",
        yPercent: -2.639932,
        z: 1.235711,
        signedInfo: 0,
        eventId: null,
        label: "stand_down",
        reason: "uninformed_but_below_washout",
        memo: "No qualifying event; z=1.235711 is below 1.25.",
      },
    ],
  },
];

export const freezeHash =
  "0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0";

export const controlMetrics = [
  { period: "IS · 15 bps", sharpe: -1.58, trades: 10, days: 79 },
  { period: "IS · 25 bps", sharpe: -2.96, trades: 10, days: 79 },
  { period: "OOS · 15 bps", sharpe: -5.57, trades: 5, days: 23 },
];
