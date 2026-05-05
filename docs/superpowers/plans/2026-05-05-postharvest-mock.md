# PostHarvest Atmos Mock — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file HTML sales-demo mock for PostHarvest Atmos: splash → AI auto-mock or manual wizard → "UC Davis" fetch → multi-room facility dashboard (map+grid) → per-room dashboard with ATMOS on/off toggle that visibly snaps drifting metrics to optimal levels.

**Architecture:** One `index.html` with inline CSS + JS + hardcoded data. Single global `state` object, one `render()` function reading `state.view` to swap visible page section. localStorage persists state across reloads. Leaflet via CDN for map. No build step. No backend.

**Tech Stack:** Vanilla JavaScript, vanilla CSS, Leaflet.js (CDN), localStorage. No frameworks, no bundler, no tests beyond manual browser verification.

**Verification model:** Single HTML file with no test runner. After each task, open `index.html` in Chrome and walk through a documented smoke check. Each task lists its smoke check explicitly.

**Reference spec:** [`docs/superpowers/specs/2026-05-05-postharvest-mock-design.md`](../specs/2026-05-05-postharvest-mock-design.md)

---

## File Structure

```
postharvest-mock/
  index.html                              # everything (HTML + inline CSS + inline JS + data)
  README.md                               # one-page demo instructions
  docs/superpowers/
    specs/2026-05-05-postharvest-mock-design.md
    plans/2026-05-05-postharvest-mock.md  # this file
```

`index.html` is one file by design (~1500–2000 lines). Internal sections:

1. `<head>` — meta + Leaflet CDN link + inline `<style>`
2. `<body>` — container `<div id="app">` (render target)
3. `<script>` — in this order:
   - Constants: `CROPS`, `COMPANIES`, `REGIONS` (lat/lng lookup)
   - State + persistence: `state`, `loadState()`, `saveState()`
   - View renderers: `renderSplash()`, `renderAiLookup()`, `renderWizardStep1()`, `renderWizardStep2()`, `renderFetchAnimation()`, `renderDashboard()`, `renderRoom()`
   - Helpers: `cropById()`, `randomDrift()`, `tickDriftValues()`
   - Top-level `render()` dispatcher + initial `loadState()` + `render()` call

Sections inside `<script>` are demarcated by `// === SECTION NAME ===` comment banners.

---

## Task 0: Project init + skeleton + commit

**Files:**
- Create: `postharvest-mock/index.html`
- Create: `postharvest-mock/README.md`
- Create: `postharvest-mock/.gitignore`

- [ ] **Step 1: Verify working directory**

```bash
cd "/Users/johnshannon/Website Design/postharvest-mock"
pwd
ls -la
```

Expected: `pwd` returns the postharvest-mock path; `ls` shows `docs/` and `.superpowers/`.

- [ ] **Step 2: Initialize git if not already a repo**

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || git init
git config user.email >/dev/null 2>&1 || echo "Set git user.email and user.name before committing"
```

Expected: either confirms repo exists, or initializes one. If the email/name aren't set, stop and ask the user how they want commits attributed.

- [ ] **Step 3: Write `.gitignore`**

```
.superpowers/
.DS_Store
```

- [ ] **Step 4: Write minimal `index.html` skeleton**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PostHarvest — Atmos Mock</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #1a1a1a; min-height: 100vh; font-family: 'Segoe UI', system-ui, sans-serif; color: #1a1a1a; }
  #app { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
</style>
</head>
<body>
<div id="app">Loading…</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
  // === CONSTANTS ===
  // (filled in by later tasks)

  // === STATE ===
  let state = { view: 'splash' };

  // === RENDER DISPATCH ===
  function render() {
    const app = document.getElementById('app');
    app.innerHTML = '<h1>Skeleton works — view: ' + state.view + '</h1>';
  }

  render();
</script>
</body>
</html>
```

- [ ] **Step 5: Write `README.md`**

```markdown
# PostHarvest Atmos Mock

Single-file HTML sales-demo mock. No build. No backend.

## Demo

Open `index.html` in Chrome.

1. Splash → "AI auto-mock"
2. Type `Rockit` → wait 3s → "Looks good"
3. Watch UC Davis fetch animation
4. Land on facility dashboard (map view, 4 pins)
5. Toggle to grid → click any room
6. Click ATMOS ON → watch metrics snap to optimal

Click "Reset Demo" in header to start over.

## Pre-baked AI companies

`Rockit` · `Tru Cape` · `Calypso` · `Costa` · `Driscoll`
```

- [ ] **Step 6: Smoke check**

Open `index.html` in Chrome. Expected: page reads "Skeleton works — view: splash" on a dark background. No console errors.

- [ ] **Step 7: Commit**

```bash
git add index.html README.md .gitignore
git commit -m "chore: initialize PostHarvest Atmos mock skeleton"
```

---

## Task 1: Crop database constant

**Files:**
- Modify: `index.html` (add to `// === CONSTANTS ===` section)

- [ ] **Step 1: Define success criterion**

Open browser console, type `CROPS['apple-gala']`. Expected: object with `displayName: 'Apples — Gala'`, `tempRange`, etc.

- [ ] **Step 2: Add `CROPS` object inside the `// === CONSTANTS ===` section**

```js
const CROPS = {
  'apple-gala':       { displayName: 'Apples — Gala',           tempRange: '0–1°C',   humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1.5–2%',  co2Range: '1.5–2%',  pressure: '1.01 atm', sensitivity: 'Highly sensitive. Ethylene scrubbing recommended.' },
  'apple-granny':     { displayName: 'Apples — Granny Smith',   tempRange: '0–1°C',   humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1–2%',    co2Range: '1–3%',    pressure: '1.01 atm', sensitivity: 'Highly sensitive. Ethylene scrubbing recommended.' },
  'apple-fuji':       { displayName: 'Apples — Fuji',           tempRange: '0–1°C',   humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1.5–2%',  co2Range: '1–2%',    pressure: '1.01 atm', sensitivity: 'Highly sensitive. Ethylene scrubbing recommended.' },
  'apple-pinklady':   { displayName: 'Apples — Pink Lady',      tempRange: '0–1°C',   humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1.5–2%',  co2Range: '1–1.5%',  pressure: '1.01 atm', sensitivity: 'Highly sensitive. Ethylene scrubbing recommended.' },
  'apple-rockit':     { displayName: 'Apples — Rockit',         tempRange: '0.5°C',   humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1.5–2%',  co2Range: '1.5–2%',  pressure: '1.01 atm', sensitivity: 'Highly sensitive. Ethylene scrubbing recommended.' },
  'pear-bartlett':    { displayName: 'Pears — Bartlett',        tempRange: '-1–0°C',  humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1–3%',    co2Range: '0–1%',    pressure: '1.01 atm', sensitivity: 'Sensitive to ethylene. Ripening accelerates rapidly.' },
  'pear-bosc':        { displayName: 'Pears — Bosc',            tempRange: '-1–0°C',  humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '2–3%',    co2Range: '0.5–1%',  pressure: '1.01 atm', sensitivity: 'Sensitive to ethylene. Ripening accelerates rapidly.' },
  'banana':           { displayName: 'Bananas',                  tempRange: '13–14°C', humidityRange: '90–95%', ethyleneThreshold: '<1 ppm',   o2Range: '2–5%',    co2Range: '2–5%',    pressure: '1.01 atm', sensitivity: 'Chilling injury below 13°C.' },
  'orange-navel':     { displayName: 'Oranges — Navel',         tempRange: '3–8°C',   humidityRange: '85–90%', ethyleneThreshold: '<5 ppm',   o2Range: '5–10%',   co2Range: '0–5%',    pressure: '1.01 atm', sensitivity: 'Moderate ethylene tolerance.' },
  'mandarin':         { displayName: 'Mandarins',                tempRange: '5–8°C',   humidityRange: '90–95%', ethyleneThreshold: '<5 ppm',   o2Range: '5–10%',   co2Range: '0–5%',    pressure: '1.01 atm', sensitivity: 'Moderate ethylene tolerance.' },
  'lemon':            { displayName: 'Lemons',                   tempRange: '10–13°C', humidityRange: '85–90%', ethyleneThreshold: '<5 ppm',   o2Range: '5–10%',   co2Range: '0–10%',   pressure: '1.01 atm', sensitivity: 'Chilling injury below 10°C.' },
  'mango-calypso':    { displayName: 'Mangoes — Calypso',       tempRange: '13°C',    humidityRange: '85–90%', ethyleneThreshold: '<1 ppm',   o2Range: '3–5%',    co2Range: '5–8%',    pressure: '1.01 atm', sensitivity: 'Tropical — chilling injury below 13°C.' },
  'avocado-hass':     { displayName: 'Avocados — Hass',          tempRange: '5–7°C',   humidityRange: '90–95%', ethyleneThreshold: '<0.5 ppm', o2Range: '2–5%',    co2Range: '3–10%',   pressure: '1.01 atm', sensitivity: 'Sensitive to ethylene. Ripens rapidly off-tree.' },
  'kiwifruit-green':  { displayName: 'Kiwifruit — Green',        tempRange: '0°C',     humidityRange: '90–95%', ethyleneThreshold: '<0.03 ppm',o2Range: '1–2%',    co2Range: '3–5%',    pressure: '1.01 atm', sensitivity: 'Extremely sensitive. <0.03 ppm ethylene critical.' },
  'strawberry':       { displayName: 'Strawberries',             tempRange: '0°C',     humidityRange: '90–95%', ethyleneThreshold: '<2 ppm',   o2Range: '5–10%',   co2Range: '15–20%',  pressure: '1.01 atm', sensitivity: 'High CO2 inhibits decay. Tolerates elevated CO2.' },
  'blueberry':        { displayName: 'Blueberries',              tempRange: '0°C',     humidityRange: '90–95%', ethyleneThreshold: '<2 ppm',   o2Range: '5–10%',   co2Range: '12–15%',  pressure: '1.01 atm', sensitivity: 'High CO2 inhibits decay.' },
  'raspberry':        { displayName: 'Raspberries',              tempRange: '0°C',     humidityRange: '90–95%', ethyleneThreshold: '<2 ppm',   o2Range: '5–10%',   co2Range: '15–20%',  pressure: '1.01 atm', sensitivity: 'High CO2 inhibits decay. Very perishable.' },
  'blackberry':       { displayName: 'Blackberries',             tempRange: '0°C',     humidityRange: '90–95%', ethyleneThreshold: '<2 ppm',   o2Range: '5–10%',   co2Range: '15–20%',  pressure: '1.01 atm', sensitivity: 'High CO2 inhibits decay.' },
  'cherry':           { displayName: 'Cherries',                 tempRange: '-1–0°C',  humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '3–10%',   co2Range: '10–15%',  pressure: '1.01 atm', sensitivity: 'High CO2 maintains firmness.' },
  'peach':            { displayName: 'Peaches',                  tempRange: '-0.5°C',  humidityRange: '90–95%', ethyleneThreshold: '<0.1 ppm', o2Range: '1–2%',    co2Range: '3–5%',    pressure: '1.01 atm', sensitivity: 'Internal breakdown risk above 0°C.' },
  'grape-table':      { displayName: 'Grapes — Table',           tempRange: '-1–0°C',  humidityRange: '90–95%', ethyleneThreshold: '<0.5 ppm', o2Range: '2–5%',    co2Range: '1–3%',    pressure: '1.01 atm', sensitivity: 'SO2 fumigation common. CA storage extends life.' }
};
```

