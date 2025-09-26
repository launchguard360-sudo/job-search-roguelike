def title_screen():
    print("\n" + "=" * 56)
    print(" Job Search Roguelike — v0.5.1e")
    print("=" * 56)
    print("Based on Real Life Horror Stories :)")
    print("Created by: Richard Glenn dela Cruz, PhD")
    try:
        input("\nPress ENTER to start your job search...")
    except EOFError:
        pass


#!/usr/bin/env python3
# Job Search Roguelike — v0.5.1e
# Additions in this build:
# • Humor+Empathy flavor pools combined for richer variety
# • Age bracket trade-offs displayed during selection
# • Resource warnings for low Energy & Money (including upcoming weekend bills/rent)
# • Keeps: 5-day workweek, monthly-ish rent, simplified win paths, hopeful tuning, UI polish, EOF safety

import random
import sys
from dataclasses import dataclass, field
from typing import Optional

# -----------------------------
# Tunables (balance knobs)
# -----------------------------
RENT_CYCLE_WEEKS = 4  # monthly-ish
UNEMPLOY_BENEFIT = 250
UNEMPLOY_WEEKS_MAX = 6




# --- Age balance knobs ---
AGE_BALANCE = {
    "Young": {"rest_bonus": 0, "rent_mult": 1.00, "unemp_mult": 1.00, "offer_bonus": 0.00},
    "Mid":   {"rest_bonus": 0, "rent_mult": 0.94, "unemp_mult": 1.20, "offer_bonus": 0.040},
    "Late":  {"rest_bonus": 2, "rent_mult": 0.80, "unemp_mult": 1.35, "offer_bonus": 0.065},
}

# Baseline bills by age bracket (per week) — Young cheaper, Late pricier
BILLS_BY_AGE = {
    "Young": 70,
    "Mid": 140,
    "Late": 210,
}

# Rent by age bracket (every RENT_CYCLE_WEEKS)
RENT_BY_AGE = {
    "Young": 560,
    "Mid": 900,
    "Late": 1250,
}

# Industries with skill tags & culture flavor
INDUSTRRIES = {  # (typo fixed below after definition to maintain compatibility if needed)
    "Tech": {
        "skills": {"coding", "product", "data"},
        "flavor": "fast-paced, ambiguous requirements, demos matter",
        "dream_job_title": "Senior Product Engineer (Dream)",
    },
    "Finance": {
        "skills": {"excel", "analysis", "risk"},
        "flavor": "formal, metrics-driven, crisp decks",
        "dream_job_title": "Quant Strategist (Dream)",
    },
    "Healthcare": {
        "skills": {"compliance", "patient", "ops"},
        "flavor": "process-heavy, outcomes & safety first",
        "dream_job_title": "Clinical Ops Lead (Dream)",
    },
    "Creative": {
        "skills": {"design", "portfolio", "story"},
        "flavor": "portfolio-forward, vibes & references",
        "dream_job_title": "Creative Director (Dream)",
    },
}
# fix name
INDUSTRIES = INDUSTRRIES

RECRUITER_EMOTIONS = [
    ("cheery", +0.07, "sounds genuinely excited to meet you"),
    ("rushed", -0.03, "is juggling back-to-back calls"),
    ("skeptical", -0.07, "keeps probing your gaps"),
    # Expanded for humor
    ("distracted", -0.05, "is clearly Slacking while you talk"),
    ("overly-friendly", -0.02, "keeps saying 'we're a family here' (yikes)"),
    ("glitchy-zoom", -0.04, "hears only every third word you say"),
]

# Action costs / effects
TRAIN_COST_ENERGY = 2
TRAIN_GAIN_SKILL = 1

NETWORK_COST_ENERGY = 2
NETWORK_WARM_INTRO_CHANCE = 0.40

REST_GAIN_ENERGY = 6

APPLY_COST_ENERGY = 2
INTERVIEW_PREP_TEMP_BOOST = 0.25
INTERVIEW_PREP_COST_MONEY = 60
INTERVIEW_PREP_COST_ENERGY = 2

