# Retirement Flexibility Calculator — Project Context

_Last updated: 2026-11-23_

## What this is

A single-file browser dashboard (`index.html`) built from the original Tkinter app
`retirement_gui.py`. The financial engine is a JavaScript port of the Python
`calculate_scenario()` function, with the original hard-coded life assumptions
now exposed as editable inputs.

No build step or dependencies. The original Tkinter app is untouched.

## Run

- **Live (hosted):** <https://elninost0rm.github.io/retirement-dashboard/>
- **Direct:** double-click `index.html`.
- **Local server:** `python serve.py` or `start_dashboard.bat` →
  <http://127.0.0.1:8420/> (stdlib only; flags `--port`, `--no-browser`).
- **Original desktop app:** `retirement_gui.py` still runs independently.

## Hosting

- Repo: <https://github.com/elninost0rm/retirement-dashboard> (public).
- Pages: served from `main` at the repo root; `index.html` is the entry point.
  No Action or build step is involved.
- Publish: `git add -A && git commit -m "…" && git push`; Pages redeploys in
  about a minute.
- **Working rule:** every change to this project ends with a commit and a push
  to `origin/main`. All edits are made through the agent interface; nothing is
  edited on github.com, so `git pull` is not normally needed.
- `build/` and `dist/` are gitignored. The old PyInstaller output (~22 MB) and
  its `.spec`/`.bat` build files were deleted; the desktop app still runs from
  source with `python retirement_gui.py`.
- Because the site is public, the defaults in `index.html` are world-readable.
  Saved scenarios stay in the visitor's own browser (`localStorage`) and in
  shared `#s=…` links; they are never uploaded.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Entire dashboard: HTML, CSS, JS, engine. |
| `compound.html` | Second app: compounding / withdrawal / safe-rate calculator (ported from `C:\Interest Calc\compound_calculator_v5.py`). |
| `serve.py` | Optional stdlib HTTP server; opens the browser. |
| `start_dashboard.bat` | Windows launcher for `serve.py`. |
| `README.md` | User-facing docs. |
| `retirement_gui.py` | Original Tkinter app, unchanged. |
| `context.md` | This file. |
| `.gitignore` | Excludes Python caches and any future build output. |

## Current defaults and headline numbers

- Balances: **blank on first load** — the two fields show a greyed-out
  `Enter amount` prompt and are held as 0 so the published site shows no
  personal figures. Enter $350,000 / $280,000 to reproduce the numbers below.
  Their sliders run 0–$1,000,000 and 0–$800,000 with $10k ticks.
- Contributions: brokerage $30,000/yr; TSP $14,000/yr.
- Income: new job $32,000/yr; spouse $31,200/yr; high-3 $110,000.
- Spending: base $56,400; ACA $3,792 (household); FEHB $6,000 (household,
  employee share); Medicare $10,000 (household); mortgage saving $9,096.
- Social Security: you $18,397; spouse $13,074 (both claim at 62).
- Ages: current age is **derived from `birthdate`** (default `1987-08-14`)
  against the computer clock — 39 on 2026-11-23, shown to the day; layoff 43,
  you retire 53, spouse retires 56 (her age).
- Returns: nominal 7.0%, inflation 3.0% → real 3.8835%.
- Mortgage payoff: June 2049.
- Pension rules: service start 2011; VERA 2036 / age 49 / 25 years;
  MRA 57 (derived from the 1987 birth date) / 30 years needed at MRA; normal
  pension age 62.
- New-job gap 0 months; severance $0/mo for 1 month; new-job health coverage on;
  FEHB kept in retirement on.
- Stress test off; projection through age 95.

Results with the balances filled in as $350,000 / $280,000 and the default birth
date (age 39 on 2026-11-23): **minimum portfolio $700,175**; **age-95 balance
$4,198,936**. The original Python/Tkinter app produced $5,014,739 at 95 because
the dashboard now phases in Medicare at your age 62 (spouse turns 65) and halves
the household ACA cost for the person still on it. With the balances blank the
plan starts from $0, so the headline shows a low minimum and an early shortfall —
expected, not a bug.