- [ ] **Step 3: Smoke check**

Reload `index.html`. Open DevTools console. Type `Object.keys(CROPS).length`. Expected: `21`. Type `CROPS['apple-rockit'].displayName`. Expected: `"Apples — Rockit"`.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add CROPS database (21 crops with UC Davis optimal levels)"
```

---

## Task 2: Pre-baked companies + region lat/lng helper

**Files:**
- Modify: `index.html` (add to `// === CONSTANTS ===` section, after `CROPS`)

- [ ] **Step 1: Define success criterion**

Console: `COMPANIES.find(c => c.matchKeys.some(k => 'rockit apple'.includes(k))).displayName`. Expected: `"Rockit Apple"`.

- [ ] **Step 2: Add `COMPANIES` array and `REGIONS` object**

```js
const COMPANIES = [
  {
    matchKeys: ['rockit'],
    displayName: 'Rockit Apple',
    hq: "Hawke's Bay, NZ",
    lat: -39.49, lng: 176.91,
    rooms: [
      { name: 'Rockit Room 1', address: '12 Apple Way, Hastings', lat: -39.49, lng: 176.91, cropId: 'apple-rockit' },
      { name: 'Rockit Room 2', address: '12 Apple Way, Hastings', lat: -39.50, lng: 176.92, cropId: 'apple-rockit' },
      { name: 'Rockit Room 3', address: '14 Apple Way, Hastings', lat: -39.48, lng: 176.93, cropId: 'apple-rockit' },
      { name: 'Rockit Room 4', address: '14 Apple Way, Hastings', lat: -39.49, lng: 176.93, cropId: 'apple-rockit' }
    ]
  },
  {
    matchKeys: ['tru cape', 'trucape', 'tru-cape'],
    displayName: 'Tru Cape',
    hq: 'Ceres, South Africa',
    lat: -33.37, lng: 19.31,
    rooms: [
      { name: 'Ceres CA-1',  address: 'Ceres Pack Hub',  lat: -33.37, lng: 19.31, cropId: 'apple-gala' },
      { name: 'Ceres CA-2',  address: 'Ceres Pack Hub',  lat: -33.38, lng: 19.32, cropId: 'apple-gala' },
      { name: 'Ceres CA-3',  address: 'Ceres Pack Hub',  lat: -33.36, lng: 19.30, cropId: 'apple-granny' },
      { name: 'Ceres CA-4',  address: 'Ceres Pack Hub',  lat: -33.37, lng: 19.30, cropId: 'apple-granny' },
      { name: 'Pear Room A', address: 'Ceres Pack Hub',  lat: -33.38, lng: 19.31, cropId: 'pear-bosc' },
      { name: 'Pear Room B', address: 'Ceres Pack Hub',  lat: -33.36, lng: 19.32, cropId: 'pear-bosc' }
    ]
  },
  {
    matchKeys: ['calypso'],
    displayName: 'Calypso Mango',
    hq: 'Bowen, QLD AU',
    lat: -20.02, lng: 148.24,
    rooms: [
      { name: 'Bowen Mango 1', address: 'Bowen Packshed', lat: -20.02, lng: 148.24, cropId: 'mango-calypso' },
      { name: 'Bowen Mango 2', address: 'Bowen Packshed', lat: -20.03, lng: 148.25, cropId: 'mango-calypso' },
      { name: 'Bowen Mango 3', address: 'Bowen Packshed', lat: -20.01, lng: 148.23, cropId: 'mango-calypso' }
    ]
  },
  {
    matchKeys: ['costa'],
    displayName: 'Costa Group',
    hq: 'Mildura, VIC AU',
    lat: -34.21, lng: 142.13,
    rooms: [
      { name: 'Mildura Citrus 1',  address: 'Mildura Hub',     lat: -34.21, lng: 142.13, cropId: 'orange-navel' },
      { name: 'Mildura Citrus 2',  address: 'Mildura Hub',     lat: -34.22, lng: 142.14, cropId: 'orange-navel' },
      { name: 'Berry Room',        address: 'Corindi NSW',     lat: -30.04, lng: 153.21, cropId: 'blueberry' },
      { name: 'Avocado Room',      address: 'Atherton QLD',    lat: -17.27, lng: 145.48, cropId: 'avocado-hass' },
      { name: 'Avocado Room 2',    address: 'Atherton QLD',    lat: -17.27, lng: 145.49, cropId: 'avocado-hass' }
    ]
  },
  {
    matchKeys: ['driscoll'],
    displayName: "Driscoll's",
    hq: 'Watsonville, CA US',
    lat: 36.91, lng: -121.76,
    rooms: [
      { name: 'Watsonville Strawberry 1', address: 'Watsonville Cooler', lat: 36.91, lng: -121.76, cropId: 'strawberry' },
      { name: 'Watsonville Strawberry 2', address: 'Watsonville Cooler', lat: 36.92, lng: -121.77, cropId: 'strawberry' },
      { name: 'Watsonville Raspberry',    address: 'Watsonville Cooler', lat: 36.91, lng: -121.75, cropId: 'raspberry' },
      { name: 'Watsonville Blueberry',    address: 'Watsonville Cooler', lat: 36.92, lng: -121.75, cropId: 'blueberry' },
      { name: 'Watsonville Blackberry',   address: 'Watsonville Cooler', lat: 36.90, lng: -121.76, cropId: 'blackberry' },
      { name: 'Oxnard Strawberry',        address: 'Oxnard Cooler',      lat: 34.20, lng: -119.18, cropId: 'strawberry' },
      { name: 'Oxnard Raspberry',         address: 'Oxnard Cooler',      lat: 34.21, lng: -119.19, cropId: 'raspberry' },
      { name: 'Oxnard Blueberry',         address: 'Oxnard Cooler',      lat: 34.21, lng: -119.18, cropId: 'blueberry' }
    ]
  }
];

const REGIONS = {
  "hawke's bay":   { lat: -39.49, lng: 176.91 },
  "ceres":         { lat: -33.37, lng: 19.31 },
  "bowen":         { lat: -20.02, lng: 148.24 },
  "mildura":       { lat: -34.21, lng: 142.13 },
  "watsonville":   { lat: 36.91,  lng: -121.76 },
  "goulburn":      { lat: -36.40, lng: 145.40 },
  "shepparton":    { lat: -36.38, lng: 145.40 },
  "yakima":        { lat: 46.60,  lng: -120.51 },
  "wenatchee":     { lat: 47.42,  lng: -120.31 },
  "default":       { lat: -37.81, lng: 144.96 }
};

function regionLatLng(addressOrCity) {
  const lower = (addressOrCity || '').toLowerCase();
  for (const key of Object.keys(REGIONS)) {
    if (key !== 'default' && lower.includes(key)) return REGIONS[key];
  }
  return REGIONS.default;
}

function matchCompany(input) {
  const lower = (input || '').toLowerCase().trim();
  if (!lower) return null;
  return COMPANIES.find(c => c.matchKeys.some(k => lower.includes(k))) || null;
}
```

- [ ] **Step 3: Smoke check**

Reload. Console: `matchCompany('rockit apple co').displayName` → `"Rockit Apple"`. `matchCompany('xyz')` → `null`. `regionLatLng('our farm in Bowen').lat` → `-20.02`.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add pre-baked companies + region lookup helpers"
```

---

## Task 3: State + persistence + render dispatcher

**Files:**
- Modify: `index.html` (replace placeholder `state` and `render()` with full versions)

- [ ] **Step 1: Define success criterion**

Set `state.view = 'splash'`, call `saveState()`, reload — `state.view` is still `'splash'`. `resetState()` clears localStorage and returns to splash.

- [ ] **Step 2: Replace `// === STATE ===` and `// === RENDER DISPATCH ===` sections with**

```js
// === STATE ===
const STORAGE_KEY = 'pht-mock-state-v1';

const DEFAULT_STATE = {
  view: 'splash',
  facility: null,
  dashboardView: 'map',
  currentRoomId: null,
  aiInput: '',
  wizardDraft: { name: '', hq: '', rooms: [] }
};

let state = JSON.parse(JSON.stringify(DEFAULT_STATE));

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try { state = Object.assign({}, DEFAULT_STATE, JSON.parse(raw)); }
  catch { /* corrupt — ignore */ }
}

function resetState() {
  localStorage.removeItem(STORAGE_KEY);
  state = JSON.parse(JSON.stringify(DEFAULT_STATE));
  render();
}

function setView(view) {
  state.view = view;
  saveState();
  render();
}

function makeRoomId() {
  return 'r_' + Math.random().toString(36).slice(2, 9);
}

// === RENDER DISPATCH ===
function render() {
  const app = document.getElementById('app');
  const view = state.view;
  if (view === 'splash')          return renderSplash(app);
  if (view === 'ai-lookup')       return renderAiLookup(app);
  if (view === 'wizard-step1')    return renderWizardStep1(app);
  if (view === 'wizard-step2')    return renderWizardStep2(app);
  if (view === 'fetch-animation') return renderFetchAnimation(app);
  if (view === 'dashboard')       return renderDashboard(app);
  if (view === 'room')            return renderRoom(app);
  app.innerHTML = '<p>Unknown view: ' + view + '</p>';
}

// stub renderers — filled in by later tasks
function renderSplash(app)          { app.innerHTML = '<h1>Splash (todo)</h1>'; }
function renderAiLookup(app)        { app.innerHTML = '<h1>AI lookup (todo)</h1>'; }
function renderWizardStep1(app)     { app.innerHTML = '<h1>Wizard 1 (todo)</h1>'; }
function renderWizardStep2(app)     { app.innerHTML = '<h1>Wizard 2 (todo)</h1>'; }
function renderFetchAnimation(app)  { app.innerHTML = '<h1>Fetch (todo)</h1>'; }
function renderDashboard(app)       { app.innerHTML = '<h1>Dashboard (todo)</h1>'; }
function renderRoom(app)            { app.innerHTML = '<h1>Room (todo)</h1>'; }

loadState();
render();
```

- [ ] **Step 3: Smoke check**