SELF_CARE_COST_MONEY = 50
SELF_CARE_GAIN_ENERGY = 2
SELF_CARE_GAIN_CONF = 2

# Base success odds tuning (hopeful)
BASE_CALLBACK_ODDS = 0.24
BASE_OFFER_ODDS = 0.32
CONF_CALLBACK_SCALE = 0.006
CONF_OFFER_SCALE = 0.006
SKILL_MATCH_BONUS = 0.03

# Resilience tuning
RESILIENCE_GAIN_ON_REJECT = 0.8
REJECTION_CONFIDENCE_LOSS = 3
CONFIDENCE_FLOOR = 5

# Gig/Temp rewards
TEMP_GIG_MONEY_REWARD = (90, 180)
TEMP_GIG_ENERGY_COST = 2

# Small good news
SMALL_GOOD_NEWS_MONEY = (20, 80)
SMALL_GOOD_NEWS_CONF = (1, 3)

# Bills surprise
SURPRISE_BILL_RANGE = (40, 120)

# Portfolio contracts target
PORTFOLIO_TARGET = 3

# Dream job odds base/bonus
BASE_DREAM_ODDS = 0.05
DREAM_BONUS_STRONG = 0.12

# --- UI helpers (bold/color + action pause) ---
class Style:
    BOLD = "\033[1m"
    RESET = "\033[0m"

class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"

def say(msg: str, *, color: Optional[str] = None, bold: bool = False):
    start = ""
    if bold:
        start += Style.BOLD
    if color:
        start += color
    end = Style.RESET if start else ""
    print(f"{start}{msg}{end}")

def action_pause():
    try:
        input("\n(press ENTER to continue)")
    except EOFError:
        pass

# Optional: better Windows support for ANSI colors
if sys.platform.startswith("win"):
    try:
        import colorama  # pip install colorama (optional)
        getattr(colorama, 'just_fix_windows_console', getattr(colorama, 'init', lambda *a, **k: None))()
    except Exception:
        pass

# --- Flavor text pools (Empathy + Humor mixed) ---
AFTER_REST = [
    # empathy
    "Taking care today powers tomorrow.",
    "Rest is part of the plan, not a detour.",
    "You gave your mind some air — good call.",
    # humor
    "You doomscrolled job tips instead of applying. Energy +4, shame +0.",
    "You napped so hard your to‑do list filed a complaint.",
]

AFTER_TRAIN = [
    "Practice makes progress.",
    "Brick by brick — your skills are stacking.",
    "Tiny reps lead to big leaps.",
    "You watched a tutorial at 1.25x speed and felt like a wizard.",
    "You learned a new shortcut. It saves 0.3 seconds. Worth it.",
]

AFTER_NETWORK = [
    "Even small conversations keep you visible.",
    "You showed up — that matters.",
    "Connections compound over time.",
    "You commented 'Great insights!' on three posts. You are now a thought follower.",
    "You joined a Slack group and muted it immediately. Balanced.",
]

AFTER_SELFCARE = [
    "Self-care isn’t indulgence — it’s maintenance.",
    "You treated yourself like a teammate worth supporting.",
    "Your future self thanks you.",
    "$50 on coffee and a candle. Expensive? Yes. Worth it? Also yes.",
    "You did yoga guided by a raccoon on YouTube. Surprisingly centering.",
]

AFTER_PREP = [
    "Preparation turns nerves into signal.",
    "Clarity beats panic — nice prep.",
    "You’ll sound more like you on the call.",
    "You rehearsed answers to your plants. They gave good feedback.",
    "You practiced until your cat judged you. That’s how you know you’re ready.",
]

AFTER_REJECTION = [
    "This one stings. Fit says nothing about your worth.",
    "They passed — not because you lack value.",
    "Rejection is data, not identity.",
    "They said you’re 'overqualified' — which is recruiter for 'we’re confused.'",
    "They spelled your name wrong. Twice. You deserve better.",
]

