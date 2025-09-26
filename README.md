Here’s a **GitHub-ready README.md** that covers **v0 → v0.5**, the gameplay loop, improvements by version, and a roadmap feel.
You can paste this directly into your repo as `README.md`.

---

````markdown
# Job Search Roguelike 🎮

A text-based roguelike where the dungeon is… the job market.  
Built in Python as a learning project — feedback welcome!

---

## 📥 Download & Run
Clone or download this repo, then run one of the version scripts with Python 3.9+:

```bash
python job_search_roguelike_v0.py
python job_search_roguelike_v01.py
python job_search_roguelike_v02.py
python job_search_roguelike_v03.py
python job_search_roguelike_v04.py
python job_search_roguelike_v05.py
````

Each version ends with **“Press ENTER to exit…”** to avoid terminal flicker.
Windows users can double-click the `.py` file if Python is associated.

---

## 🎯 Core Gameplay Loop

* Manage **Energy, Money, and Confidence** while job hunting.
* Choose weekly actions:

  * **Apply** → chance at callbacks/offers
  * **Network** → boosts connections
  * **Train** → build industry skills
  * **Rest** → restore energy
  * (from v0.5) **Self-Care** and **Interview Prep** add more control
* Survive random events: rejections, bills, surprise gigs, good news.
* Win by landing a **dream job** or through alternative career paths.
* Lose if **any core stat hits zero**.

---

## 🛠️ Version History

### v0 — The Bare Minimum (MVP)

* Core stats: Energy, Money, Confidence
* Actions: Apply, Network, Train, Rest
* Random events: rejections, bills, small wins
* Victory: land dream job
* Loss: run out of any stat
* **Fix:** added exit pause (`Press ENTER to exit…`)

👉 *Proof of concept — invite laughs & “too real” comments.*

---

### v0.1 — Identity & Replay

* Added **Age brackets**: Young, Mid, Late career
* Added **Industries** with skill tags & culture flavor
* Bills now **scale with age bracket**

👉 *Hook: “Which industry should I expand next?”*

---

### v0.2 — Flavor & Variety

* Recruiters now have **emotions** (cheery, rushed, skeptical)
* New weekly events: **surprise bills, temp gigs, good news**
* More flavorful text for interviews and outcomes

👉 *Hook: “What’s the worst real rejection email line you’ve seen?”*

---

### v0.3 — Balance & Challenge

* **Rent due every 6 weeks**
* **Unemployment benefit**: $200/week for up to 4 weeks
* **Resilience mechanic**: rejections sting less over time
* Tweaked **energy costs & gig scaling**

👉 *Hook: share 1,000-run stats like: “70% survive, 25% broke, 5% burnout — realistic?”*

---

### v0.4 — Multiple Paths to Victory

* Survival victory (last 26 weeks)
* Portfolio victory (secure 3+ contracts)
* Pivot victory (switch industries successfully)
* Consultant victory (network + skills + savings)

👉 *Hook: “What’s YOUR definition of career success? Should I add it as a win?”*

---

### v0.5 — Player Agency

* **Self-Care**: spend money to restore Energy + Confidence
* **Interview Prep**: spend money/energy for bonus to next interview
* **Networking upgrades**: chance for warm introductions (better callbacks)

👉 *Hook: “What’s the most underrated job search strategy IRL?”*

---

### v0.5.1e — Tone & UX Polish

* Mixed Humor+Empathy Pool: combined copy bank for events/rejections/tooltips to keep moments supportive *and* funny.
* Age Picker Trade-offs (rebalanced):

  * **Young:** lower weekly/rent costs.
  * **Mid:** balanced costs, **+1 random background skill**, **+1 Confidence**.
  * **Late:** slightly higher costs, **+2 background skills (spread)**, **+2 Confidence**, **+$100** starting savings.
* Low-Resource Warnings: pre-action alerts when Energy or Money is about to hit zero.
* “Streak Assist” rename: replaced the “pity system” label in UI/code with a neutral term (logic unchanged).

**Deletions / Removals**

* Removed the separate humor vs. empathy toggles (now a single mixed pool).
* Removed all “pity system” wording from UI/comments (now “Streak Assist”).

👉 Hook: “Should we let you toggle Gentle Mode, Dark Humor Mode, or keep the mixed pool?”

---

### v0.5.1e (Gentle Mode, Tuned, Title + Exitfix)

This build is a playable balance pass of the Job Search Roguelike designed to give unemployed players a more pleasant, cathartic run-through without removing the real-life sting of job hunting.

Key Features in this version:

Gentle Mode tuning: Win rates for all age brackets (Young, Mid, Late) calibrated to ~32–35% under random play, so every run feels survivable while still challenging.

Title screen restored: Memorable intro banner with creator credit and subtitle (Based on Real Life Horror Stories :)).

Safe exit wrapper: When packaged as an .exe, the window no longer vanishes instantly — it always pauses for ENTER before closing, whether you win, lose, or crash.

Balanced mechanics:

Rest now restores more energy and scales with age assists.

Weekly costs and unemployment benefits adjust by career stage.

Application success odds include small age-based bonuses.

Victory conditions: Multiple win paths (Dream Job, Portfolio contracts, Consultant). Loss occurs if Energy, Money, or Confidence run out.

Why this build matters:
This version is tuned to be empathetic yet funny, ensuring that unemployed players who just want a quick laugh or a hopeful escape can still succeed in a run without grinding through repeated frustration

---

## 🚧 Roadmap

Future ideas (based on feedback):

* Remote / hybrid / onsite job types
* Multi-stage interviews
* More industry-specific job types & starting goals
* Expanded random events (networking fails, burnout, side hustles)
* Polished UI or graphical version

---

## 💬 Feedback

* Leave a GitHub issue or comment on [itch.io page](https://jobseeker.itch.io/job-search-roguelike)
* Or reach me at: [richardglenn.delacruz1@gmail.com]

---

## ❤️ Support

This game is **free**. If you enjoy it and want to fuel further updates,
optional donations are enabled on itch.io.




💬 Feedback Welcome!
Built from real job search experiences. What resonates? What's missing?
Found a bug? Open an issue
Have an idea? Start a discussion
Want to contribute? Fork and submit a PR!

"Disturbingly accurate" - Beta Tester
"Harder than Dark Souls" - Unemployed Developer