Reload. Page shows "Splash (todo)". Console: `setView('dashboard')` → page now shows "Dashboard (todo)". Reload → page still shows "Dashboard (todo)" (persisted). Console: `resetState()` → page returns to "Splash (todo)".

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add state, persistence, and render dispatcher"
```

---

## Task 4: Splash view

**Files:**
- Modify: `index.html` — `renderSplash()` and add splash CSS

- [ ] **Step 1: Define success criterion**

After `resetState()`, page shows two large clickable cards: "Manual setup" and "AI auto-mock". Clicking each routes to the corresponding view.

- [ ] **Step 2: Add splash CSS to `<style>` block** (append at end)

```css
/* === SPLASH === */
.splash { width: 100%; max-width: 880px; }
.splash h1 { color: #f0f7f0; text-align: center; margin-bottom: 8px; font-size: 32px; font-weight: 700; }
.splash .subtitle { color: #a8c5a0; text-align: center; margin-bottom: 40px; }
.splash-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.splash-card { background: #f0f7f0; border-radius: 16px; padding: 36px 28px; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; border: 2px solid transparent; }
.splash-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.4); border-color: #2e7d32; }
.splash-card .icon { font-size: 36px; margin-bottom: 12px; }
.splash-card h3 { color: #1a6b1a; margin-bottom: 8px; font-size: 20px; }
.splash-card p { color: #555; font-size: 14px; line-height: 1.5; }
```

- [ ] **Step 3: Replace `renderSplash()` stub**

```js
function renderSplash(app) {
  app.innerHTML = `
    <div class="splash">
      <h1>Set up your facility</h1>
      <p class="subtitle">Choose how you'd like to add your cool-rooms</p>
      <div class="splash-cards">
        <div class="splash-card" id="splash-manual">
          <div class="icon">✍️</div>
          <h3>Manual setup</h3>
          <p>Enter your facility, cool-room addresses, and crops by hand. Best if you know your operation in detail.</p>
        </div>
        <div class="splash-card" id="splash-ai">
          <div class="icon">🤖</div>
          <h3>AI auto-mock</h3>
          <p>Just type your company name. We'll search the web and pre-fill addresses, rooms, and products for you.</p>
        </div>
      </div>
    </div>
  `;
  document.getElementById('splash-manual').onclick = () => setView('wizard-step1');
  document.getElementById('splash-ai').onclick = () => setView('ai-lookup');
}
```

- [ ] **Step 4: Smoke check**

Reload (after `resetState()` if needed). Two cards visible. Hover lifts the card. Click "AI auto-mock" → page shows "AI lookup (todo)". `resetState()` → back to splash. Click "Manual setup" → "Wizard 1 (todo)".

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: splash view with manual / AI auto-mock cards"
```

---

## Task 5: AI lookup view (input → spinner → reveal)

**Files:**
- Modify: `index.html` — `renderAiLookup()` and add AI lookup CSS

- [ ] **Step 1: Define success criterion**

Type "Rockit" → submit → 3-second spinner with rotating status text → reveal card showing "Rockit Apple, Hawke's Bay NZ, 4 rooms, Apples — Rockit". Three buttons: Accept / Edit / Cancel. Type "xyz" → submit → "Couldn't find" message + "Enter manually" button.

- [ ] **Step 2: Add CSS**

```css
/* === AI LOOKUP === */
.ai-panel { background: #f0f7f0; border-radius: 16px; padding: 36px; width: 100%; max-width: 640px; }
.ai-panel h2 { color: #1a6b1a; margin-bottom: 8px; }
.ai-panel .hint { color: #666; font-size: 13px; margin-bottom: 20px; }
.ai-input-row { display: flex; gap: 12px; }
.ai-input { flex: 1; padding: 14px 16px; border-radius: 10px; border: 2px solid #c8d8c4; font-size: 15px; outline: none; }
.ai-input:focus { border-color: #2e7d32; }
.btn { padding: 14px 24px; border-radius: 10px; border: none; cursor: pointer; font-weight: 600; font-size: 14px; }
.btn-primary { background: #2e7d32; color: #fff; }
.btn-primary:hover { background: #1a6b1a; }
.btn-secondary { background: #fff; color: #2e7d32; border: 1px solid #2e7d32; }
.btn-link { background: transparent; color: #555; text-decoration: underline; }
.spinner-block { text-align: center; padding: 40px 20px; }
.spinner { width: 48px; height: 48px; border: 4px solid #c8d8c4; border-top-color: #2e7d32; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinner-status { color: #1a6b1a; font-weight: 600; }
.reveal-card { background: #fff; border-radius: 12px; padding: 24px; margin-top: 20px; }
.reveal-card .row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.reveal-card .row:last-child { border-bottom: none; }
.reveal-card .row .label { color: #888; font-size: 12px; text-transform: uppercase; }
.reveal-card .row .value { color: #1a1a1a; font-weight: 600; }
.reveal-actions { display: flex; gap: 12px; margin-top: 16px; }
.not-found { text-align: center; color: #c0392b; padding: 24px; background: #fff5f4; border-radius: 10px; margin-top: 16px; }
```

- [ ] **Step 3: Replace `renderAiLookup()`**

```js
function renderAiLookup(app) {
  const phase = state._aiPhase || 'input'; // 'input' | 'searching' | 'found' | 'notfound'
  const matched = state._aiMatched || null;

  app.innerHTML = `
    <div class="ai-panel">
      <h2>AI auto-mock</h2>
      <p class="hint">Enter your company name. We'll search the web for cool-room locations, crops stored, and facility details.</p>
      ${phase === 'input' ? `
        <div class="ai-input-row">
          <input class="ai-input" id="ai-input" placeholder="e.g. Rockit Apple" value="${(state.aiInput || '').replace(/"/g, '&quot;')}">
          <button class="btn btn-primary" id="ai-submit">Search</button>
        </div>
        <button class="btn btn-link" id="ai-back" style="margin-top: 12px;">← Back</button>
      ` : ''}
      ${phase === 'searching' ? `
        <div class="spinner-block">
          <div class="spinner"></div>
          <div class="spinner-status" id="spinner-status">Searching the web…</div>
        </div>
      ` : ''}
      ${phase === 'found' && matched ? `
        <div class="reveal-card">
          <div class="row"><span class="label">Company</span><span class="value">${matched.displayName}</span></div>
          <div class="row"><span class="label">Headquarters</span><span class="value">${matched.hq}</span></div>
          <div class="row"><span class="label">Cool-rooms</span><span class="value">${matched.rooms.length}</span></div>
          <div class="row"><span class="label">Products stored</span><span class="value">${[...new Set(matched.rooms.map(r => CROPS[r.cropId].displayName))].join(', ')}</span></div>
        </div>
        <div class="reveal-actions">
          <button class="btn btn-primary" id="ai-accept">Looks good — fetch UC Davis levels</button>
          <button class="btn btn-secondary" id="ai-edit">Edit first</button>
          <button class="btn btn-link" id="ai-cancel">Cancel</button>
        </div>
      ` : ''}
      ${phase === 'notfound' ? `
        <div class="not-found">
          <p><strong>We couldn't find this company in our database.</strong></p>
          <p style="margin-top: 8px; font-size: 13px;">Try one of: Rockit, Tru Cape, Calypso, Costa, Driscoll — or enter manually.</p>
        </div>
        <div class="reveal-actions">
          <button class="btn btn-primary" id="ai-manual">Enter manually</button>
          <button class="btn btn-secondary" id="ai-retry">Try again</button>
          <button class="btn btn-link" id="ai-cancel-nf">Cancel</button>
        </div>
      ` : ''}
    </div>
  `;

  if (phase === 'input') {
    const input = document.getElementById('ai-input');
    input.focus();
    input.oninput = (e) => { state.aiInput = e.target.value; saveState(); };
    input.onkeydown = (e) => { if (e.key === 'Enter') document.getElementById('ai-submit').click(); };
    document.getElementById('ai-submit').onclick = startAiSearch;
    document.getElementById('ai-back').onclick = () => { state.aiInput = ''; setView('splash'); };
  }

  if (phase === 'found') {
    document.getElementById('ai-accept').onclick = () => acceptAiMatch(matched);
    document.getElementById('ai-edit').onclick = () => loadMatchIntoWizard(matched);
    document.getElementById('ai-cancel').onclick = () => clearAiAndBack();
  }

  if (phase === 'notfound') {
    document.getElementById('ai-manual').onclick = () => clearAiAndGoTo('wizard-step1');
    document.getElementById('ai-retry').onclick = () => { state._aiPhase = 'input'; render(); };
    document.getElementById('ai-cancel-nf').onclick = () => clearAiAndBack();
  }
}

function startAiSearch() {
  state._aiPhase = 'searching';
  render();
  const statuses = ['Searching the web…', 'Finding cool-room locations…', 'Identifying products stored…'];
  let i = 0;
  const interval = setInterval(() => {
    i = (i + 1) % statuses.length;
    const el = document.getElementById('spinner-status');
    if (el) el.textContent = statuses[i];
  }, 1000);

  setTimeout(() => {
    clearInterval(interval);
    const matched = matchCompany(state.aiInput);
    if (matched) {
      state._aiMatched = matched;
      state._aiPhase = 'found';
    } else {
      state._aiPhase = 'notfound';
    }
    render();
  }, 3000);
}

function acceptAiMatch(matched) {
  state.facility = {
    name: matched.displayName,
    hq: matched.hq,
    lat: matched.lat,
    lng: matched.lng,
    rooms: matched.rooms.map(r => ({
      id: makeRoomId(),
      name: r.name,
      address: r.address,
      lat: r.lat,
      lng: r.lng,
      cropId: r.cropId,
      atmosOn: false
    }))
  };
  state._aiPhase = null;
  state._aiMatched = null;
  state.aiInput = '';
  setView('fetch-animation');
}

function loadMatchIntoWizard(matched) {
  state.wizardDraft = {
    name: matched.displayName,
    hq: matched.hq,
    rooms: matched.rooms.map(r => ({ ...r, id: makeRoomId() }))
  };
  state._aiPhase = null;
  state._aiMatched = null;
  setView('wizard-step2');
}

function clearAiAndBack() {
  state._aiPhase = null;
  state._aiMatched = null;
  state.aiInput = '';
  setView('splash');
}

function clearAiAndGoTo(view) {
  state._aiPhase = null;
  state._aiMatched = null;
  setView(view);
}
```

- [ ] **Step 4: Smoke check**

`resetState()` → click "AI auto-mock" → type "Rockit" → click Search. Spinner runs ~3 seconds, status text rotates. Then card shows "Rockit Apple, Hawke's Bay NZ, Cool-rooms 4, Products stored Apples — Rockit". Click Cancel → back to splash. Repeat with input "xyz" → "We couldn't find" message. Click "Try again" → input phase. Click "Looks good — fetch UC Davis levels" → routes to "Fetch (todo)" placeholder.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: AI lookup view with spinner, reveal, and not-found paths"
```

---

## Task 6: Manual wizard step 1 (facility name + HQ)

**Files:**
- Modify: `index.html` — `renderWizardStep1()` (reuses CSS from Task 5)

- [ ] **Step 1: Define success criterion**

Splash → "Manual setup" → form with facility name + HQ inputs + "Next" button. Empty inputs disable Next. Filled in → click Next routes to Wizard 2 with `state.wizardDraft.name` and `.hq` populated.

- [ ] **Step 2: Replace `renderWizardStep1()`**

```js
function renderWizardStep1(app) {
  const draft = state.wizardDraft;
  app.innerHTML = `
    <div class="ai-panel">
      <h2>Step 1 of 2 — Your facility</h2>
      <p class="hint">Tell us where your operation is based.</p>
      <div style="display: flex; flex-direction: column; gap: 14px;">
        <div>
          <label class="label" style="display:block;font-size:11px;color:#888;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.8px;">Facility name</label>
          <input class="ai-input" id="w1-name" placeholder="e.g. Acme Cold Storage Co." value="${(draft.name || '').replace(/"/g, '&quot;')}">
        </div>
        <div>
          <label class="label" style="display:block;font-size:11px;color:#888;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.8px;">Headquarters</label>
          <input class="ai-input" id="w1-hq" placeholder="City, Region/Country" value="${(draft.hq || '').replace(/"/g, '&quot;')}">
        </div>
      </div>
      <div style="display: flex; gap: 12px; margin-top: 24px;">
        <button class="btn btn-link" id="w1-back">← Back</button>
        <div style="flex: 1;"></div>
        <button class="btn btn-primary" id="w1-next">Next →</button>
      </div>
    </div>
  `;
  const nameInput = document.getElementById('w1-name');
  const hqInput = document.getElementById('w1-hq');
  const nextBtn = document.getElementById('w1-next');
  function refreshNext() { nextBtn.disabled = !(nameInput.value.trim() && hqInput.value.trim()); nextBtn.style.opacity = nextBtn.disabled ? '0.5' : '1'; }
  refreshNext();
  nameInput.oninput = (e) => { state.wizardDraft.name = e.target.value; saveState(); refreshNext(); };
  hqInput.oninput = (e) => { state.wizardDraft.hq = e.target.value; saveState(); refreshNext(); };
  nameInput.focus();
  document.getElementById('w1-back').onclick = () => setView('splash');
  nextBtn.onclick = () => { if (!nextBtn.disabled) setView('wizard-step2'); };
}
```

- [ ] **Step 3: Smoke check**

`resetState()` → Manual → form. "Next" appears disabled (opacity 0.5). Type "Acme" + "Sydney AU" → Next enables. Click → Wizard 2 (todo) placeholder. `resetState()` → enter inputs → reload mid-flow → values persist (state saved on input).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: wizard step 1 (facility name + HQ)"
```

---

## Task 7: Manual wizard step 2 (add rooms with crop autocomplete)

**Files:**
- Modify: `index.html` — `renderWizardStep2()` and add wizard-2 CSS

- [ ] **Step 1: Define success criterion**

Wizard 2 shows list of added rooms (initially empty) and "+ Add room" form: room name, address, crop autocomplete. Type "app" in crop field → dropdown with all 5 apple options. Pick one → row added. "Done" disabled until at least 1 room. Click Done → fetch-animation, with `state.facility` populated from `state.wizardDraft`.

- [ ] **Step 2: Add CSS**

```css
/* === WIZARD STEP 2 === */
.rooms-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
.room-row { background: #fff; border-radius: 8px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; }
.room-row .info { font-size: 14px; }
.room-row .info b { color: #1a6b1a; }
.room-row .info small { color: #888; display: block; margin-top: 2px; }
.room-row .remove { color: #c0392b; cursor: pointer; font-size: 12px; background: transparent; border: none; }
.add-room-form { background: #fff; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.add-room-form .row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
.crop-autocomplete { position: relative; }
.crop-suggestions { position: absolute; top: 100%; left: 0; right: 0; background: #fff; border: 1px solid #c8d8c4; border-top: none; border-radius: 0 0 8px 8px; max-height: 200px; overflow-y: auto; z-index: 10; }
.crop-suggestions .item { padding: 10px 12px; cursor: pointer; font-size: 13px; }
.crop-suggestions .item:hover, .crop-suggestions .item.active { background: #e8f5e9; color: #1a6b1a; }
```

- [ ] **Step 2.5: Append `cropOptions()` helper inside `// === CONSTANTS ===` (or near top of script)**

```js
function cropOptions(query) {
  const q = (query || '').toLowerCase().trim();
  const all = Object.entries(CROPS).map(([id, c]) => ({ id, displayName: c.displayName }));
  if (!q) return all.slice(0, 8);
  return all.filter(c => c.displayName.toLowerCase().includes(q)).slice(0, 8);
}
```

- [ ] **Step 3: Replace `renderWizardStep2()`**

```js
function renderWizardStep2(app) {
  const draft = state.wizardDraft;
  const cropQuery = state._cropQuery || '';
  const cropOpen = state._cropOpen || false;
  const newRoom = state._newRoom || { name: '', address: '', cropId: null, cropDisplay: '' };

  app.innerHTML = `
    <div class="ai-panel" style="max-width: 720px;">
      <h2>Step 2 of 2 — Add cool-rooms</h2>
      <p class="hint">Add each cool-room with its address and the crop it stores.</p>

      <div class="rooms-list" id="rooms-list">
        ${draft.rooms.length === 0 ? '<p style="color:#888;font-size:13px;font-style:italic;">No rooms yet — add one below.</p>' : ''}
        ${draft.rooms.map((r, idx) => `
          <div class="room-row">
            <div class="info">
              <b>${r.name}</b> · ${CROPS[r.cropId] ? CROPS[r.cropId].displayName : '(unknown crop)'}
              <small>${r.address}</small>
            </div>
            <button class="remove" data-idx="${idx}">Remove</button>
          </div>
        `).join('')}
      </div>

      <div class="add-room-form">
        <div class="row3">
          <input class="ai-input" id="nr-name" placeholder="Room name" value="${(newRoom.name || '').replace(/"/g, '&quot;')}">
          <input class="ai-input" id="nr-addr" placeholder="Address / location" value="${(newRoom.address || '').replace(/"/g, '&quot;')}">
          <div class="crop-autocomplete">
            <input class="ai-input" id="nr-crop" placeholder="Crop (type to search)" value="${(newRoom.cropDisplay || cropQuery || '').replace(/"/g, '&quot;')}" autocomplete="off">
            ${cropOpen ? `
              <div class="crop-suggestions">
                ${cropOptions(cropQuery).map(o => `<div class="item" data-id="${o.id}" data-display="${o.displayName.replace(/"/g, '&quot;')}">${o.displayName}</div>`).join('')}
              </div>
            ` : ''}
          </div>
        </div>
        <button class="btn btn-secondary" id="add-room-btn">+ Add room to list</button>
      </div>

      <div style="display: flex; gap: 12px; margin-top: 20px;">
        <button class="btn btn-link" id="w2-back">← Back</button>
        <div style="flex: 1;"></div>
        <button class="btn btn-primary" id="w2-done">Done — fetch optimal levels →</button>
      </div>
    </div>
  `;

  // crop autocomplete
  const cropInput = document.getElementById('nr-crop');
  cropInput.oninput = (e) => {
    state._cropQuery = e.target.value;
    state._cropOpen = true;
    state._newRoom = { ...(state._newRoom || {}), cropId: null, cropDisplay: e.target.value };
    saveState();
    render();
    document.getElementById('nr-crop').focus();
  };
  cropInput.onfocus = () => { state._cropOpen = true; render(); document.getElementById('nr-crop').focus(); };
  document.querySelectorAll('.crop-suggestions .item').forEach(el => {
    el.onclick = () => {
      state._newRoom = { ...(state._newRoom || {}), cropId: el.dataset.id, cropDisplay: el.dataset.display };
      state._cropQuery = el.dataset.display;
      state._cropOpen = false;
      saveState();
      render();
    };
  });

  document.getElementById('nr-name').oninput = (e) => { state._newRoom = { ...(state._newRoom || {}), name: e.target.value }; saveState(); };
  document.getElementById('nr-addr').oninput = (e) => { state._newRoom = { ...(state._newRoom || {}), address: e.target.value }; saveState(); };

  document.getElementById('add-room-btn').onclick = () => {
    const nr = state._newRoom || {};
    if (!nr.name || !nr.address || !nr.cropId) {
      alert('Please fill in room name, address, and pick a crop from the dropdown.');
      return;
    }
    const ll = regionLatLng(nr.address);
    state.wizardDraft.rooms.push({
      id: makeRoomId(),
      name: nr.name,
      address: nr.address,
      lat: ll.lat,
      lng: ll.lng,
      cropId: nr.cropId
    });
    state._newRoom = { name: '', address: '', cropId: null, cropDisplay: '' };
    state._cropQuery = '';
    state._cropOpen = false;
    saveState();
    render();
  };

  document.querySelectorAll('.room-row .remove').forEach(btn => {
    btn.onclick = () => {
      const idx = parseInt(btn.dataset.idx, 10);
      state.wizardDraft.rooms.splice(idx, 1);
      saveState();
      render();
    };
  });

  document.getElementById('w2-back').onclick = () => setView('wizard-step1');
  const doneBtn = document.getElementById('w2-done');
  doneBtn.disabled = draft.rooms.length === 0;
  doneBtn.style.opacity = doneBtn.disabled ? '0.5' : '1';
  doneBtn.onclick = () => {
    if (doneBtn.disabled) return;
    state.facility = {
      name: state.wizardDraft.name,
      hq: state.wizardDraft.hq,
      lat: regionLatLng(state.wizardDraft.hq).lat,
      lng: regionLatLng(state.wizardDraft.hq).lng,
      rooms: state.wizardDraft.rooms.map(r => ({ ...r, atmosOn: false }))
    };
    state.wizardDraft = { name: '', hq: '', rooms: [] };
    state._newRoom = { name: '', address: '', cropId: null, cropDisplay: '' };
    state._cropQuery = '';
    state._cropOpen = false;
    setView('fetch-animation');
  };
}
```

- [ ] **Step 4: Smoke check**

`resetState()` → Manual → "Acme" + "Sydney" → Next. Empty rooms list. Type "Room A" + "Hawke's Bay" + click crop input → dropdown shows 8 crops. Type "app" → 5 apple cultivars only. Click "Apples — Gala" → field fills, dropdown closes. Click "Add room to list" → row added. Add a 2nd room with a different crop. Click Remove on first → gone. Click "Done" → fetch-animation placeholder.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: wizard step 2 with crop autocomplete and room list management"
```