AFTER_CALLBACK = [
    "Momentum! Keep your head up.",
    "Proof your signals are landing.",
    "The door cracked open — step through.",
    "Your forgotten application from 3 weeks ago just phoned home.",
    "Recruiter replied at 11:59 PM. Chaos energy recognized.",
]

AFTER_CONTRACT = [
    "Not the dream yet, but you kept your career moving.",
    "A step forward — your runway got longer.",
    "Stacking wins builds belief.",
    "Welcome to freelance: you get to pick your hours (all of them).",
    "They want 'quick deliverables' and 'robust architecture'. Sure, why not both.",
]

AFTER_WEEK_WRAP = [
    "You bought yourself another week of focus.",
    "You kept the lights on and the hope warm.",
    "Every week finished is progress banked.",
    "Bills paid. Anxiety reduced by 7%. Scientific.",
    "Your spreadsheet says 'survivor'. Your heart says 'try again'.",
]

SURPRISE_BILL_LINES = [
    "Event: Surprise bill — apparently parking meters don’t accept exposure bucks.",
    "Event: A mysterious 'service fee' appeared. Service unclear, fee very clear.",
]

TEMP_GIG_LINES = [
    "You did a gig moving office chairs. Confidence unchanged, core strengthened.",
    "Food delivery sprint: tips were mid, podcast was excellent.",
    "Tutored algebra and remembered how mean letters can be.",
]

SMALL_GOOD_NEWS_LINES = [
    "Someone liked your LinkedIn post. (It was your mom, but still.)",
    "Old coworker sent an encouraging DM. Your day brightened 12%.",
    "A stranger on the bus said 'you got this'. Statistically significant uplift.",
]

@dataclass
class Player:
    name: str
    age_bracket: str
    start_industry: str
    target_industry: str  # kept for compatibility; always == start_industry
    week: int = 1
    day: int = 1  # 1-5 workdays
    energy: int = 10
    money: int = 400
    confidence: int = 10
    resilience: float = 0.0
    unemployed_weeks_paid: int = 0
    contracts: int = 0
    interview_prep_active: bool = False
    warm_intro: bool = False
    skills: dict = field(default_factory=lambda: {k: 0 for k in {"coding","product","data","excel","analysis","risk","compliance","patient","ops","design","portfolio","story"}})
    game_over: bool = False
    win_reason: Optional[str] = None
    loss_reason: Optional[str] = None
    consecutive_rejections: int = 0
    mentor_boost: bool = False

    def any_stat_empty(self) -> bool:
        return self.energy <= 0 or self.money <= 0 or self.confidence <= 0

    def industry_skill_match(self, industry: str) -> int:
        tags = INDUSTRIES[industry]["skills"]
        return sum(self.skills.get(tag, 0) > 0 for tag in tags)

    def status_line(self) -> str:
        return (f"Week {self.week} Day {self.day}/5 | Energy {self.energy} | Money ${self.money} | "
                f"Confidence {self.confidence} | Resilience {self.resilience:.1f} | "
                f"Contracts {self.contracts}")

def clamp(v, lo, hi): return max(lo, min(hi, v))

def press_any_key_to_exit():
    try:
        input("\nPress ENTER to exit…")
    except EOFError:
        pass

def choose(prompt, options):
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            s = input("> ").strip()
        except EOFError:
            return 0
        if s.isdigit() and 1 <= int(s) <= len(options):
            return int(s) - 1
        print("Pick a number from the list.")

