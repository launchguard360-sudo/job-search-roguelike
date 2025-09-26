#!/usr/bin/env python3
# Job Search Roguelike — v0.5.1 (Hopeful Tuning + Readability)
# Changelog vs v0.5:
# - UI: Bold/color emphasis on high-signal lines; pause after actions for readability.
# - Balance: Higher callback/offer odds, stronger warm intros & interview prep, reduced rejection sting.
# - Economy: Slightly stronger unemployment benefits (longer duration).
# - RNG: Weekly events tilted toward positive outcomes.
# - Empathy: Motivational messages; loss framed as "chapter end"; end summary highlights progress.
# - Fairness: Pity meter breaks cold streaks; mentor boost after rejection; confidence floor.
#
# Notes:
# - Windows terminals may need 'colorama' for ANSI color support (optional).
# - Structure and victories otherwise preserved from v0.5 for compatibility.

import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# -----------------------------
# Tunables (balance knobs)
# -----------------------------
WEEKS_TO_SURVIVE = 26
RENT_CYCLE_WEEKS = 6  # kept for v0.5.1 compatibility; consider 4 in v0.6
UNEMPLOY_BENEFIT = 250       # 200 -> 250
UNEMPLOY_WEEKS_MAX = 6       # 4 -> 6

# Baseline bills by age bracket (per week)
BILLS_BY_AGE = {
    "Young": 80,
    "Mid": 140,
    "Late": 200,
}

# Rent by age bracket (every RENT_CYCLE_WEEKS)
RENT_BY_AGE = {
    "Young": 600,
    "Mid": 900,
    "Late": 1200,
}