---

## Task 8: Fetch animation view

**Files:**
- Modify: `index.html` — `renderFetchAnimation()` and add fetch CSS

- [ ] **Step 1: Define success criterion**

Land on view → "Fetching optimal storage levels from UC Davis Postharvest Center…" + spinner for 2 seconds → auto-routes to `dashboard` view.

- [ ] **Step 2: Add CSS**

```css
/* === FETCH ANIMATION === */
.fetch-screen { text-align: center; color: #f0f7f0; }
.fetch-screen .uc-davis { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #a8c5a0; margin-bottom: 16px; }
.fetch-screen h2 { font-size: 24px; font-weight: 600; margin-bottom: 32px; }
.fetch-screen .spinner { border-color: #2a3a2a; border-top-color: #4caf50; }
.fetch-screen .room-tally { color: #a8c5a0; font-size: 13px; margin-top: 24px; }
```

- [ ] **Step 3: Replace `renderFetchAnimation()`**

```js
function renderFetchAnimation(app) {
  const facility = state.facility;
  if (!facility) { setView('splash'); return; }
  app.innerHTML = `
    <div class="fetch-screen">
      <div class="uc-davis">UC Davis Postharvest Technology Center</div>
      <h2>Fetching optimal storage levels…</h2>
      <div class="spinner"></div>
      <div class="room-tally" id="tally">Configuring ${facility.rooms.length} cool-rooms</div>
    </div>
  `;
  const messages = [
    'Configuring ' + facility.rooms.length + ' cool-rooms',
    'Loading ethylene thresholds',
    'Setting temperature & humidity targets',
    'Calibrating O2 / CO2 ranges'
  ];
  let i = 0;
  const interval = setInterval(() => {
    i = (i + 1) % messages.length;
    const el = document.getElementById('tally');
    if (el) el.textContent = messages[i];
  }, 500);
  setTimeout(() => {
    clearInterval(interval);
    setView('dashboard');
  }, 2000);
}
```