def intro(seed: Optional[int] = None) -> Player:
    say("=== Job Search Roguelike — v0.5.1e ===", bold=True)
    print("One action per weekday. Weekends auto-wrap bills & events.\n")
    if seed is None:
        try:
            seed_in = input("Optional: enter a seed for reproducibility (or press ENTER): ").strip()
            seed = int(seed_in) if seed_in else None
        except (ValueError, EOFError):
            seed = None
    if seed is not None:
        random.seed(seed)
        print(f"(Using seed {seed})\n")

    try:
        name = input("Your name: ").strip() or "Player"
    except EOFError:
        name = "Player"

    # Age bracket selection with visible trade-offs
    print("Age brackets (with trade-offs):")
    print("  1. Young  — lower weekly/rent costs.")
    print("  2. Mid    — balanced costs, +1 random background skill, +1 confidence.")
    print("  3. Late   — slightly higher costs, +2 background skills spread, +2 confidence, +$100 savings.")
    age_map = ["Young", "Mid", "Late"]
    age_idx = choose("Choose your age bracket:", age_map)
    age = age_map[age_idx]

    ind_names = list(INDUSTRIES.keys())
    start_idx = choose("Pick your current industry:", ind_names)
    start_ind = ind_names[start_idx]
    target_ind = start_ind  # target == start, by design

    # Create player
    p = Player(name=name, age_bracket=age, start_industry=start_ind, target_industry=target_ind)

    # Age bracket trade-offs
    for tag in INDUSTRIES[start_ind]["skills"]:
        p.skills[tag] = p.skills.get(tag, 0) + 1

    if age == "Mid":
        extra = random.choice(list(INDUSTRIES[start_ind]["skills"]))
        p.skills[extra] += 1
        p.confidence += 1
    elif age == "Late":
        tags = list(INDUSTRIES[start_ind]["skills"])
        random.shuffle(tags)
        for t in tags[:2]:
            p.skills[t] += 1
        p.confidence += 2
        p.money += 100

    print("\nFlavor:", INDUSTRIES[target_ind]["flavor"])
    say(f"\nStarting stats → {p.status_line()}", color=Color.CYAN, bold=True)
    print("Win paths:")
    print(" • Dream Job offer in your industry")
    print(f" • Sustainable Freelance Career: secure {PORTFOLIO_TARGET}+ contracts")
    print(" • Consultant: strong network, skills, and savings\n")
    return p

def weekly_costs(player: Player):
    m = AGE_BALANCE[player.age_bracket]["rent_mult"]
    bills = int(BILLS_BY_AGE[player.age_bracket] * m)
    player.money -= bills
    say(f"Weekly bills: -${bills}", color=Color.YELLOW, bold=True)

    if player.week % RENT_CYCLE_WEEKS == 0:
        rent = int(RENT_BY_AGE[player.age_bracket] * m)
        player.money -= rent
        say(f"Rent due (week {player.week}): -${rent}", color=Color.RED, bold=True)

    if player.unemployed_weeks_paid < UNEMPLOY_WEEKS_MAX:
        um = AGE_BALANCE[player.age_bracket]["unemp_mult"]
        benefit = int(UNEMPLOY_BENEFIT * um)
        player.money += benefit
        player.unemployed_weeks_paid += 1
        say(f"Unemployment benefit: +${benefit} (week {player.unemployed_weeks_paid}/{UNEMPLOY_WEEKS_MAX})", color=Color.GREEN, bold=True)

def random_weekly_event(player: Player):
    roll = random.random()
    if roll < 0.15:
        amt = random.randint(*SURPRISE_BILL_RANGE)
        player.money -= amt
        line = random.choice(SURPRISE_BILL_LINES)
        say(f"{line} -${amt}", color=Color.RED, bold=True)
    elif roll < 0.50:
        pay = random.randint(*TEMP_GIG_MONEY_REWARD)
        player.money += pay
        player.energy = max(0, player.energy - TEMP_GIG_ENERGY_COST)
        base = f"Event: Temp gig → +${pay}, Energy -{TEMP_GIG_ENERGY_COST}"
        if random.random() < 0.25:
            player.confidence += 1
            base += ", Confidence +1"
        say(base, color=Color.CYAN, bold=True)
        print(random.choice(TEMP_GIG_LINES))
    else:
        m = random.randint(*SMALL_GOOD_NEWS_MONEY)
        c = random.randint(*SMALL_GOOD_NEWS_CONF)
        player.money += m
        player.confidence += c
        say(f"Event: Small good news → +${m} money, +{c} confidence", color=Color.GREEN, bold=True)
        print(random.choice(SMALL_GOOD_NEWS_LINES))