## Engine rules (`calculateScenario` in `index.html`)

All figures are in today's dollars. Balances grow at
`(1 + nominal return) / (1 + inflation) − 1`.

### Pension

- Service years are **auto-calculated** from `service_start_year` at the layoff
  year: `serviceAtLayoff = max(0, layoffYear - serviceStartYear)`.
- `nominalPension = high3 × serviceAtLayoff × (serviceAtLayoff < 20 ? 1.0% : 1.1%)`.
- **No COLA before 62** for any regular FERS annuity. An immediate pension is
  frozen in nominal dollars from its start age until 62, then COLA (so its
  today's-dollar value falls each year before 62).
- **VERA:** only when `layoffYear === veraYear` AND `layoffAge === veraAge` AND
  service ≥ `veraService`. Starts at the VERA age; nominal, eroding to 62, then
  COLA. Pays the **FERS Supplement** from `max(pensionStart, mraAge)` to 62 (5 CFR
  842.503(b)(1): a VERA taken before MRA waits until MRA).
- **MRA+30:** when `layoffAge ≥ mraAge` and service ≥ `mraService`. Starts at the
  layoff age; nominal until 62, then COLA. Also pays the **FERS Supplement**
  from the start age until 62, ≈ `ss_you × service/40`, with no COLA.
- **Normal:** when `layoffAge ≥ normalPensionAge` and service ≥ 5. Starts at the
  layoff age; COLA applies from 62. Gets a supplement only for a 60+20 retirement
  before 62.
- **Deferred:** everything else. Starts at the normal pension age; the nominal
  amount is eroded from the actual leave year to that age. No supplement.
- Pension income is counted **while still working** the new job (bug fixed).
- Example: VERA at 49 with 25 years = $30,250 nominal, $20,599 by 62; MRA+30 at
  57 with 33 years = $39,930 nominal, $34,444 by 62, plus a $15,178/yr FERS
  supplement until 62; deferred at 43 with 19 years = $11,919 at 62.

### Health

- $0 while anyone is working (federal job, spouse job, or new job when the
  coverage toggle is on and the job is active).
- **FEHB** (`fehb_enabled`, default on): only with an **immediate annuity** —
  VERA, MRA+30, or normal. The household `fehb` premium is paid from the pension
  start year for life, even while a spouse still works, and Medicare is added on
  top as each of you turns 65. A deferred annuity cannot keep FEHB, so those
  plans fall back to ACA regardless of the toggle. “FEHB coverage begins” is an
  event on the pension start year.
- **ACA** is a household amount; halved when only one person is on ACA. It is
  ignored whenever FEHB applies.
- Medicare is a household amount; half from your age 62 (spouse turns 65), full
  from your age 65. A “Spouse Medicare begins” event fires at 62. When FEHB
  continues, set `medicare` to Part B only — the FEHB plan acts as the supplement.
- The new-job coverage toggle (`new_job_health`, default on) assumes **family
  coverage** while the new job is active (after the gap, until your retirement
  age). The gap year itself still pays ACA.
- The sidebar dims whichever of ACA/FEHB does not apply and explains why in a
  hint line under the spending group.

### Job, gap, severance, spending

- New-job income starts after `new_job_gap_months` and runs until your retirement
  age; the first year is prorated.
- Severance is **monthly × 1–12 months**, paid from the layoff year only (not
  before). It is a cash inflow to brokerage; the table note shows it separately
  and the cash-flow chart stacks it as a gold income segment. “Net need” is
  shown **after** severance.
- Base spending includes the mortgage until the payoff. Payoff year/month are
  inputs (default 2049/June); the month is the last payment month, so June means
  6 months mortgage + 6 months savings in the payoff year.
- Working-year cash flow uses mortgage-adjusted spending and gap health costs.

### Withdrawals, SS, horizon

- Withdrawals draw brokerage first, then TSP once age ≥ 59.5. Because the loop is
  annual, access effectively starts at age 60; the UI adds a synthetic “TSP
  access (59½)” milestone at 60.
- Balances never go negative. A deficit larger than the balances takes what is
  there and records the rest as **unfunded** (`extra.unfunded_total`, plus a
  per-row `unfunded`); it never borrows or compounds a negative balance.
- Pre-59½ shortfall sets the brokerage-failed warning.
- Displayed columns always add up: `total` is the rounded sum of the unrounded
  balances, and the TSP column absorbs the ±$1 rounding difference.
- Your SS starts at 62; spouse SS starts at your age 59 (spouse 62). Claim ages
  are fixed; no early/late adjustment.
- Projection ends at your age 95 (spouse is 98 at the end).

## UI

- **Header:** Save (name dialog), Saved (count + popover library), Pin (compare,
  up to 4), Reset, theme toggle.
- **Hero:** minimum portfolio, portfolio at 95, funded-through age (a year with
  unfunded spending ends the run), real return, brokerage low before 59½,
  sparkline.
- **Input rail:** static (no internal scroll/sticky), scrolls with the page.
  Every dollar, year, month, age, and service field is a slider with an editable
  value chip. Hover a slider or chip and scroll to nudge; Shift+scroll = 10×.
  The one exception is **current age**: it comes from the `birthdate` date field
  (no slider) and displays as years/months/days plus the next birthday.
- **Tick sizes:** $10k for six-digit defaults, $1k for five-digit, $250 for
  ACA/mortgage/severance, 1 for years/months/ages/services, 0.5% for nominal
  return and inflation. Dollar slider max = 3× default (severance 0–$25k);
  exact values can be typed above the slider max.
- **Charts:** Portfolio (stacked brokerage/TSP, total line, milestones, stress
  band, no-stress baseline, pinned overlays) and Retirement cash flow (pension,
  SS, severance, spending, portfolio-draw shading). Tabs.
- **Cards:** Key moments (click to jump to a table row), What moves the needle
  (age-95 impact of spending +$5k, return −1%, retire +2, layoff +1, stress
  add/remove; first-retirement withdrawal rate), Scenario compare, year-by-year
  table with All/Milestones/Shortfalls filters, Copy summary, CSV export.
- **Saved scenarios:** Save names the current plan; Saved opens a top-right
  popover with Load/Delete and Save current. Up to 12; duplicate names get
  `(2)`; Reset keeps saved plans.
- **Theme:** light/dark; print styles; responsive.

## Compound calculator (`compound.html`)

A second page, reached from the tab strip under the app bar; the retirement page
links back the same way. It is a JS port of `compound_calculator_v5.py` (Tkinter
+ matplotlib) and has its own three tabs:

- **Accumulation:** principal, nominal return, years, inflation, annual
  contribution → nominal value, today's dollars, interest earned, total
  contributed, buying-power lost, real return; growth chart and a year-by-year
  table.
- **Withdrawals:** starting balance, return, inflation, years, annual
  withdrawal, optional contribution, withdrawal growth above inflation →
  real/nominal balance chart, depletion year, total withdrawn.
- **Safe rate:** balance, return, inflation, years, target ending balance →
  exact sustainable rate, per year/month, a 2.0–7.0% comparison table
  (green = lasts, red = runs out), trajectory chart, and a "$X/month" checker.

Math is a 1:1 port (`future_value`, `real_value`, `real_return`,
`simulate_withdrawals`, `safe_withdrawal_rate`, `simulate_at_rate`), so results
match the Python app: 10,000 at 7% for 20 years = 38,696.84 nominal /
21,425.50 real; 500,000 drawing 30,000 real at 7%/3% depletes in year 28
(820,600.64 withdrawn); the exact rate for 500,000 over 30 years is 5.7015% =
28,507.42/yr.

Persistence is its own `localStorage` key `compound-calculator-v1` (tab, theme
and all inputs). On a first visit it borrows the retirement page's theme so the
two pages match; the theme toggle then updates only the compound page.

## Persistence

- Primary: URL fragment `#s=<base64 UTF-8 JSON>` containing current values
  (including `birthdate`), pinned scenarios, saved scenarios (`sv`), tab, filter,
  and theme.
- Mirror: `localStorage` key `retirement-dashboard-v2` when available.
- Saved scenarios store only non-default values (`compactValues`) to keep the
  hash shorter; up to 12.
- In some preview/opaque-origin environments `localStorage` is ephemeral per
  reload; the URL hash is the reliable store. In normal Chrome/HTTP use both work.

## Recent decisions/changes

1. Ported the Python engine to JS; verified defaults/stress/deferred against the
   original.
2. Rebuilt the UI: hero, charts, milestones, sensitivity, compare, table, dark
   mode.
3. Exposed life variables: payoff date, pension paths (VERA/MRA/deferred),
   service start/auto service years, Medicare household phase-in, new-job gap,
   monthly severance, new-job health coverage.
4. Converted all numeric inputs to sliders with editable value chips and wheel
   adjustment; made the rail static.
5. Added named saved scenarios and moved the saved list into the header popover.
6. Severance is now monthly × 1–12 months; table note and cash-flow chart show it.
7. Return/inflation ticks are 0.5%.
8. Published to GitHub Pages from a public repo; `.gitignore` keeps build
   artifacts out. Pushes to `main` redeploy the live site.
9. Brokerage and TSP starting balances ship **blank** with an `Enter amount`
   placeholder so the public page shows no personal figures; blank is stored as
   0 and both sliders keep a wide 0–$1M / 0–$800k range.
10. Added FEHB: an immediate annuity (VERA/MRA+30/normal) pays the household
    `fehb` premium from the pension start year instead of ACA, with Medicare
    added at 62/65. Deferred plans still use ACA. ACA/FEHB rows dim to show
    which one is in force.
11. Added the second app: a tab strip under the app bar switches between the
    retirement dashboard and a JS port of the compounding/withdrawal/SWR
    calculator. Separate pages (`index.html`, `compound.html`) sharing design
    tokens and theme; the Python original is untouched.
12. Deleted the old PyInstaller output (`build/`, `dist/`, ~22 MB) plus
    `retirement_gui.spec` and `build_exe.bat`. `retirement_gui.py` is kept as the
    reference implementation; it still runs from source.
13. Current age now comes from a **birth date** field (default 1987-08-14) read
    against the computer clock; the age slider was removed. The engine still uses
    whole years, and `current_age` is derived, never edited directly.
14. Audited the engine headless against the Python original and an independent
    ledger (57/57 years each, 8 scenarios). Fixed three defects found in that
    audit: a negative balance compounded like an asset and its debt was erased at
    retirement; table columns could miss the total by $1; and unfunded spending
    after 59½ was dropped without a record. Spare "unfunded" is now surfaced in
    the hero, a banner, the row note and the shortfalls filter.
15. Corrected the MRA+30 branch: regular FERS annuities get **no COLA before 62**,
    so an immediate pension is now frozen in nominal dollars until then (it had
    assumed COLA from day one). Added the **FERS Supplement** for MRA+30 —
    `ss_you × service/40` from retirement to 62, no COLA — shown on the cash-flow
    chart, tooltip, banner, hero hint and text summary. VERA was unaffected by
    that change (it already eroded to 62); the deferred and normal branches now
    share the same no-COLA-before-62 rule.
16. Made the supplement visible per year: each row's note now appends
    `(incl. supplement $X)`, and the cash-flow chart starts at the first year with
    pension or supplement income instead of the first fully-retired year. Salary
    is drawn as its own segment (and counted against spending) so those extra
    years don't read as portfolio draws.
17. Corrected the **VERA supplement**. 5 CFR 842.503(a)(3) makes early retirement
    eligible, but 842.503(b)(1) withholds payment until MRA — so a VERA taken at 49
    or 54 now pays `ss_you × service/40` from MRA to 62. Before this, only MRA+30
    was modeled and VERA got nothing. A VERA taken at or after MRA pays
    immediately; a 60+20 normal retirement before 62 also qualifies; deferred and
    MRA+10 get none.
18. MRA is now **derived from the birth date** (5 U.S.C. 842.202: 55–57 depending
    on birth year; 57 for 1970+) instead of an editable "MRA+30 age" slider. The
    row shows the value read-only, and the companion field is renamed "Service
    needed at MRA". A fractional MRA rounds to the nearest birthday in the annual
    model. This removes the ability to set an MRA that does not legally exist.

## Known assumptions / open items

- Ages are whole years inside the engine. The exact age (years, months, days) is
  display-only, and the first projection year is treated as a full year from
  today — no partial-year proration of contributions, spending, or returns.
- New-job health coverage is assumed to cover **both** of you (family coverage).
  If it is employee-only, or Medicare costs should continue while employer
  coverage is active, this needs refinement.
- No income taxes, RMDs, survivor scenario, long-term care, other assets/income,
  ACA subsidies, IRMAA, or medical inflation.
- Pension COLA is assumed full from age 62 (FERS COLA reductions when inflation
  is low are not modeled). No COLA is paid before 62.
- The **FERS supplement** (VERA and MRA+30) is modeled gross — `ss_you ×
  service/40` from `max(retirement, MRA)` to 62. The earnings test (reduction for
  wages above the annual exempt amount) and any non-civilian service rules are not
  applied. Post-separation wages are treated as zero, per 5 CFR 842.504(b)(2)(ii).
- Spouse age gap is fixed at 3 years older.
- SS claim ages are fixed at 62; no early/late benefit adjustment.
- Horizon is your age 95; no separate spouse horizon.
- TSP access is annual (effective age 60); the 59.5 event is a UI milestone.
- Age is derived from `birthdate`; change the birth date rather than looking for
  an age control.

## Verification notes

- Balances 350k/280k, age 39 (default birth date): min **$700,175**, real
  **3.8835%**, end at 95 **$4,198,936**.
- VERA 49/25: **$30,250** nominal → **$20,599** by 62, plus a **$11,498**/yr
  supplement from 57; end at 95 **$7,560,986** (was $7,338,075 with no supplement).
- VERA 54/30: **$36,300** nominal, supplement **$13,798**/yr from 57, end
  **$9,689,489**.
- MRA+30 57/33: **$39,930** nominal → **$34,444** by 62 after 5 years without
  COLA; FERS supplement **$15,178**/yr from 57 to 62. Rows 57–61 carry
  `(incl. supplement …)`; the cash-flow chart starts at 57 with salary shaded.
- Deferred 43/19: **$11,919** at 62.
- Engine audit (run headless from `index.html`): 57/57 years identical to
  `retirement_gui.py` with rules aligned (no FEHB, no new-job coverage,
  `aca == medicare`), and 57/57 identical to a ledger rewritten from these rules
  in 8 scenarios (default, VERA, MRA+30, gap+severance, blank+gap, stress,
  negative real return, overspend).
- Overspend probe (age 50, $1k balances, $150k spend): balances clamp at $0 and
  $5,252,063 is reported unfunded; no negative balances anywhere.
- Severance $5,016/mo × 12 with $60,192 spend: note shows
  `Spend $60,192 · Gtd Inc $0 · Severance $60,192 · Net need $0`; cash-flow
  portfolio draw $0.
- Saved scenarios persist across reload, load correctly, and delete; no console
  errors in the tested flows.
