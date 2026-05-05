# PostHarvest Atmos Mock Software — Design Spec

**Date:** 2026-05-05
**Status:** Approved (design sections), pending implementation
**Owner:** John Shannon

## Purpose

Single-file HTML sales-demo mock for PostHarvest Technologies. Shows a buyer how the Atmos product would work end-to-end: enter facility info (manually or via mock AI lookup), system fetches optimal storage levels per crop from "UC Davis Postharvest Center", then a dashboard lets them toggle Atmos on/off and watch room conditions converge to optimal.

Audience: prospective customers (apple, pear, citrus, mango, berry growers/packers/storage operators) during a 60–90 second pitch.

## Non-goals

- Real backend, real database, real API calls.
- Real UC Davis API integration (animation only; data hardcoded from published UC Davis Postharvest Center figures).
- Real Atmos hardware connection.
- Automation/preset rules page (deferred — see Future).
- Multi-user, login, permissions.
- Mobile responsive (desktop-only pitch).
- Content for nav tabs other than Overview (Reports / Readings / Config / Pair are stubs).
- Hybrid AI search calling a real web search API (flagged for v2).

## Stack

- **One file:** `postharvest-mock/index.html` containing HTML + inline CSS + inline JS + hardcoded data.
- **Vanilla JS** — no framework, no build step.
- **Leaflet.js** via CDN for the facility map view (OpenStreetMap tiles, no key).
- **localStorage** for persistence between page reloads. Reset button in header.
- Reuses visual style from existing `postharvest-dashboard_1.html` (green palette, segoe ui, room-dashboard layout).

## Architecture

### Single global state object

```js
state = {
  view: 'splash' | 'ai-lookup' | 'wizard-step1' | 'wizard-step2'
       | 'fetch-animation' | 'dashboard' | 'room',
  facility: {
    name: string,
    hq: string,
    rooms: [
      { id, name, address, lat, lng, cropId, atmosOn: boolean }
    ]
  },
  dashboardView: 'map' | 'grid',
  currentRoomId: string | null
}
```

### Render loop

Single `render()` function reads `state.view` and swaps the visible page section. Every state mutation calls `render()` and `persist()`.

### Persistence

- `persist()` writes `state` to `localStorage['pht-mock-state']` after every change.
- On load, hydrate from `localStorage` if present, else default to splash.
- Header has a "Reset Demo" button that clears storage and returns to splash.

## Pages / views

### 1. Splash

- Headline: "Set up your facility"
- Two large cards:
  - **Manual setup** — proceeds to wizard-step1
  - **AI auto-mock** — proceeds to ai-lookup
- Reset button (top-right) hidden on splash (nothing to reset yet).

### 2. AI lookup (`view: 'ai-lookup'`)

- Single text input: "Enter your company name…"
- Submit button.
- On submit: 3-second "Researching…" spinner with rotating status text:
  - "Searching the web…"
  - "Finding cool-room locations…"
  - "Identifying products stored…"