def warn_resources(player: Player, *, upcoming_wrap: bool = False):
    """Warn when resources are low or about to dip below zero on weekend wrap."""
    # Energy warning
    if player.energy <= 2:
        say("Warning: Low Energy. Consider Rest or Self‑Care.", color=Color.YELLOW, bold=True)
    # Money warning immediate
    if player.money <= 100:
        say("Warning: Low Money. Consider a Temp Gig week or lighter spending.", color=Color.YELLOW, bold=True)
    # Predict weekend bills/rent if wrap incoming
    if upcoming_wrap:
        projected = player.money - BILLS_BY_AGE[player.age_bracket]
        rent_due = (player.week % RENT_CYCLE_WEEKS == 0)
        if rent_due:
            projected -= RENT_BY_AGE[player.age_bracket]
        if projected <= 0:
            msg = "Warning: Upcoming bills "
            msg += "+ rent " if rent_due else ""
            msg += "may push Money below $0 this weekend."
            say(msg, color=Color.YELLOW, bold=True)

def act_rest(player: Player):
    gain = REST_GAIN_ENERGY + AGE_BALANCE[player.age_bracket]["rest_bonus"]
    before = player.energy
    player.energy = min(12, player.energy + gain)
    actual = player.energy - before
    player.confidence = clamp(player.confidence + 1, 0, 99)
    say(f"You rest. Energy +{actual}, Confidence +1", color=Color.GREEN, bold=True)
    print(random.choice(AFTER_REST))

def act_train(player: Player):
    if player.energy < TRAIN_COST_ENERGY:
        say("Too tired to train.", color=Color.RED, bold=True)
        return
    player.energy -= TRAIN_COST_ENERGY
    tag = random.choice(list(INDUSTRIES[player.target_industry]["skills"]))
    player.skills[tag] = player.skills.get(tag, 0) + TRAIN_GAIN_SKILL
    player.confidence += 1
    say(f"You train {tag}. Skill +{TRAIN_GAIN_SKILL}, Confidence +1, Energy -{TRAIN_COST_ENERGY}", color=Color.CYAN, bold=True)
    print(random.choice(AFTER_TRAIN))

def act_network(player: Player):
    if player.energy < NETWORK_COST_ENERGY:
        say("Too tired to network.", color=Color.RED, bold=True)
        return
    player.energy -= NETWORK_COST_ENERGY
    player.confidence += 1
    if random.random() < NETWORK_WARM_INTRO_CHANCE:
        player.warm_intro = True
        say("You networked into a WARM INTRO for next Apply!", color=Color.GREEN, bold=True)
    else:
        say("You networked. Confidence +1, Energy -2", color=Color.CYAN, bold=True)
    print(random.choice(AFTER_NETWORK))

def act_selfcare(player: Player):
    if player.money < SELF_CARE_COST_MONEY:
        say("Not enough money for self-care.", color=Color.RED, bold=True)
        return
    post = player.money - SELF_CARE_COST_MONEY
    if post <= 0:
        say("Heads up: Self‑Care would drop Money to $0. Proceed mindfully.", color=Color.YELLOW, bold=True)
    player.money -= SELF_CARE_COST_MONEY
    player.energy += SELF_CARE_GAIN_ENERGY
    player.confidence += SELF_CARE_GAIN_CONF
    say(f"Self-care day: -${SELF_CARE_COST_MONEY}, Energy +{SELF_CARE_GAIN_ENERGY}, Confidence +{SELF_CARE_GAIN_CONF}", color=Color.GREEN, bold=True)
    print(random.choice(AFTER_SELFCARE))

def act_interview_prep(player: Player):
    if player.money < INTERVIEW_PREP_COST_MONEY or player.energy < INTERVIEW_PREP_COST_ENERGY:
        say("You lack money or energy for interview prep.", color=Color.RED, bold=True)
        return
    post = player.money - INTERVIEW_PREP_COST_MONEY
    if post <= 0:
        say("Heads up: Interview Prep would drop Money to $0. Proceed mindfully.", color=Color.YELLOW, bold=True)
    player.money -= INTERVIEW_PREP_COST_MONEY
    player.energy -= INTERVIEW_PREP_COST_ENERGY
    player.interview_prep_active = True
    say(f"You prepare for interviews: -${INTERVIEW_PREP_COST_MONEY}, Energy -{INTERVIEW_PREP_COST_ENERGY}, next interview gets +{int(INTERVIEW_PREP_TEMP_BOOST*100)}%", color=Color.CYAN, bold=True)
    print(random.choice(AFTER_PREP))