- [ ] **Step 4: Smoke check**

After completing wizard or AI accept → 2-sec animation with rotating tally text → auto-routes to "Dashboard (todo)".

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: UC Davis fetch animation"
```

---

## Task 9: Facility dashboard — header + grid view

**Files:**
- Modify: `index.html` — `renderDashboard()` and add dashboard CSS

- [ ] **Step 1: Define success criterion**

Lands on dashboard with:
- Header: PostHarvest logo, breadcrumbs (LOCATIONS ✓ FACILITY ✓ ROOM ○), facility name, user avatar, "Reset Demo" button.
- Below header: facility name large, view toggle [Map | Grid], "+ Add Room" button.
- Grid view shows tile per room with: room name, crop, ethylene reading, status badge.
- Click a tile → routes to `room` view with `currentRoomId` set.

Map button switches to map view (covered in Task 10).

- [ ] **Step 2: Add CSS** (this section is the largest — covers shared frame + grid)

```css
/* === DASHBOARD FRAME === */
body { background: #1a1a1a; }
#app { padding: 30px 20px; align-items: flex-start; }
.frame { background: #0d0d0d; border-radius: 18px; padding: 6px; width: 100%; max-width: 1100px; box-shadow: 0 30px 80px rgba(0,0,0,0.8); margin: 0 auto; }
.dash { background: #f0f7f0; border-radius: 13px; overflow: hidden; }
.dash-nav { background: #1a6b1a; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; }
.dash-nav .logo { display: flex; align-items: center; gap: 8px; color: white; font-weight: 700; font-size: 15px; }
.dash-nav .crumbs { display: flex; align-items: center; gap: 8px; color: rgba(255,255,255,0.85); font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
.dash-nav .crumb-dot { width: 18px; height: 18px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; }
.dash-nav .crumb-dot.done { background: #4caf50; color: white; }
.dash-nav .crumb-dot.active { background: #4db6ac; color: white; }
.dash-nav .crumb-dot.todo { background: rgba(255,255,255,0.2); color: rgba(255,255,255,0.6); }
.dash-nav .crumb-line { width: 24px; height: 2px; background: rgba(255,255,255,0.3); }
.dash-nav .user { display: flex; align-items: center; gap: 8px; color: white; font-size: 12px; }
.dash-nav .reset { background: rgba(255,255,255,0.15); color: white; border: none; padding: 6px 12px; border-radius: 16px; font-size: 11px; cursor: pointer; }
.dash-nav .reset:hover { background: rgba(255,255,255,0.25); }

/* === FACILITY HEADER === */
.fac-header { padding: 20px 24px; background: white; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e0e0e0; }
.fac-header .title h2 { font-size: 22px; color: #1a1a1a; }
.fac-header .title .hq { color: #888; font-size: 13px; margin-top: 2px; }
.fac-header .actions { display: flex; gap: 10px; align-items: center; }
.toggle { display: inline-flex; background: #f0f0f0; border-radius: 20px; padding: 3px; }
.toggle button { background: transparent; border: none; padding: 6px 16px; font-size: 12px; font-weight: 600; cursor: pointer; border-radius: 16px; color: #888; }
.toggle button.active { background: #2e7d32; color: white; }
.add-room-btn { background: #2e7d32; color: white; border: none; padding: 8px 16px; border-radius: 18px; cursor: pointer; font-size: 12px; font-weight: 600; }

/* === FACILITY BODY === */
.fac-body { padding: 24px; min-height: 480px; background: #f0f7f0; }
.grid-tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.tile { background: white; border-radius: 12px; padding: 18px; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }
.tile:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.tile h4 { font-size: 15px; color: #1a1a1a; margin-bottom: 4px; }
.tile .crop { color: #1a6b1a; font-size: 12px; margin-bottom: 12px; font-weight: 600; }
.tile .ethy { font-size: 28px; font-weight: 700; color: #1a1a1a; }
.tile .ethy small { font-size: 12px; font-weight: 500; color: #888; }
.tile .badge { display: inline-block; padding: 4px 10px; border-radius: 10px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 8px; }
.badge.ok { background: #e8f5e9; color: #1a6b1a; }
.badge.warn { background: #fff5e1; color: #b87800; }
.badge.crit { background: #fff5f4; color: #c0392b; }
.tile .atmos-pill { display: inline-block; margin-top: 8px; margin-left: 8px; font-size: 10px; padding: 4px 10px; border-radius: 10px; background: #f0f0f0; color: #888; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }
.tile .atmos-pill.on { background: #1a6b1a; color: white; }

#map-container { width: 100%; height: 460px; border-radius: 12px; }
```

- [ ] **Step 3: Add helpers `roomEthylene()`, `roomStatus()`, and `renderDashboard()`**

```js
// === ROOM HELPERS ===
function roomEthylene(room) {
  // very lightweight: optimal mid-low if atmos on, drift band if off
  const crop = CROPS[room.cropId];
  const thresholdNum = parseFloat((crop.ethyleneThreshold || '0.1').replace(/[<>\sa-zA-Z]/g, '')) || 0.1;
  if (room.atmosOn) {
    return Math.round((thresholdNum * 0.8) * 1000) / 1000;
  } else {
    return Math.round((thresholdNum * 4) * 1000) / 1000;
  }
}

function roomStatus(room) {
  return room.atmosOn ? 'ok' : 'warn';
}

function renderDashboard(app) {
  const facility = state.facility;
  if (!facility) { setView('splash'); return; }

  app.innerHTML = `
    <div class="frame">
      <div class="dash">
        <div class="dash-nav">
          <div class="logo">🌱 PostHarvest</div>
          <div class="crumbs">
            <span>LOCATIONS</span><span class="crumb-dot done">✓</span>
            <span class="crumb-line"></span>
            <span>FACILITY</span><span class="crumb-dot active">●</span>
            <span class="crumb-line"></span>
            <span>ROOM</span><span class="crumb-dot todo">○</span>
          </div>
          <div class="user">
            <button class="reset" id="reset-btn">Reset Demo</button>
            <span>${(facility.name || 'demo').slice(0, 20)}</span>
            <div style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-size:14px;">👤</div>
          </div>
        </div>

        <div class="fac-header">
          <div class="title">
            <h2>${facility.name}</h2>
            <div class="hq">${facility.hq} · ${facility.rooms.length} cool-rooms</div>
          </div>
          <div class="actions">
            <div class="toggle">
              <button id="t-map" class="${state.dashboardView === 'map' ? 'active' : ''}">Map</button>
              <button id="t-grid" class="${state.dashboardView === 'grid' ? 'active' : ''}">Grid</button>
            </div>
            <button class="add-room-btn" id="add-room">+ Add Room</button>
          </div>
        </div>

        <div class="fac-body">
          ${state.dashboardView === 'grid' ? `
            <div class="grid-tiles">
              ${facility.rooms.map(r => {
                const crop = CROPS[r.cropId];
                const ethy = roomEthylene(r);
                const status = roomStatus(r);
                return `
                  <div class="tile" data-id="${r.id}">
                    <h4>${r.name}</h4>
                    <div class="crop">${crop.displayName}</div>
                    <div class="ethy">${ethy.toFixed(3)} <small>ppm</small></div>
                    <span class="badge ${status}">${r.atmosOn ? 'At optimal' : 'Operational'}</span>
                    <span class="atmos-pill ${r.atmosOn ? 'on' : ''}">Atmos ${r.atmosOn ? 'ON' : 'OFF'}</span>
                  </div>
                `;
              }).join('')}
            </div>
          ` : `
            <div id="map-container"></div>
          `}
        </div>
      </div>
    </div>
  `;

  document.getElementById('reset-btn').onclick = () => { if (confirm('Reset demo to splash?')) resetState(); };
  document.getElementById('t-map').onclick = () => { state.dashboardView = 'map'; saveState(); render(); };
  document.getElementById('t-grid').onclick = () => { state.dashboardView = 'grid'; saveState(); render(); };
  document.getElementById('add-room').onclick = () => { state.wizardDraft = { name: facility.name, hq: facility.hq, rooms: facility.rooms.map(r => ({ ...r })) }; setView('wizard-step2'); };

  if (state.dashboardView === 'grid') {
    document.querySelectorAll('.tile').forEach(el => {
      el.onclick = () => {
        state.currentRoomId = el.dataset.id;
        setView('room');
      };
    });
  }
  // map handled in Task 10
}
```

- [ ] **Step 4: Smoke check**

Complete a flow into dashboard. Header shows facility name, breadcrumbs, Reset Demo button. Default view = `map` per state default — toggle to Grid by clicking Grid button. Tiles render: 4 tiles for Rockit (or however many you set up), each with room name, crop, ethylene reading (e.g., "0.320 ppm"), "Operational" badge, "Atmos OFF" pill. Click a tile → routes to "Room (todo)". Reset Demo → confirm → splash. `+ Add Room` routes to wizard-step2 with existing rooms preloaded.

(Map view will currently render an empty container — that's fine until Task 10.)

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: facility dashboard frame and grid tile view"
```

---

## Task 10: Facility dashboard — Leaflet map view

**Files:**
- Modify: `index.html` — extend `renderDashboard()` to init Leaflet when `dashboardView === 'map'`

- [ ] **Step 1: Define success criterion**

Click "Map" toggle → Leaflet map renders centered on `facility.lat/lng`, with a colored circle marker per room (green if atmos on, amber if off). Clicking a marker pops up "<Room name> — <Crop> — <ethylene> ppm" with an "Open" link that routes to `room` view.

- [ ] **Step 2: Append `initFacilityMap()` and call it from `renderDashboard()`**

Inside `renderDashboard()`, after the existing `if (state.dashboardView === 'grid') { ... }` block, append:

```js
  if (state.dashboardView === 'map') {
    setTimeout(() => initFacilityMap(facility), 0);
  }
```

Then add this function below `renderDashboard`:

```js
let _leafletMap = null;
function initFacilityMap(facility) {
  const el = document.getElementById('map-container');
  if (!el) return;
  if (_leafletMap) { _leafletMap.remove(); _leafletMap = null; }
  _leafletMap = L.map(el).setView([facility.lat, facility.lng], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap'
  }).addTo(_leafletMap);

  facility.rooms.forEach(room => {
    const crop = CROPS[room.cropId];
    const ethy = roomEthylene(room);
    const color = room.atmosOn ? '#2e7d32' : '#ff9800';
    const marker = L.circleMarker([room.lat, room.lng], {
      radius: 10,
      fillColor: color,
      color: '#fff',
      weight: 2,
      fillOpacity: 0.9
    }).addTo(_leafletMap);
    marker.bindPopup(`
      <div style="font-family:'Segoe UI',sans-serif;font-size:13px;min-width:180px;">
        <strong>${room.name}</strong><br>
        ${crop.displayName}<br>
        <span style="color:#888;">Ethylene: ${ethy.toFixed(3)} ppm</span><br>
        <a href="#" onclick="event.preventDefault(); state.currentRoomId='${room.id}'; setView('room');">Open room →</a>
      </div>
    `);
  });
}
```

- [ ] **Step 3: Smoke check**

Default route after fetch-animation lands on map view (since `dashboardView` default is `'map'`). Map renders OSM tiles, pins drop at room locations. Multi-region facilities (Costa, Driscoll's) should pan/zoom out to fit (set view to `6` is OK; bonus: `_leafletMap.fitBounds()` if facility has multiple regions). Click a pin → popup → "Open room →" → routes to room view.

- [ ] **Step 4: Polish: fit bounds for multi-region facilities**

Replace the `setView` line in `initFacilityMap` with:

```js
  if (facility.rooms.length > 1) {
    const bounds = L.latLngBounds(facility.rooms.map(r => [r.lat, r.lng]));
    _leafletMap.fitBounds(bounds, { padding: [40, 40] });
  } else {
    _leafletMap.setView([facility.lat, facility.lng], 8);
  }
```

Re-test with Costa Group (rooms across 3 regions) — map should pan/zoom to show all.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: Leaflet map view with per-room markers"
```

---

## Task 11: Room dashboard layout (port from existing demo)

**Files:**
- Modify: `index.html` — `renderRoom()` and add room CSS

- [ ] **Step 1: Define success criterion**

Click a room tile → room dashboard renders with:
- Same header frame as facility dashboard, with breadcrumbs LOCATIONS ✓ FACILITY ✓ ROOM ●
- Tabs row: Overview (active), Config / Reports / Readings / Pair (clicking shows alert "Coming soon")
- Crop summary strip with optimal ranges (CA/DCA pill, temp, humidity, ethylene, O2, CO2)
- ATMOS toggle + status text
- 5 horizontal bars (ethylene, temperature, humidity, pressure, oxygen) with target labels
- Right-side stat card (large ethylene reading + 4 mini-stats + status badge)
- Bottom chart placeholder (will be filled in Task 13)
- Back button → facility dashboard

ATMOS toggle stub — flip `state.facility.rooms[i].atmosOn` and re-render. Visible state change required (badge text + bar widths). Detail values come in Task 12.

- [ ] **Step 2: Add CSS** (room layout — port + simplify from existing dashboard)

```css
/* === ROOM === */
.tabs-row { background: white; padding: 0 24px; display: flex; align-items: center; border-bottom: 1px solid #e0e0e0; }
.tabs-row .room-name { font-size: 18px; font-weight: 700; color: #1a1a1a; margin-right: 24px; padding: 14px 0; }
.tabs-row .tab { padding: 14px 16px; font-size: 11px; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; cursor: pointer; color: #888; }
.tabs-row .tab.active { color: white; background: #2e7d32; border-radius: 18px; margin: 6px 4px; padding: 8px 16px; }
.tabs-row .back { margin-left: auto; padding: 14px 0; color: #888; cursor: pointer; font-size: 13px; }
.tabs-row .back:hover { color: #2e7d32; }
.crop-strip { padding: 14px 24px; background: white; display: flex; align-items: center; gap: 24px; border-bottom: 1px solid #f0f0f0; font-size: 12px; }
.crop-strip .col { display: flex; align-items: baseline; gap: 6px; }
.crop-strip .col .lbl { color: #888; font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase; }
.crop-strip .col .val { color: #1a1a1a; font-weight: 600; }
.crop-strip .col .val.alert { color: #c0392b; font-weight: 700; }
.crop-strip .ca-pill { background: #2e7d32; color: white; padding: 3px 10px; border-radius: 10px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; }
.crop-strip .note { color: #888; font-style: italic; font-size: 11px; margin-left: auto; max-width: 240px; }
.atmos-bar { background: #e8f5e9; padding: 12px 24px; display: flex; align-items: center; gap: 16px; }
.atmos-bar .demo-pill { background: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; color: #888; letter-spacing: 1px; }
.atmos-toggle { background: white; padding: 8px 18px; border-radius: 22px; border: 2px solid #2e7d32; cursor: pointer; font-weight: 700; font-size: 13px; color: #2e7d32; display: inline-flex; align-items: center; gap: 8px; }
.atmos-toggle.on { background: #2e7d32; color: white; }
.atmos-status { font-size: 13px; color: #1a6b1a; }
.atmos-status.warn { color: #b87800; }
.room-body { padding: 20px 24px; display: grid; grid-template-columns: 1fr 240px; gap: 16px; background: #f0f7f0; }
.bars-card { background: white; border-radius: 10px; padding: 18px; }
.bar-row { display: grid; grid-template-columns: 110px 1fr 90px; gap: 12px; align-items: center; padding: 10px 0; }
.bar-row .lbl { font-size: 11px; color: #888; letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; }
.bar-track { background: #f0f0f0; height: 14px; border-radius: 7px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 7px; transition: width 1.2s cubic-bezier(.2,.7,.3,1), background 1.2s; }
.bar-row .target { font-size: 11px; color: #888; text-align: right; }
.stat-card { background: white; border-radius: 10px; padding: 16px; }
.stat-card .ethy-big { font-size: 36px; font-weight: 700; color: #1a1a1a; line-height: 1; margin-top: 6px; }
.stat-card .ethy-big small { font-size: 12px; color: #888; font-weight: 500; }
.stat-card .label-row { font-size: 10px; color: #888; letter-spacing: 1px; text-transform: uppercase; }
.stat-card .target-line { color: #888; font-size: 11px; margin-top: 4px; }
.stat-card .mini-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 12px; margin-top: 14px; }
.mini { font-size: 12px; }
.mini .v { font-size: 16px; font-weight: 700; color: #1a1a1a; }
.mini .l { color: #888; font-size: 9px; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 2px; }
.mini .t { color: #888; font-size: 9px; margin-top: 2px; }
.system-status-card { background: white; border-radius: 10px; padding: 14px; margin-top: 12px; text-align: center; }
.system-status-card .lbl { font-size: 10px; color: #888; letter-spacing: 1px; text-transform: uppercase; }
.system-status-card .pill { background: #2e7d32; color: white; padding: 6px 14px; border-radius: 14px; font-size: 12px; font-weight: 700; margin-top: 6px; display: inline-block; }
.system-status-card .pill.warn { background: #b87800; }
.chart-card { background: white; border-radius: 10px; padding: 16px; margin: 16px 24px 24px; }
```

- [ ] **Step 3: Replace `renderRoom()`**

```js
function renderRoom(app) {
  const facility = state.facility;
  if (!facility) { setView('splash'); return; }
  const room = facility.rooms.find(r => r.id === state.currentRoomId);
  if (!room) { setView('dashboard'); return; }
  const crop = CROPS[room.cropId];
  const ethy = roomEthylene(room);
  const ethyClass = room.atmosOn ? '' : 'alert';
  const status = room.atmosOn ? 'at optimal' : 'operational';
  const statusClass = room.atmosOn ? '' : 'warn';
  const atmosOn = room.atmosOn;

  // Bar fill widths (drift wider, optimal narrower & green)
  const fills = computeBarFills(room);

  app.innerHTML = `
    <div class="frame">
      <div class="dash">
        <div class="dash-nav">
          <div class="logo">🌱 PostHarvest</div>
          <div class="crumbs">
            <span>LOCATIONS</span><span class="crumb-dot done">✓</span>
            <span class="crumb-line"></span>
            <span>FACILITY</span><span class="crumb-dot done">✓</span>
            <span class="crumb-line"></span>
            <span>ROOM</span><span class="crumb-dot active">●</span>
          </div>
          <div class="user">
            <button class="reset" id="reset-btn">Reset Demo</button>
            <span>${(facility.name || 'demo').slice(0, 20)}</span>
            <div style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-size:14px;">👤</div>
          </div>
        </div>

        <div class="tabs-row">
          <div class="room-name">${room.name}</div>
          <div class="tab active">Overview</div>
          <div class="tab" data-stub>Config</div>
          <div class="tab" data-stub>Reports</div>
          <div class="tab" data-stub>Readings</div>
          <div class="tab" data-stub>Pair</div>
          <div class="back" id="back-to-fac">← Back to facility</div>
        </div>

        <div class="crop-strip">
          <div class="col"><span class="val">${crop.displayName.split(' — ')[0]}</span><span class="lbl">${crop.displayName.includes('—') ? '— ' + crop.displayName.split(' — ')[1] : ''}</span></div>
          <div class="ca-pill">CA/DCA</div>
          <div class="col"><span class="lbl">Temp</span><span class="val">${crop.tempRange}</span></div>
          <div class="col"><span class="lbl">Humidity</span><span class="val">${crop.humidityRange}</span></div>
          <div class="col"><span class="lbl">Ethylene</span><span class="val alert">${crop.ethyleneThreshold}</span></div>
          <div class="col"><span class="lbl">O₂</span><span class="val">${crop.o2Range}</span></div>
          <div class="col"><span class="lbl">CO₂</span><span class="val">${crop.co2Range}</span></div>
          <div class="note">${crop.sensitivity}</div>
        </div>

        <div class="atmos-bar">
          <span class="demo-pill">DEMO</span>
          <button class="atmos-toggle ${atmosOn ? 'on' : ''}" id="atmos-toggle">⏻ ATMOS ${atmosOn ? 'ON' : 'OFF'}</button>
          <span class="atmos-status ${statusClass}">${atmosOn ? '✓ All 5 factors at ' + crop.displayName.split(' — ')[1] || crop.displayName.split(' — ')[0] + ' optimal — Atmos is working' : 'Press to see Atmos bring all factors to ' + crop.displayName + ' optimal levels'}</span>
        </div>

        <div class="room-body">
          <div class="bars-card">
            <div class="bar-row"><span class="lbl">Ethylene</span><div class="bar-track"><div class="bar-fill" style="width:${fills.ethylene.w}%;background:${fills.ethylene.color}"></div></div><span class="target">→ ${crop.ethyleneThreshold}</span></div>
            <div class="bar-row"><span class="lbl">Temperature</span><div class="bar-track"><div class="bar-fill" style="width:${fills.temp.w}%;background:${fills.temp.color}"></div></div><span class="target">→ ${crop.tempRange}</span></div>
            <div class="bar-row"><span class="lbl">Humidity</span><div class="bar-track"><div class="bar-fill" style="width:${fills.hum.w}%;background:${fills.hum.color}"></div></div><span class="target">→ ${crop.humidityRange}</span></div>
            <div class="bar-row"><span class="lbl">Pressure</span><div class="bar-track"><div class="bar-fill" style="width:${fills.pres.w}%;background:${fills.pres.color}"></div></div><span class="target">→ ${crop.pressure}</span></div>
            <div class="bar-row"><span class="lbl">Oxygen</span><div class="bar-track"><div class="bar-fill" style="width:${fills.o2.w}%;background:${fills.o2.color}"></div></div><span class="target">→ ${crop.o2Range}</span></div>
          </div>
          <div>
            <div class="stat-card">
              <div class="label-row">ETHYLENE READING</div>
              <div class="ethy-big">${ethy.toFixed(3)}</div>
              <div class="target-line">Target: ${crop.ethyleneThreshold}</div>
              <div class="mini-grid">
                <div class="mini"><div class="v">${fills.hum.value}%</div><div class="l">HUMIDITY</div><div class="t">→ ${crop.humidityRange}</div></div>
                <div class="mini"><div class="v">${fills.temp.value}°C</div><div class="l">TEMPERATURE</div><div class="t">→ ${crop.tempRange}</div></div>
                <div class="mini"><div class="v">${fills.pres.value} atm</div><div class="l">PRESSURE</div><div class="t">→ ${crop.pressure}</div></div>
                <div class="mini"><div class="v">${fills.o2.value}%</div><div class="l">OXYGEN</div><div class="t">→ ${crop.o2Range}</div></div>
              </div>
            </div>
            <div class="system-status-card">
              <div class="lbl">SYSTEM STATUS</div>
              <span class="pill ${statusClass}">${atmosOn ? '✓ at optimal' : '⚠ ' + status}</span>
            </div>
          </div>
        </div>

        <div class="chart-card" id="chart-card">
          <div style="font-size:11px;color:#888;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:8px;">24-hour history</div>
          <div id="chart-mount" style="height:220px;display:flex;align-items:center;justify-content:center;color:#888;font-size:13px;">(chart appears in Task 13)</div>
        </div>
      </div>
    </div>
  `;

  document.getElementById('reset-btn').onclick = () => { if (confirm('Reset demo to splash?')) resetState(); };
  document.getElementById('back-to-fac').onclick = () => { state.currentRoomId = null; setView('dashboard'); };
  document.querySelectorAll('[data-stub]').forEach(el => el.onclick = () => alert('"' + el.textContent + '" tab — coming soon'));
  document.getElementById('atmos-toggle').onclick = () => {
    room.atmosOn = !room.atmosOn;
    saveState();
    render();
  };
}
```

(Note: `computeBarFills(room)` is a placeholder — will be implemented in Task 12. For this task, add a temporary stub at the end of the script.)

- [ ] **Step 3.5: Add temporary `computeBarFills` stub**

```js
function computeBarFills(room) {
  const on = room.atmosOn;
  const greenColor = '#2e7d32';
  const tealColor = '#4db6ac';
  const lightTeal = '#a8d8d4';
  const ethyleneNum = roomEthylene(room);
  return {
    ethylene: { w: on ? 18 : 70, color: on ? greenColor : '#c0392b', value: ethyleneNum.toFixed(3) },
    temp:     { w: on ? 22 : 55, color: greenColor, value: on ? '0.5' : '3.8' },
    hum:      { w: on ? 92 : 88, color: tealColor,  value: on ? '92.5' : '91.7' },
    pres:     { w: on ? 50 : 48, color: tealColor,  value: '1.01' },
    o2:       { w: on ? 25 : 70, color: lightTeal,  value: on ? '1.75' : '20.8' }
  };
}
```

- [ ] **Step 4: Smoke check**

Click any tile → room dashboard. Header crumbs: ROOM is now active dot. Crop strip shows CA/DCA pill + correct optimal ranges per crop. Click ATMOS button → toggles ON/OFF. ON: bars shrink/turn green-ish, ethylene reading drops (from e.g. 0.320 → 0.080), status badge turns "✓ at optimal" with green color. OFF: ethylene back up, badge "⚠ operational" amber. Bars animate (CSS transition). Click "Back to facility" → returns to dashboard with that room's atmos state preserved (visible in tile pill). Refresh → state preserved.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: room dashboard with bars, stats, ATMOS toggle"
```

---

## Task 12: Drift values + live jitter (setInterval)

**Files:**
- Modify: `index.html` — replace `computeBarFills` stub with crop-aware drift logic; add `tickRoomLive()` interval

- [ ] **Step 1: Define success criterion**

While ATMOS is OFF, ethylene reading and bar widths jitter slightly every 2 seconds (visibly alive). When ATMOS is ON, values stay rock-steady at optimal. Switching rooms, then refreshing, then toggling ATMOS — never crashes; jitter resets cleanly.

- [ ] **Step 2: Replace `computeBarFills` with**

```js
function rangeMid(rangeStr) {
  // accepts "0–1°C", "-1–0°C", "13°C", "<0.1 ppm", "92%", "1.01 atm", "0.5°C", "1.5–2%"
  const cleaned = String(rangeStr).replace(/[^\d\.\-––]/g, ''); // keep digits, ., -, en dash
  const parts = cleaned.split(/[––-]/).filter(Boolean).map(parseFloat);
  if (parts.length === 0) return 0;
  if (parts.length === 1) return parts[0];
  return (parts[0] + parts[1]) / 2;
}

function ethyleneTargetNum(crop) {
  const m = String(crop.ethyleneThreshold).match(/[0-9]*\.?[0-9]+/);
  return m ? parseFloat(m[0]) : 0.1;
}

function jitter(base, amplitude) {
  return base + (Math.random() * 2 - 1) * amplitude;
}

function computeBarFills(room) {
  const crop = CROPS[room.cropId];
  const on = room.atmosOn;
  const greenColor = '#2e7d32';
  const tealColor = '#4db6ac';
  const lightTeal = '#a8d8d4';

  // Ethylene
  const ethyTarget = ethyleneTargetNum(crop);
  const ethyValue = on ? jitter(ethyTarget * 0.8, ethyTarget * 0.05) : jitter(ethyTarget * 4, ethyTarget * 0.5);
  const ethyW = on ? Math.min(25, (ethyValue / ethyTarget) * 30) : Math.min(80, (ethyValue / ethyTarget) * 25);

  // Temp
  const tempMid = rangeMid(crop.tempRange);
  const tempVal = on ? jitter(tempMid, 0.2) : jitter(tempMid + 3, 0.5);
  const tempW = on ? 25 : 55;

  // Humidity
  const humMid = rangeMid(crop.humidityRange);
  const humVal = on ? jitter(humMid, 0.5) : jitter(humMid - 3, 1);
  const humW = on ? 92 : 84;

  // Pressure (always near 1.01)
  const presVal = jitter(1.01, on ? 0.005 : 0.02);
  const presW = on ? 50 : 52;

  // O2
  const o2Mid = rangeMid(crop.o2Range);
  const o2Val = on ? jitter(o2Mid, 0.1) : jitter(20.8, 0.3);
  const o2W = on ? 25 : 75;

  return {
    ethylene: { w: ethyW, color: on ? greenColor : '#c0392b', value: ethyValue.toFixed(3) },
    temp:     { w: tempW, color: greenColor, value: tempVal.toFixed(1) },
    hum:      { w: humW,  color: tealColor,  value: humVal.toFixed(1) },
    pres:     { w: presW, color: tealColor,  value: presVal.toFixed(2) },
    o2:       { w: o2W,   color: lightTeal,  value: o2Val.toFixed(2) }
  };
}
```

- [ ] **Step 3: Add live tick (jitter every 2 seconds while on `room` view)**

At the bottom of the script (just before the final `loadState(); render();`):

```js
let _liveTickInterval = null;

function startLiveTick() {
  if (_liveTickInterval) clearInterval(_liveTickInterval);
  _liveTickInterval = setInterval(() => {
    if (state.view !== 'room') return;
    const facility = state.facility;
    if (!facility) return;
    const room = facility.rooms.find(r => r.id === state.currentRoomId);
    if (!room) return;
    // Only re-render bars + stats, not the whole page (keep ATMOS toggle clicks responsive)
    const fills = computeBarFills(room);
    const ethyEl = document.querySelector('.ethy-big');
    if (ethyEl) ethyEl.firstChild.nodeValue = fills.ethylene.value;
    document.querySelectorAll('.bar-row').forEach((row, i) => {
      const keys = ['ethylene', 'temp', 'hum', 'pres', 'o2'];
      const k = keys[i];
      const fill = row.querySelector('.bar-fill');
      if (fill) {
        fill.style.width = fills[k].w + '%';
        fill.style.background = fills[k].color;
      }
    });
    const minis = document.querySelectorAll('.mini .v');
    if (minis.length === 4) {
      minis[0].textContent = fills.hum.value + '%';
      minis[1].textContent = fills.temp.value + '°C';
      minis[2].textContent = fills.pres.value + ' atm';
      minis[3].textContent = fills.o2.value + '%';
    }
  }, 2000);
}

startLiveTick();
```

- [ ] **Step 4: Smoke check**

Open a room with ATMOS OFF. Watch for ~10 seconds. Ethylene reading and bar widths jitter every 2 seconds. Toggle ATMOS ON → numbers settle at optimal-mid, jitter is barely visible. Toggle OFF → resumes drifting. Navigate away from room (back to dashboard) → no errors, no orphan timers visible (the interval check `if (state.view !== 'room') return` handles this).

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: drift jitter + live tick on room view"
```

---

## Task 13: 24-hour chart with ATMOS ACTIVATED line

**Files:**
- Modify: `index.html` — replace `(chart appears in Task 13)` placeholder with inline SVG chart

- [ ] **Step 1: Define success criterion**

Room view shows a 24-hour line chart spanning 5 series (ethylene, temp, humidity, pressure, oxygen). When ATMOS is ON, a vertical dashed line labeled "ATMOS ACTIVATED" appears at ~70% across, and the right portion of each line is flat at optimal-mid. When ATMOS is OFF, all 5 lines drift across the full 24 hours.

- [ ] **Step 2: Add chart helper and replace placeholder**

In `renderRoom()`, replace:

```js
<div id="chart-mount" style="height:220px;display:flex;align-items:center;justify-content:center;color:#888;font-size:13px;">(chart appears in Task 13)</div>
```

with:

```js
<div id="chart-mount">${chartSvg(room)}</div>
```

Add this function alongside `computeBarFills`:

```js
function chartSvg(room) {
  const crop = CROPS[room.cropId];
  const W = 980, H = 220, padL = 40, padR = 100, padT = 20, padB = 30;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const N = 48; // 30-min ticks across 24h
  const activatedAt = N * 0.7; // ~17:00 if start = 11:00
  const on = room.atmosOn;

  function pathFor(beforeBase, afterBase, beforeAmp, afterAmp, scaleMin, scaleMax, color) {
    const points = [];
    for (let i = 0; i < N; i++) {
      const isBefore = i < activatedAt;
      let v;
      if (on) {
        v = isBefore ? beforeBase + (Math.random() - 0.5) * beforeAmp : afterBase + (Math.random() - 0.5) * afterAmp;
      } else {
        v = beforeBase + (Math.random() - 0.5) * beforeAmp;
      }
      const x = padL + (i / (N - 1)) * innerW;
      const y = padT + innerH - ((v - scaleMin) / (scaleMax - scaleMin)) * innerH;
      points.push([x, y]);
    }
    const d = points.map((p, i) => (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
    return `<path d="${d}" stroke="${color}" stroke-width="1.6" fill="none"/>`;
  }

  // Lines normalized into one shared 0..30 scale (just for drawing)
  // ethylene (red-green), temperature (dark green), humidity (light teal), pressure (teal), oxygen (light teal)
  const ethyTarget = ethyleneTargetNum(crop);
  const tempMid = rangeMid(crop.tempRange);
  const humMid = rangeMid(crop.humidityRange);
  const o2Mid = rangeMid(crop.o2Range);

  const lines = [
    pathFor(ethyTarget * 4, ethyTarget * 0.8, ethyTarget * 1.5, ethyTarget * 0.05, 0, ethyTarget * 6, '#1a6b1a'),                // ethylene
    pathFor(tempMid + 3, tempMid, 0.6, 0.2, tempMid - 5, tempMid + 8, '#4caf50'),                                                  // temp
    pathFor(humMid - 2, humMid, 1.5, 0.4, humMid - 12, humMid + 4, '#7fc4be'),                                                     // humidity
    pathFor(1.01, 1.01, 0.04, 0.005, 0.95, 1.10, '#4db6ac'),                                                                       // pressure
    pathFor(o2Mid * 6, o2Mid, 0.8, 0.1, 0, o2Mid * 8, '#a8d8d4')                                                                  // oxygen
  ];

  const activatedX = padL + (activatedAt / (N - 1)) * innerW;
  const activatedLine = on ? `
    <line x1="${activatedX}" y1="${padT}" x2="${activatedX}" y2="${H - padB}" stroke="#1a6b1a" stroke-width="1.5" stroke-dasharray="4 3"/>
    <rect x="${activatedX - 60}" y="${padT - 14}" width="120" height="20" fill="#1a6b1a" rx="3"/>
    <text x="${activatedX}" y="${padT}" fill="white" font-size="10" font-weight="700" text-anchor="middle">ATMOS ACTIVATED</text>
  ` : '';

  // x-axis ticks every 4 hours
  const xLabels = ['11:00','12:10','13:20','14:30','15:40','16:50','18:00','19:10','20:20','21:30','22:50']
    .map((t, i) => {
      const x = padL + (i / 10) * innerW;
      return `<text x="${x}" y="${H - 6}" font-size="9" fill="#888" text-anchor="middle">${t}</text>`;
    }).join('');

  const legend = ['Ethylene', 'Temperature', 'Humidity', 'Pressure', 'Oxygen']
    .map((label, i) => `<text x="${padL + i * 100}" y="${H + 12}" font-size="10" fill="#888">● ${label}</text>`)
    .join('');

  return `<svg viewBox="0 0 ${W} ${H + 24}" preserveAspectRatio="xMidYMid meet" style="width:100%;height:auto;display:block;">
    ${lines.join('\n')}
    ${activatedLine}
    ${xLabels}
    ${legend}
  </svg>`;
}
```

- [ ] **Step 3: Smoke check**

Open a room with ATMOS OFF — chart shows 5 lines drifting across full 24 hours, no ATMOS ACTIVATED label. Toggle ATMOS ON → chart re-renders, vertical dashed line + green "ATMOS ACTIVATED" pill appears ~70% across, lines after the dashed line are flatter (especially ethylene and oxygen). Toggle off → label disappears.

(Lines are randomly generated each render — that's fine for a sales demo.)

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: 24-hour SVG chart with ATMOS ACTIVATED marker"
```

---

## Task 14: Final polish + manual end-to-end demo

**Files:**
- Modify: `index.html` — bug fixes only
- Modify: `README.md` — finalize demo script

- [ ] **Step 1: Run the full demo flow**

`resetState()`. Walk this sequence:
1. Splash → "AI auto-mock"
2. Type "Rockit" → Search → wait 3s → reveal card
3. Click "Looks good — fetch UC Davis levels" → 2s fetch → land on dashboard (map view by default)
4. Verify map: 4 pins around Hawke's Bay, all amber. Click a pin → popup → "Open room →"
5. Lands on room view, ATMOS OFF, ethylene visibly drifting around 0.3+ ppm
6. Click ATMOS ON → 1.5s animation → bars shrink/turn green, ethylene snaps to ~0.08 ppm, status badge turns "✓ at optimal", chart shows ATMOS ACTIVATED line
7. Click "Back to facility" → tile for that room now shows green "Atmos ON" pill + "At optimal" badge
8. Toggle to Grid view → tile colors reflect the toggled room
9. Click "+ Add Room" → wizard step 2 with existing 4 rooms preloaded, add a 5th (Bartlett pear, "Hawke's Bay")
10. Done → 2s fetch → dashboard shows 5 pins / 5 tiles
11. Click "Reset Demo" → confirm → splash

Document any bugs found, fix in this task. Common issues to check:
- Long company names or many rooms breaking the header layout — fix by truncating with `text-overflow: ellipsis` if needed
- Toggle button label "+ Add Room" vs the wizard expecting empty draft — confirmed in Task 9 to preload existing rooms
- Chart re-rendering producing visible flicker on every live-tick — Task 12's surgical update should avoid this; verify

- [ ] **Step 2: Update README with finalized demo script**

```markdown
# PostHarvest Atmos Mock

Single-file HTML sales-demo mock. No build, no backend, no dependencies beyond Leaflet (CDN).

## Demo (90 seconds)

1. **Open `index.html` in Chrome.**
2. Splash → click **AI auto-mock**.
3. Type `Rockit` → **Search** → 3-second "researching" animation → reveal Rockit Apple, 4 cool-rooms, Hawke's Bay NZ.
4. Click **Looks good — fetch UC Davis levels** → 2-second fetch animation → land on facility map.
5. **Map view**: 4 amber pins. Click any pin → popup → **Open room →**.
6. Inside the room: ATMOS is **OFF**, ethylene drifts around 0.3 ppm (red), bars run wide.
7. Click **ATMOS ON** → 1.5-sec snap to optimal. Ethylene falls to ~0.08 ppm. Status: **at optimal**. Chart shows green **ATMOS ACTIVATED** marker.
8. **Back to facility** → toggle to **Grid** view. The room you toggled shows a green **Atmos ON** pill.

## Pre-baked AI companies

| Type… | Reveals |
|---|---|
| `Rockit` | Rockit Apple — 4 rooms, Hawke's Bay NZ |
| `Tru Cape` | Tru Cape — 6 rooms, Ceres South Africa |
| `Calypso` | Calypso Mango — 3 rooms, Bowen QLD |
| `Costa` | Costa Group — 5 rooms, multi-region AU |
| `Driscoll` | Driscoll's — 8 rooms, California |

Anything else → "couldn't find" → falls through to manual wizard.

## Reset

Click **Reset Demo** in the top-right of the dashboard header to wipe localStorage and return to splash.

## State persistence

The demo persists to `localStorage['pht-mock-state-v1']` so a refresh keeps you wherever you were.
```

- [ ] **Step 3: Commit**

```bash
git add index.html README.md
git commit -m "polish: end-to-end demo verification + README"
```

---

## Self-review checklist (run after writing this plan)

- [ ] **Spec coverage:**
  - Splash with 2 paths → Task 4 ✓
  - AI lookup with pre-baked + not-found → Task 5 ✓
  - Manual wizard (2 steps) → Tasks 6, 7 ✓
  - UC Davis fetch animation → Task 8 ✓
  - Facility dashboard map+grid → Tasks 9, 10 ✓
  - Room dashboard + ATMOS toggle → Tasks 11, 12 ✓
  - 24h chart with ATMOS ACTIVATED → Task 13 ✓
  - localStorage persistence → Task 3 ✓
  - Reset Demo → Task 9 ✓
  - 21-crop database → Task 1 ✓
  - 5 pre-baked companies → Task 2 ✓
  - Drift values + live jitter → Task 12 ✓

- [ ] **Placeholder scan:** none — every task has full code blocks. (`computeBarFills` stub in Task 11 is intentional and replaced in Task 12.)

- [ ] **Type consistency:**
  - `state.view` enum identical between Task 3 (definition) and all renderers ✓
  - `roomEthylene(room)` defined Task 9, used Tasks 9, 10, 11 ✓
  - `computeBarFills(room)` stubbed Task 11, replaced Task 12 ✓
  - `state.facility.rooms[i].atmosOn` consistent across tasks ✓
  - `state.dashboardView` enum `'map' | 'grid'` consistent ✓