- Match logic: `companyName.toLowerCase().includes(<key>)` against pre-baked companies (see Data → Pre-baked companies).
- **Match found:** reveal facility card (name, HQ, # rooms, products) → "Looks good?" Accept / Edit / Cancel buttons.
  - Accept → `state.facility = matched`, advance to fetch-animation.
  - Edit → load matched data into wizard-step2 for tweaking.
  - Cancel → back to splash.
- **No match:** "We couldn't find this company. Want to enter manually?" → wizard-step1.

### 3. Manual wizard

**Step 1 (`wizard-step1`):**
- Inputs: facility name, HQ city/region.
- Next → step 2.

**Step 2 (`wizard-step2`):**
- "Add cool-rooms" — list of added rooms + "+ Add room" button.
- Add-room sub-form: room name, address (free text), crop autocomplete.
- Crop autocomplete: typeahead over crop database, shows "Apples - Gala", "Apples - Fuji"…
- Each added room gets a temporary lat/lng (geocoded mock — pull from a small lookup of major produce regions, fall back to a default).
- "Done" → fetch-animation.

### 4. Fetch animation (`view: 'fetch-animation'`)

- Full-screen overlay.
- Text: "Fetching optimal storage levels from UC Davis Postharvest Center…"
- Spinner 2 seconds.
- For each room, slot in optimal levels from crop database into `state.facility.rooms[i].optimal`.
- Auto-advance to dashboard.

### 5. Facility dashboard (`view: 'dashboard'`)

- Header: facility name, HQ, toggle [Map | Grid], "+ Add Room" button (loads add-room sub-form modal), Reset button.
- **Map view:** Leaflet map, pin per room. Pin color = room status (green = at optimal / Atmos on, yellow = drifting, red = critical). Click pin → opens room popup with crop + ethylene reading + "Open" link → room view.
- **Grid view:** tiles per room. Each tile shows: room name, crop, status badge, current ethylene reading, mini "ON/OFF" indicator. Click tile → room view.

### 6. Room dashboard (`view: 'room'`)

Reuses existing dashboard layout from `postharvest-dashboard_1.html`:
- Header (logo, locations/facility/room breadcrumbs, user avatar)
- Tabs row: Overview (active), Config / Reports / Readings / Pair (stubs — clicking shows "Coming soon")
- Crop summary strip: crop, optimal ranges per metric, "Highly sensitive…" note
- ATMOS ON/OFF toggle button + status text
- 5 horizontal bars: Ethylene / Temperature / Humidity / Pressure / Oxygen with target labels
- Right-side card: Ethylene reading (large), 4 mini-stats (humidity / temperature / pressure / oxygen), system status badge
- Bottom chart: line chart of all 5 metrics over 24 hours, with "ATMOS ACTIVATED" marker if room.atmosOn === true

**Atmos toggle behavior:**
- **OFF:** each metric drifts within a "drift band" computed as `optimalMidpoint × 1.4 ± 15%`. Ethylene drift band sits 3–5× above the threshold (e.g., 0.30–0.45 ppm for an apple-gala room with <0.1 ppm target — visibly red). Values jitter every 2 seconds via `setInterval`. Status badge: "Operational" (running but not optimised).
- **ON:** 1.5 second CSS transition. Values snap to mid-optimal range. Status badge: "At optimal". Chart appends a vertical "ATMOS ACTIVATED" line and values converge to flat optimal lines (matches existing demo screenshot 2).

Toggle is **per-room**. Each room has independent atmosOn state.

Back button → facility dashboard.

## Data

### Pre-baked companies (5)

| Match key | Display name | HQ | Lat/Lng | Rooms |
|---|---|---|---|---|
| `rockit` | Rockit Apple | Hawke's Bay, NZ | -39.49, 176.91 | 4 — all `apple-rockit` |
| `tru cape` / `trucape` | Tru Cape | Ceres, South Africa | -33.37, 19.31 | 6 — mix of `apple-gala`, `apple-granny`, `pear-bosc` |
| `calypso` | Calypso Mango | Bowen, QLD AU | -20.02, 148.24 | 3 — all `mango-calypso` |
| `costa` | Costa Group | Mildura, VIC AU | -34.21, 142.13 | 5 — `orange-navel`, `blueberry`, `avocado-hass` |
| `driscoll` | Driscoll's | Watsonville, CA US | 36.91, -121.76 | 8 — `strawberry`, `raspberry`, `blueberry`, `blackberry` |

Each pre-baked room has its own address (clustered around HQ lat/lng with small random offsets, baked at design time so they're stable across reloads).

### Crop database (~20 entries)

Each entry: `id`, `displayName`, `tempRange`, `humidityRange`, `ethyleneThreshold`, `o2Range`, `co2Range`, `pressure`, `sensitivityNote`.

Numbers grounded in UC Davis Postharvest Technology Center published optimal storage conditions (degrees Celsius, % RH, ppm, % atmosphere). Bake into JS object `CROPS = { 'apple-gala': {...}, ... }`.

| id | display | temp °C | RH % | ethylene ppm | O2 % | CO2 % | pressure atm |
|---|---|---|---|---|---|---|---|
| apple-gala | Apples — Gala | 0–1 | 90–95 | <0.1 | 1.5–2 | 1.5–2 | 1.01 |
| apple-granny | Apples — Granny Smith | 0–1 | 90–95 | <0.1 | 1–2 | 1–3 | 1.01 |
| apple-fuji | Apples — Fuji | 0–1 | 90–95 | <0.1 | 1.5–2 | 1–2 | 1.01 |
| apple-pinklady | Apples — Pink Lady | 0–1 | 90–95 | <0.1 | 1.5–2 | 1–1.5 | 1.01 |
| apple-rockit | Apples — Rockit | 0.5 | 90–95 | <0.1 | 1.5–2 | 1.5–2 | 1.01 |
| pear-bartlett | Pears — Bartlett | -1–0 | 90–95 | <0.1 | 1–3 | 0–1 | 1.01 |
| pear-bosc | Pears — Bosc | -1–0 | 90–95 | <0.1 | 2–3 | 0.5–1 | 1.01 |
| banana | Bananas | 13–14 | 90–95 | <1 | 2–5 | 2–5 | 1.01 |
| orange-navel | Oranges — Navel | 3–8 | 85–90 | <5 | 5–10 | 0–5 | 1.01 |
| mandarin | Mandarins | 5–8 | 90–95 | <5 | 5–10 | 0–5 | 1.01 |
| lemon | Lemons | 10–13 | 85–90 | <5 | 5–10 | 0–10 | 1.01 |
| mango-calypso | Mangoes — Calypso | 13 | 85–90 | <1 | 3–5 | 5–8 | 1.01 |
| avocado-hass | Avocados — Hass | 5–7 | 90–95 | <0.5 | 2–5 | 3–10 | 1.01 |
| kiwifruit-green | Kiwifruit — Green | 0 | 90–95 | <0.03 | 1–2 | 3–5 | 1.01 |
| strawberry | Strawberries | 0 | 90–95 | <2 | 5–10 | 15–20 | 1.01 |
| blueberry | Blueberries | 0 | 90–95 | <2 | 5–10 | 12–15 | 1.01 |
| raspberry | Raspberries | 0 | 90–95 | <2 | 5–10 | 15–20 | 1.01 |
| blackberry | Blackberries | 0 | 90–95 | <2 | 5–10 | 15–20 | 1.01 |
| cherry | Cherries | -1–0 | 90–95 | <0.1 | 3–10 | 10–15 | 1.01 |
| peach | Peaches | -0.5 | 90–95 | <0.1 | 1–2 | 3–5 | 1.01 |
| grape-table | Grapes — Table | -1–0 | 90–95 | <0.5 | 2–5 | 1–3 | 1.01 |

### Address-to-latlng helper

For manual wizard, use a small lookup of common produce regions (e.g., "Hawke's Bay" → -39.49,176.91; "Goulburn Valley" → -36.4,145.4). Fall back to a default if no match. Lat/lng only used to drop pin on the map.

## File layout

```
postharvest-mock/
  index.html       # everything (HTML + CSS + JS + data)
  README.md        # how to demo: open file, follow demo flow
  docs/
    superpowers/
      specs/
        2026-05-05-postharvest-mock-design.md   # this file
```

Estimated size: ~1500–2000 lines in `index.html`.

## Demo flow (sales pitch, ~90 seconds)

1. Open `index.html` → splash.
2. Click "AI auto-mock" → type "Rockit" → spinner 3 sec → "Rockit Apple, 4 rooms, Hawke's Bay" reveal.
3. Click "Looks good" → 2-sec UC Davis fetch animation → lands on map view (4 pins around Hawke's Bay, all green).
4. Toggle to **Grid** view → click "Apple Room 2".
5. Lands on room dashboard with ATMOS **OFF** — ethylene at 0.36 ppm (red), drift values, status "Operational".
6. Click **ATMOS ON** → 1.5 sec animation → values snap to 0.082 ppm, "At optimal", chart shows ATMOS ACTIVATED line.
7. Back → click another room → repeat for variety.

## Future (v2+)

- **Hybrid AI lookup** — real web search for unknown company names via API (Brave Search, Perplexity, etc).
- **Automation rules page** — port Screenshot 4 (Ripening / Degreening / Ethylene Scrubbing presets + custom condition→action builder).
- **Reports tab** — historical condition charts, room comparisons.
- **Mobile responsive layout.**
- **Multi-user / SSO.**

## Acceptance criteria

- [ ] Single `index.html` file, opens in Chrome with no console errors.
- [ ] Splash → AI auto-mock → "Rockit" → reveal → fetch → dashboard works without dev tools.
- [ ] Splash → manual setup → 2 rooms with different crops → fetch → dashboard works.
- [ ] Map view drops correct pins for all 5 pre-baked companies.
- [ ] Grid view tiles render with correct mini-stats.
- [ ] Room dashboard ATMOS toggle visibly changes all 5 metrics + chart.
- [ ] Refreshing the page restores state from localStorage.
- [ ] "Reset Demo" returns to splash and clears localStorage.
- [ ] All 21 crops render correct optimal ranges in the room dashboard summary strip.
