# Retirement Flexibility Calculator — Web Dashboard

A browser dashboard built from `retirement_gui.py`. The core balance engine is a
faithful port, and the assumptions that used to be hard-coded are now editable:
pension eligibility paths, service start, mortgage payoff date, the Medicare
phase-in, and a new-job gap/severance.

## Live version

<https://elninost0rm.github.io/retirement-dashboard/>

Published from the [retirement-dashboard](https://github.com/elninost0rm/retirement-dashboard)
repository with GitHub Pages. Every push to `main` redeploys it within a minute.

## Two calculators

The site has two apps, switched with the tab strip under the header:

- **Retirement plan** (`index.html`) — the federal pension / TSP / Social Security
  projection described below.
- **Compounding & withdrawals** (`compound.html`) — a standalone compounding
  calculator ported from `compound_calculator_v5.py`, with three tabs of its own:
  Accumulation (lump sum plus contributions, nominal and real), Withdrawals
  (draw-down with depletion detection) and Safe rate (maximum sustainable
  withdrawal rate, plus a "$X a month — is that safe?" check).

Both share the same design tokens and light/dark theme, and each remembers its
own inputs in the browser.

## Run it

**Option A — just open it**

Double-click `index.html`. Everything runs locally in the page; no installs.

**Option B — local server (recommended)**

Double-click `start_dashboard.bat`, or run:

```
python serve.py
```

It serves the dashboard at <http://127.0.0.1:8420/> and opens your browser.
Press `Ctrl+C` in the terminal to stop it. Standard library only.

Flags: `python serve.py --port 9000`, `python serve.py --no-browser`.

## What's in the dashboard

- **Hero summary** — minimum portfolio, balance at 95, funded-through age,
  real return, and the brokerage low point before 59½, with a portfolio sparkline.
- **Birth date** — your age is derived from the computer clock, so there is no
  age slider: the field shows the exact age (years, months, days) and the
  projection uses whole years. The birth date is saved with the scenario.
- **Live inputs** — every field and slider recalculates immediately. Ages stay
  in a valid order while you drag, and invalid numbers are flagged inline.
- **Blank starting balances** — Brokerage start and TSP start load empty with a
  greyed-out `Enter amount` prompt, so the published page shows nobody's real
  figures. Type a number (or drag the slider) and the projection updates.
- **Pension eligibility** — service start year (years are calculated
  automatically), VERA year/age/service, MRA+30 age/service, and the normal
  pension age.
- **Sliders everywhere** — every dollar, year, age, service, and month field is
  a slider with an editable value chip. Dollar ticks are $10k for six-digit
  defaults, $1k for five-digit defaults, and $250 for the four-digit fields
  (ACA, mortgage saving, severance). Nominal return and inflation use 0.5%
  ticks. Slider maximums are 3× the default; hover a slider and scroll to nudge
  it, Shift+scroll for 10×.
- **Layoff bridge** — a new-job gap in months, monthly severance for 1–12 months,
  and a toggle for whether the new job offers health insurance.
- **Retiree health** — a "Keep FEHB in retirement" toggle plus a household FEHB
  premium. With an immediate annuity the FEHB cost applies from retirement and
  the ACA premium is dimmed and ignored; a deferred annuity can't keep FEHB, so
  ACA applies and the hint line says why.
- **Mortgage payoff** — payoff year and month, with the spending reduction
  prorated across the payoff year.
- **Portfolio chart** — stacked brokerage/TSP areas, a total line, milestone
  markers, the stress window, and hover details. With the stress test on, the
  no-stress path is overlaid as a dashed comparison line.
- **Cash-flow chart** — income (pension, Social Security, the FERS supplement for
  MRA+30 plans, and salary while either of you still works) against spending from
  the pension start onward, with the portfolio draw shaded.
- **Key moments** — every milestone (layoff, pension start, retirement, SS, TSP
  access, Medicare, mortgage payoff) with the portfolio value at that age. Click
  one to jump to the year in the table.
- **What moves the needle** — the impact on the age-95 balance of spending
  $5k more, a 1% lower return, retiring two years later, delaying the layoff a
  year, or adding/removing the stress test.
- **Scenario compare** — pin up to four scenarios; they appear as extra lines
  on the chart and side by side in the compare table.
- **Saved scenarios** — save the current plan under a name, load it later, or
  delete it. Up to 12 plans are kept with the dashboard state.
- **Table filters** — all years, milestones only, or shortfalls only (unfunded
  years count as shortfalls).
- **Dark mode**, copyable text summary, CSV export, and print-friendly styles.

## Saving and sharing

The current scenario and your saved scenarios are encoded in the URL fragment
(`#s=…`), so:

- Reloading restores your inputs, pinned scenarios, saved library, chart tab,
  filter, and theme.
- Copying the URL shares the exact scenario and saved plans.
- When served over HTTP, it is also mirrored to `localStorage`.

Use **Save** in the header to name the current plan; click **Saved** next to it to
open the saved list, where you can Load or Delete. Use **Reset** in the header to
return every input to its default — saved plans are kept.

## Accuracy

The core balance math matches the original engine. With $350,000 brokerage and
$280,000 TSP entered, the plan bottoms out at **$700,175 at age 39** with a
**3.8835% real return**, ending at **$4,198,936** at 95. The age-95 balance is
lower than the old Tkinter app because the dashboard now phases in the spouse's
Medicare cost at your age 62 and halves the household ACA cost for the one person
still on it.

The two starting balances are blank by default, so a fresh page shows an
unfunded plan starting from $0 until you enter your own figures.

The new pension paths were checked against hand calculations:

- **VERA at 49** with 25 years: $30,250 nominal, eroding to $20,599 by 62.
- **MRA+30 at 57** with 33 years: $39,930 nominal, eroding to $34,444 by 62,
  plus a FERS supplement of $15,178/yr until 62.
- **Deferred at 43** with 19 years: $11,919 at 62.

The engine was then audited outside the browser and compared year by year against
two independent implementations. All 57 projection years matched the original
Python model to the dollar once the rules were aligned, and all 57 matched a
second implementation written from the documented rules across the default, VERA,
MRA+30, gap/severance, blank-balance, stress, negative-return and overspend
scenarios.

Balances never go negative. If a year's spending exceeds what the balances can
cover, they stop at $0 and the remainder is reported as **unfunded** — in the
hero, a banner, the year's note, and the shortfalls filter — rather than being
silently absorbed.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole dashboard (HTML + CSS + JS, no dependencies). |
| `compound.html` | Compounding / withdrawal / safe-rate calculator, same design, own tabs. |
| `serve.py` | Optional local server that opens the dashboard in your browser. |
| `start_dashboard.bat` | Windows launcher for `serve.py`. |
| `retirement_gui.py` | Original Tkinter desktop app, unchanged. |

## Model assumptions

- All figures are in today's dollars; balances grow at
  `(1 + nominal return) / (1 + inflation) − 1`.
- **Service years** are calculated from the federal service start year at the
  layoff age. The pension multiplier is 1.0% per year, 1.1% at 20+ years.
- **Pension paths:**
  - **VERA:** only when the layoff year equals the VERA year, the layoff age
    equals the VERA age, and service meets the minimum. Starts at the VERA age;
    the full nominal amount erodes with inflation until 62, then gets COLA.
  - **MRA+30:** when the layoff age is at least the MRA age and service meets the
    minimum. Starts at the layoff age; nominal until COLA begins at 62. Also pays
    the **FERS Supplement** (about SS × service/40) from retirement to 62.
  - **Normal:** at or after the normal pension age with at least 5 years. Starts
    at the layoff age; COLA applies from 62.
  - **Deferred:** everything else. Starts at the normal pension age, with the
    nominal amount eroded from the leave year to that age.
- The spouse is modeled as 3 years older; spouse Social Security starts at your
  age 59, yours at 62.
- The FERS supplement (MRA+30 plans) is modeled gross, before the earnings test;
  it ends at 62 and has no COLA.
- **Health costs:** zero while anyone is working. Retiring on an **immediate**
  annuity (VERA, MRA+30, or normal) keeps **FEHB**: the household FEHB premium is
  paid from the retirement year for life, with Medicare added as each of you turns
  65. On a **deferred** annuity FEHB is not available, and with the toggle off you
  use **ACA** instead. ACA is a household amount, halved when only one of you is
  on it; Medicare is a household amount, half for one person from your age 62
  (when your spouse turns 65), full from your 65. When FEHB continues, enter only
  Medicare Part B in the Medicare field.
- Withdrawals come from brokerage first, then TSP once you reach 59½.
- The mortgage payoff year and month are inputs. The month is the last month
  with a payment, so June means six months of mortgage spending and six months of
  savings in that year.
- The new job starts after the gap and runs until your retirement age. Severance
  is a **monthly net amount for 1–12 months**, paid from the layoff onward. The
  year-by-year net need is shown after severance, and the cash-flow chart stacks
  severance as a gold income segment. If **New job offers health insurance** is
  on (the default), both of you are treated as covered while you work there, so
  ACA costs pause until the new job ends. The gap year itself still pays ACA.
- Projection runs from your current age through 95.

**Note:** the default current age is 38. Set it to **39** to align the default
VERA year (2036) with age 49.