def rejection_hit(player: Player):
    loss = max(1, int(REJECTION_CONFIDENCE_LOSS - player.resilience))
    player.confidence = max(CONFIDENCE_FLOOR, player.confidence - loss)
    player.resilience += RESILIENCE_GAIN_ON_REJECT
    player.consecutive_rejections += 1
    if random.random() < 0.25:
        player.mentor_boost = True
        say("A mentor reviewed your résumé. Next Apply gets a quiet boost.", color=Color.GREEN, bold=True)
    say(f"Rejection. Confidence -{loss}. Your resilience grows (+{RESILIENCE_GAIN_ON_REJECT}).", color=Color.YELLOW, bold=True)
    print(random.choice(AFTER_REJECTION))

def offer_received(player: Player, job_title: str, industry: str, dream: bool=False):
    if dream:
        player.win_reason = f"Landed Dream Job: {job_title} in {industry}"
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("Well done. You turned persistence into opportunity.")
        return
    player.contracts += 1
    gain = random.randint(200, 500)
    player.money += gain
    player.confidence += 2
    say(f"Offer! You secured a short contract in {industry}: +${gain}, Contracts {player.contracts}", color=Color.GREEN, bold=True)
    print(random.choice(AFTER_CONTRACT))

def apply_flow(player: Player):
    if player.energy < APPLY_COST_ENERGY:
        say("Too tired to apply.", color=Color.RED, bold=True)
        return

    player.energy -= APPLY_COST_ENERGY
    emotion, mod, flavor = random.choice(RECRUITER_EMOTIONS)
    say(f"You apply to a {player.target_industry} role.", bold=True)
    print(f"Recruiter is {emotion} — {flavor}.")

    match_count = player.industry_skill_match(player.target_industry)
    warm = 0.15 if player.warm_intro else 0.0
    prep = INTERVIEW_PREP_TEMP_BOOST if player.interview_prep_active else 0.0
    pity = 0.10 if player.consecutive_rejections >= 3 else 0.0
    mentor = 0.07 if player.mentor_boost else 0.0
    callback_odds = clamp(
        BASE_CALLBACK_ODDS
        + player.confidence * CONF_CALLBACK_SCALE
        + match_count * SKILL_MATCH_BONUS
        + warm + mentor + pity
        + mod * 0.5,
        0.01, 0.90
    )

    player.warm_intro = False
    player.interview_prep_active = False
    player.mentor_boost = False

    if random.random() < callback_odds:
        say("Callback! You got an interview.", color=Color.GREEN, bold=True)
        player.consecutive_rejections = 0
        offer_odds = clamp(
            BASE_OFFER_ODDS
            + player.confidence * CONF_OFFER_SCALE
            + match_count * SKILL_MATCH_BONUS
            + prep
            + mod,
            0.02, 0.85
        )
        dream_bonus = DREAM_BONUS_STRONG if (match_count >= 2 and player.confidence >= 14) else 0.0
        dream_odds = clamp(BASE_DREAM_ODDS + dream_bonus, 0.0, 0.35)
        r = random.random()
        if r < dream_odds:
            title = INDUSTRIES[player.target_industry]["dream_job_title"]
            offer_received(player, title, player.target_industry, dream=True)
        elif r < dream_odds + offer_odds:
            offer_received(player, "Contract Offer", player.target_industry, dream=False)
        else:
            rejection_hit(player)
        print(random.choice(AFTER_CALLBACK))
    else:
        rejection_hit(player)