# Industries with skill tags & culture flavor
INDUSTRIES = {
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

RECRUITER_EMOTIONS = [
    ("cheery", +0.07, "sounds genuinely excited to meet you"),
    ("rushed", -0.03, "is juggling back-to-back calls"),
    ("skeptical", -0.07, "keeps probing your gaps"),
]

# Action costs / effects
TRAIN_COST_ENERGY = 2
TRAIN_GAIN_SKILL = 1

NETWORK_COST_ENERGY = 2
NETWORK_WARM_INTRO_CHANCE = 0.40  # 0.25 -> 0.40 (v0.5.1)

REST_GAIN_ENERGY = 4

APPLY_COST_ENERGY = 2
INTERVIEW_PREP_TEMP_BOOST = 0.25  # 0.15 -> 0.25 (v0.5.1)
INTERVIEW_PREP_COST_MONEY = 60
INTERVIEW_PREP_COST_ENERGY = 2

SELF_CARE_COST_MONEY = 50
SELF_CARE_GAIN_ENERGY = 2
SELF_CARE_GAIN_CONF = 2

# Base success odds tuning
BASE_CALLBACK_ODDS = 0.24   # 0.18 -> 0.24
BASE_OFFER_ODDS = 0.28      # 0.22 -> 0.28

# Confidence contribution scaling to callbacks/offers
CONF_CALLBACK_SCALE = 0.006 # 0.004 -> 0.006
CONF_OFFER_SCALE = 0.006    # 0.004 -> 0.006

# Skill contribution (matching industry skills)
SKILL_MATCH_BONUS = 0.03    # 0.02 -> 0.03 per matching tag count

# Resilience tuning (rejections sting less over time)
RESILIENCE_GAIN_ON_REJECT = 0.8  # 0.5 -> 0.8
REJECTION_CONFIDENCE_LOSS = 3    # 4 -> 3 (reduced sting)
CONFIDENCE_FLOOR = 5             # new: never drop below this

# Gig/Temp rewards
TEMP_GIG_MONEY_REWARD = (90, 180)    # (60, 140) -> (90, 180)
TEMP_GIG_ENERGY_COST = 2

# Small good news
SMALL_GOOD_NEWS_MONEY = (20, 80)
SMALL_GOOD_NEWS_CONF = (1, 3)

# Bills surprise
SURPRISE_BILL_RANGE = (40, 120)

# Portfolio contracts target
PORTFOLIO_TARGET = 3

# Dream job odds base/bonus (gentle lift)
BASE_DREAM_ODDS = 0.05     # base 0.03 -> 0.05
DREAM_BONUS_STRONG = 0.12  # bonus 0.08 -> 0.12

# --- UI helpers (bold/color + action pause) ---
class Style:
    BOLD = "\\033[1m"
    RESET = "\\033[0m"

class Color:
    GREEN = "\\033[92m"
    RED = "\\033[91m"
    YELLOW = "\\033[93m"
    CYAN = "\\033[96m"

def say(msg: str, *, color: str | None = None, bold: bool = False):
    start = ""
    if bold:
        start += Style.BOLD
    if color:
        start += color
    end = Style.RESET if start else ""
    print(f"{start}{msg}{end}")

def action_pause():
    try:
        input("\\n(press ENTER to continue)")
    except EOFError:
        pass

# Optional: better Windows support for ANSI colors
if sys.platform.startswith("win"):
    try:
        import colorama  # pip install colorama (optional)
        colorama.just_fix_windows_console()
    except Exception:
        pass

@dataclass
class Player:
    name: str
    age_bracket: str
    start_industry: str
    target_industry: str
    week: int = 1
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
    # v0.5.1 hopeful fairness
    consecutive_rejections: int = 0
    mentor_boost: bool = False

    def any_stat_empty(self) -> bool:
        return self.energy <= 0 or self.money <= 0 or self.confidence <= 0

    def industry_skill_match(self, industry: str) -> int:
        tags = INDUSTRIES[industry]["skills"]
        return sum(self.skills.get(tag, 0) > 0 for tag in tags)

    def status_line(self) -> str:
        return (f"Week {self.week} | Energy {self.energy} | Money ${self.money} | "
                f"Confidence {self.confidence} | Resilience {self.resilience:.1f} | "
                f"Contracts {self.contracts}")

def clamp(v, lo, hi): return max(lo, min(hi, v))

def press_any_key_to_exit():
    try:
        input("\\nPress ENTER to exit…")
    except EOFError:
        pass

def choose(prompt, options):
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        s = input("> ").strip()
        if s.isdigit() and 1 <= int(s) <= len(options):
            return int(s) - 1
        print("Pick a number from the list.")

def intro(seed: Optional[int] = None) -> Player:
    say("=== Job Search Roguelike — v0.5.1 ===", bold=True)
    print("Tip: choose Age & Industry. Land a dream job — and take care of yourself along the way.\\n")
    if seed is None:
        try:
            seed_in = input("Optional: enter a seed for reproducibility (or press ENTER): ").strip()
            seed = int(seed_in) if seed_in else None
        except ValueError:
            seed = None
    if seed is not None:
        random.seed(seed)
        print(f"(Using seed {seed})\\n")

    name = input("Your name: ").strip() or "Player"
    age_idx = choose("Choose your age bracket:", list(BILLS_BY_AGE.keys()))
    age = list(BILLS_BY_AGE.keys())[age_idx]
    ind_names = list(INDUSTRIES.keys())
    start_idx = choose("Pick your current background industry:", ind_names)
    start_ind = ind_names[start_idx]
    target_idx = choose("Pick your target industry for job applications:", ind_names)
    target_ind = ind_names[target_idx]

    p = Player(name=name, age_bracket=age, start_industry=start_ind, target_industry=target_ind)
    # Give tiny starting skill in background
    for tag in INDUSTRIES[start_ind]["skills"]:
        p.skills[tag] = 1
    print("\\nFlavor:", INDUSTRIES[target_ind]["flavor"])
    say(f"\\nStarting stats → {p.status_line()}", color=Color.CYAN, bold=True)
    print("Win paths:")
    print(" • Dream Job offer in your target industry")
    print(f" • Survive {WEEKS_TO_SURVIVE} weeks without hitting zero")
    print(f" • Portfolio: secure {PORTFOLIO_TARGET}+ contracts")
    print(" • Pivot: land a job in an industry different from your background")
    print(" • Consultant: strong network, skills, and savings\\n")
    return p

def weekly_costs(player: Player):
    # Bills scale with age bracket
    bills = BILLS_BY_AGE[player.age_bracket]
    player.money -= bills
    say(f"Weekly bills: -${bills}", color=Color.YELLOW, bold=True)

    # Rent due every RENT_CYCLE_WEEKS
    if player.week % RENT_CYCLE_WEEKS == 0:
        rent = RENT_BY_AGE[player.age_bracket]
        player.money -= rent
        say(f"Rent due (week {player.week}): -${rent}", color=Color.RED, bold=True)

    # Unemployment safety net (extended in v0.5.1)
    if player.unemployed_weeks_paid < UNEMPLOY_WEEKS_MAX:
        player.money += UNEMPLOY_BENEFIT
        player.unemployed_weeks_paid += 1
        say(f"Unemployment benefit: +${UNEMPLOY_BENEFIT} (week {player.unemployed_weeks_paid}/{UNEMPLOY_WEEKS_MAX})", color=Color.GREEN, bold=True)

def random_weekly_event(player: Player):
    # Tilt RNG toward positive weeks:
    # 0.00-0.15: Surprise bill (15%)
    # 0.15-0.50: Temp gig (35%)
    # 0.50-1.00: Small good news (50%)
    roll = random.random()
    if roll < 0.15:
        amt = random.randint(*SURPRISE_BILL_RANGE)
        player.money -= amt
        say(f"Event: Surprise bill appears (parking ticket?): -${amt}", color=Color.RED, bold=True)
    elif roll < 0.50:
        pay = random.randint(*TEMP_GIG_MONEY_REWARD)
        player.money += pay
        player.energy = max(0, player.energy - TEMP_GIG_ENERGY_COST)
        # small morale bump sometimes
        if random.random() < 0.25:
            player.confidence += 1
            say(f"Event: Temp gig → +${pay}, Energy -{TEMP_GIG_ENERGY_COST}, Confidence +1", color=Color.CYAN, bold=True)
        else:
            say(f"Event: Temp gig → +${pay}, Energy -{TEMP_GIG_ENERGY_COST}", color=Color.CYAN, bold=True)
    else:
        m = random.randint(*SMALL_GOOD_NEWS_MONEY)
        c = random.randint(*SMALL_GOOD_NEWS_CONF)
        player.money += m
        player.confidence += c
        say(f"Event: Small good news → +${m} money, +{c} confidence", color=Color.GREEN, bold=True)

def act_rest(player: Player):
    player.energy += REST_GAIN_ENERGY
    player.confidence = clamp(player.confidence + 1, 0, 99)
    say(f"You rest. Energy +{REST_GAIN_ENERGY}, Confidence +1", color=Color.GREEN, bold=True)
    print("Taking care today powers tomorrow.")

def act_train(player: Player):
    if player.energy < TRAIN_COST_ENERGY:
        say("Too tired to train.", color=Color.RED, bold=True)
        return
    player.energy -= TRAIN_COST_ENERGY
    # Train a random tag from target industry
    tag = random.choice(list(INDUSTRIES[player.target_industry]["skills"]))
    player.skills[tag] = player.skills.get(tag, 0) + TRAIN_GAIN_SKILL
    player.confidence += 1
    say(f"You train {tag}. Skill +{TRAIN_GAIN_SKILL}, Confidence +1, Energy -{TRAIN_COST_ENERGY}", color=Color.CYAN, bold=True)
    print("Practice makes progress, not perfection.")

def act_network(player: Player):
    if player.energy < NETWORK_COST_ENERGY:
        say("Too tired to network.", color=Color.RED, bold=True)
        return
    player.energy -= NETWORK_COST_ENERGY
    player.confidence += 1
    # v0.5.1: higher chance for warm intro
    if random.random() < NETWORK_WARM_INTRO_CHANCE:
        player.warm_intro = True
        say("You networked into a WARM INTRO for next Apply!", color=Color.GREEN, bold=True)
    else:
        say("You networked. Confidence +1, Energy -2", color=Color.CYAN, bold=True)
    print("Even small conversations keep you visible.")

def act_selfcare(player: Player):
    if player.money < SELF_CARE_COST_MONEY:
        say("Not enough money for self-care.", color=Color.RED, bold=True)
        return
    player.money -= SELF_CARE_COST_MONEY
    player.energy += SELF_CARE_GAIN_ENERGY
    player.confidence += SELF_CARE_GAIN_CONF
    say(f"Self-care day: -${SELF_CARE_COST_MONEY}, Energy +{SELF_CARE_GAIN_ENERGY}, Confidence +{SELF_CARE_GAIN_CONF}", color=Color.GREEN, bold=True)
    print("Self-care isn’t a detour; it’s part of the road.")

def act_interview_prep(player: Player):
    if player.money < INTERVIEW_PREP_COST_MONEY or player.energy < INTERVIEW_PREP_COST_ENERGY:
        say("You lack money or energy for interview prep.", color=Color.RED, bold=True)
        return
    player.money -= INTERVIEW_PREP_COST_MONEY
    player.energy -= INTERVIEW_PREP_COST_ENERGY
    player.interview_prep_active = True
    say(f"You prepare for interviews: -${INTERVIEW_PREP_COST_MONEY}, Energy -{INTERVIEW_PREP_COST_ENERGY}, next interview gets +{int(INTERVIEW_PREP_TEMP_BOOST*100)}%", color=Color.CYAN, bold=True)
    print("Preparation turns nerves into signal.")

def rejection_hit(player: Player):
    # Confidence loss reduced by resilience; never below floor
    loss = max(1, int(REJECTION_CONFIDENCE_LOSS - player.resilience))
    player.confidence = max(CONFIDENCE_FLOOR, player.confidence - loss)
    player.resilience += RESILIENCE_GAIN_ON_REJECT
    player.consecutive_rejections += 1
    # 25% chance to receive a mentor boost for next Apply
    if random.random() < 0.25:
        player.mentor_boost = True
        say("A mentor reviewed your résumé. Next Apply gets a quiet boost.", color=Color.GREEN, bold=True)
    say(f"Rejection. Confidence -{loss}. Your resilience grows (+{RESILIENCE_GAIN_ON_REJECT}).", color=Color.YELLOW, bold=True)
    print("This one stings. Fit says nothing about your worth.")

def offer_received(player: Player, job_title: str, industry: str, dream: bool=False):
    if dream:
        player.win_reason = f"Landed Dream Job: {job_title} in {industry}"
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("Well done. You turned persistence into opportunity.")
        return
    # Contract or regular offer: treat as short contract
    player.contracts += 1
    gain = random.randint(200, 500)
    player.money += gain
    player.confidence += 2
    say(f"Offer! You secured a short contract in {industry}: +${gain}, Contracts {player.contracts}", color=Color.GREEN, bold=True)
    print("Not the dream yet, but your career kept moving.")

def apply_flow(player: Player):
    if player.energy < APPLY_COST_ENERGY:
        say("Too tired to apply.", color=Color.RED, bold=True)
        return

    player.energy -= APPLY_COST_ENERGY
    # Recruiter emotion
    emotion, mod, flavor = random.choice(RECRUITER_EMOTIONS)
    say(f"You apply to a {player.target_industry} role.", bold=True)
    print(f"Recruiter is {emotion} — {flavor}.")

    # Callback odds
    match_count = player.industry_skill_match(player.target_industry)
    warm = 0.15 if player.warm_intro else 0.0            # 0.10 -> 0.15
    prep = INTERVIEW_PREP_TEMP_BOOST if player.interview_prep_active else 0.0
    pity = 0.10 if player.consecutive_rejections >= 3 else 0.0
    mentor = 0.07 if player.mentor_boost else 0.0
    callback_odds = (
        BASE_CALLBACK_ODDS
        + player.confidence * CONF_CALLBACK_SCALE
        + match_count * SKILL_MATCH_BONUS
        + warm + mentor + pity
        + mod * 0.5  # emotion has milder effect on callback than offer
    )
    callback_odds = clamp(callback_odds, 0.01, 0.90)

    player.warm_intro = False  # consumed
    player.interview_prep_active = False  # consumed
    player.mentor_boost = False           # consumed

    if random.random() < callback_odds:
        say("Callback! You got an interview.", color=Color.GREEN, bold=True)
        player.consecutive_rejections = 0  # break cold streaks

        # Offer odds if callback
        offer_odds = (
            BASE_OFFER_ODDS
            + player.confidence * CONF_OFFER_SCALE
            + match_count * SKILL_MATCH_BONUS
            + prep
            + mod
        )
        offer_odds = clamp(offer_odds, 0.02, 0.85)

        # Dream job special chance if strong alignment
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
    else:
        rejection_hit(player)

def check_victory_conditions(player: Player):
    if player.game_over:
        return
    # Survival
    if player.week > WEEKS_TO_SURVIVE:
        player.win_reason = f"Survival Victory: You lasted {WEEKS_TO_SURVIVE} weeks."
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("You navigated challenges and kept going. That endurance matters.")
        return
    # Portfolio
    if player.contracts >= PORTFOLIO_TARGET:
        player.win_reason = f"Portfolio Victory: {player.contracts} contracts."
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("Your freelance projects added up to a sustainable path.")
        return
    # Pivot (land a job in different industry)
    if player.contracts >= 1 and player.target_industry != player.start_industry:
        player.win_reason = f"Pivot Victory: broke into {player.target_industry} from {player.start_industry}."
        player.game_over = True
        say(f"▶ Victory! {player.win_reason}", color=Color.GREEN, bold=True)
        print("A brave move. Your adaptability opened new doors.")
        return
    # Consultant victory: “network + skills + savings”
    # Approx: confidence 16+, at least 4 trained tags total, $1500+
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
        print("Running out doesn’t erase what you built. You can carry this resilience into the next run.")

def show_actions():
    print("\\nActions:")
    print("  1) Apply (Energy -2)  — Try for callbacks/offers")
    print("  2) Network (Energy -2) — Chance for warm intro next Apply")
    print("  3) Train (Energy -2)   — Improve a target-industry skill, +Confidence")
    print("  4) Rest                — Recover Energy, small Confidence")
    print("  5) Self-Care ($50)     — +Energy +Confidence")
    print("  6) Interview Prep ($60, Energy -2) — Big boost to next interview")
    print("  7) End week")

def game_loop(player: Player):
    while not player.game_over:
        say("\\n" + "=" * 48, color=Color.CYAN, bold=True)
        print(player.status_line())
        show_actions()
        choice = input("> ").strip()

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
        elif choice == "7":
            say("\\n— Week wrap-up —", color=Color.CYAN, bold=True)
            weekly_costs(player)
            random_weekly_event(player)
            player.week += 1
            did_action = True
        else:
            say("Pick 1–7.", color=Color.YELLOW, bold=True)

        check_loss(player)
        if not player.game_over:
            check_victory_conditions(player)

        # Pause so the player can read the outcome before the menu returns
        if not player.game_over and did_action:
            action_pause()

    # Exit screen (no flicker)
    say("\\n=== Run Summary ===", bold=True)
    print(player.status_line())
    if player.win_reason:
        print("Result:", player.win_reason)
        print("This journey wasn’t easy — you faced uncertainty and kept going. Well done.")
    elif player.loss_reason:
        print("Result:", player.loss_reason)
        print("You applied, learned, and built resilience. You’re not starting from zero next time.")
    press_any_key_to_exit()

def main():
    try:
        p = intro()
        game_loop(p)
    except KeyboardInterrupt:
        print("\\nInterrupted.")
        press_any_key_to_exit()

if __name__ == "__main__":
    main()