def check_victory_conditions(player: Player):
    if player.game_over:
        return
    # Sustainable Freelance Career
    if player.contracts >= PORTFOLIO_TARGET:
        player.win_reason = f"Sustainable Freelance Career: {player.contracts} contracts."
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("Your freelance projects added up to a steady path.")
        return
    # Consultant victory: network + skills + savings
    trained_tags = sum(1 for v in player.skills.values() if v >= 2)
    if player.confidence >= 16 and trained_tags >= 4 and player.money >= 1500:
        player.win_reason = "Consultant Victory: strong skills, network, and runway."
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("You built enough stability to choose your clients and pace.")

def check_loss(player: Player):
    if player.any_stat_empty():
        player.loss_reason = "You ran out of a core resource (Energy, Money, or Confidence)."
        player.game_over = True
        say(f"✖ This chapter ends. {player.loss_reason}", color=Color.RED, bold=True)
        print("Running out doesn’t erase what you built. Carry it into the next run.")

def show_actions(player: Player):
    print("\nActions (1 per day):")
    print("  1) Apply (Energy -2)  — Try for callbacks/offers")
    print("  2) Network (Energy -2) — Chance for warm intro next Apply")
    print("  3) Train (Energy -2)   — Improve a skill in your industry, +Confidence")
    print("  4) Rest                — Recover Energy, small Confidence")
    print("  5) Self-Care ($50)     — +Energy +Confidence")
    print("  6) Interview Prep ($60, Energy -2) — Big boost to next interview")
    # Resource warnings near the menu
    upcoming_wrap = (player.day == 5)  # weekend next
    warn_resources(player, upcoming_wrap=upcoming_wrap)

def weekend_wrap(player: Player):
    say("\n— Weekend wrap —", color=Color.CYAN, bold=True)
    weekly_costs(player)
    random_weekly_event(player)
    player.week += 1
    player.day = 1
    print(random.choice(AFTER_WEEK_WRAP))
    # Post-wrap warnings
    warn_resources(player, upcoming_wrap=False)

def game_loop(player: Player):
    while not player.game_over:
        say("\n" + "=" * 48, color=Color.CYAN, bold=True)
        print(player.status_line())
        show_actions(player)
        try:
            choice = input("> ").strip()
        except EOFError:
            break

        did_action = False

        if choice == "1":
            apply_flow(player); did_action = True
        elif choice == "2":
            act_network(player); did_action = True
        elif choice == "3":
            act_train(player); did_action = True
        elif choice == "4":
            act_rest(player); did_action = True
        elif choice == "5":
            act_selfcare(player); did_action = True
        elif choice == "6":
            act_interview_prep(player); did_action = True
        else:
            say("Pick 1–6.", color=Color.YELLOW, bold=True)

        check_loss(player)
        if not player.game_over:
            check_victory_conditions(player)

        if not player.game_over and did_action:
            action_pause()
            player.day += 1
            if player.day > 5:
                weekend_wrap(player)

    # Exit screen and option to restart
    say("\n=== Run Summary ===", bold=True)
    print(player.status_line())
    if player.win_reason:
        print("Result:", player.win_reason)
        print("This journey wasn’t easy — you faced uncertainty and kept going. Well done.")
    elif player.loss_reason:
        print("Result:", player.loss_reason)
        print("You applied, learned, and built resilience. You’re not starting from zero next time.")

def start_game():
    title_screen()
    while True:
        try:
            p = intro()
            game_loop(p)
            ans = input("\nStart a new run? (y/n): ").strip().lower()
        except EOFError:
            ans = "n"
        if ans != "y":
            break
    press_any_key_to_exit()

def main():
    try:
        start_game()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        press_any_key_to_exit()

if __name__ == "__main__":
    main()


def _safe_exit(message="\nPress ENTER to exit..."):
    try:
        input(message)
    except Exception:
        pass

def _run_main():
    try:
        main()
    except Exception:
        print("\n[Unhandled Error] The game encountered an unexpected error:")
        _traceback.print_exc()
        _safe_exit("\nPress ENTER to close...")
    else:
        _safe_exit("\nThanks for playing! Press ENTER to close...")

if __name__ == "__main__":
    _run_main()
