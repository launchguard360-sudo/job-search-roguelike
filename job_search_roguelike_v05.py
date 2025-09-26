#!/usr/bin/env python3
# Job Search Roguelike — v0.5 (terminal prototype)
# Features included:
# V0: Core stats (Energy, Money, Confidence), Actions (Apply, Network, Train, Rest),
#     random events (rejections, bills, small wins), Victory (dream job), Loss (any stat <= 0),
#     exit flicker fix (press any key to exit).
# V0.1: Age brackets (Young/Mid/Late), Industries (skills + culture flavor),
#       bills scale with age bracket.
# V0.2: Recruiter emotions, new weekly events, flavorful text.
# V0.3: Rent due every 6 weeks, unemployment safety net ($200/wk, 4 weeks),
#       Resilience (rejections sting less over time), energy/cost tweaks.
# V0.4: Multiple victory paths (Survival 26w, Portfolio 3+ contracts, Pivot, Consultant).
# V0.5: Player agency: Self-Care, Interview Prep, Networking warm intros.

import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# -----------------------------
# Tunables (balance knobs)
# -----------------------------
WEEKS_TO_SURVIVE = 26
RENT_CYCLE_WEEKS = 6
UNEMPLOY_BENEFIT = 200
UNEMPLOY_WEEKS_MAX = 4

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
NETWORK_WARM_INTRO_CHANCE = 0.25  # v0.5

REST_GAIN_ENERGY = 4

APPLY_COST_ENERGY = 2
INTERVIEW_PREP_TEMP_BOOST = 0.15  # v0.5
INTERVIEW_PREP_COST_MONEY = 60
INTERVIEW_PREP_COST_ENERGY = 2

SELF_CARE_COST_MONEY = 50
SELF_CARE_GAIN_ENERGY = 2
SELF_CARE_GAIN_CONF = 2

# Base success odds tuning
BASE_CALLBACK_ODDS = 0.18
BASE_OFFER_ODDS = 0.22

# Confidence contribution scaling to callbacks/offers
CONF_CALLBACK_SCALE = 0.004
CONF_OFFER_SCALE = 0.004

# Skill contribution (matching industry skills)
SKILL_MATCH_BONUS = 0.02  # per matching tag count

# Resilience tuning (rejections sting less over time)
RESILIENCE_GAIN_ON_REJECT = 0.5
REJECTION_CONFIDENCE_LOSS = 4  # reduced by resilience

# Gig/Temp rewards
TEMP_GIG_MONEY_REWARD = (60, 140)
TEMP_GIG_ENERGY_COST = 2

# Small good news
SMALL_GOOD_NEWS_MONEY = (20, 80)
SMALL_GOOD_NEWS_CONF = (1, 3)

# Bills surprise
SURPRISE_BILL_RANGE = (40, 120)

# Portfolio contracts target (v0.4)
PORTFOLIO_TARGET = 3

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
        input("\nPress ENTER to exit…")
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
    print("=== Job Search Roguelike — v0.5 ===")
    print("Tip: set environment by choosing Age & Industry. Survive 26 weeks or land a dream job.\n")
    if seed is None:
        try:
            seed_in = input("Optional: enter a seed for reproducibility (or press ENTER): ").strip()
            seed = int(seed_in) if seed_in else None
        except ValueError:
            seed = None
    if seed is not None:
        random.seed(seed)
        print(f"(Using seed {seed})\n")

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
    print("\nFlavor:", INDUSTRIES[target_ind]["flavor"])
    print(f"\nStarting stats → {p.status_line()}")
    print("Win paths:")
    print(" • Dream Job offer in your target industry")
    print(f" • Survive {WEEKS_TO_SURVIVE} weeks without hitting zero")
    print(f" • Portfolio: secure {PORTFOLIO_TARGET}+ contracts")
    print(" • Pivot: land a job in an industry different from your background")
    print(" • Consultant: high network & skill presence with savings\n")
    return p

def weekly_costs(player: Player):
    # Bills scale with age bracket
    bills = BILLS_BY_AGE[player.age_bracket]
    player.money -= bills
    print(f"Weekly bills: -${bills}")

    # Rent due every RENT_CYCLE_WEEKS
    if player.week % RENT_CYCLE_WEEKS == 0:
        rent = RENT_BY_AGE[player.age_bracket]
        player.money -= rent
        print(f"Rent due (week {player.week}): -${rent}")

    # Unemployment safety net (first 4 weeks only)
    if player.unemployed_weeks_paid < UNEMPLOY_WEEKS_MAX:
        player.money += UNEMPLOY_BENEFIT
        player.unemployed_weeks_paid += 1
        print(f"Unemployment benefit: +${UNEMPLOY_BENEFIT} (week {player.unemployed_weeks_paid}/{UNEMPLOY_WEEKS_MAX})")

def random_weekly_event(player: Player):
    roll = random.random()
    if roll < 0.25:
        # Surprise bill
        amt = random.randint(*SURPRISE_BILL_RANGE)
        player.money -= amt
        print(f"Event: Surprise bill appears (parking ticket?): -${amt}")
    elif roll < 0.50:
        # Temp gig
        pay = random.randint(*TEMP_GIG_MONEY_REWARD)
        player.money += pay
        player.energy = max(0, player.energy - TEMP_GIG_ENERGY_COST)
        print(f"Event: Temp gig weekend → +${pay}, Energy -{TEMP_GIG_ENERGY_COST}")
    else:
        # Small good news
        m = random.randint(*SMALL_GOOD_NEWS_MONEY)
        c = random.randint(*SMALL_GOOD_NEWS_CONF)
        player.money += m
        player.confidence += c
        print(f"Event: Small good news → +${m} money, +{c} confidence")

def act_rest(player: Player):
    player.energy += REST_GAIN_ENERGY
    player.confidence = clamp(player.confidence + 1, 0, 99)
    print(f"You rest. Energy +{REST_GAIN_ENERGY}, Confidence +1")

def act_train(player: Player):
    if player.energy < TRAIN_COST_ENERGY:
        print("Too tired to train.")
        return
    player.energy -= TRAIN_COST_ENERGY
    # Train a random tag from target industry
    tag = random.choice(list(INDUSTRIES[player.target_industry]["skills"]))
    player.skills[tag] = player.skills.get(tag, 0) + TRAIN_GAIN_SKILL
    player.confidence += 1
    print(f"You train {tag}. Skill +{TRAIN_GAIN_SKILL}, Confidence +1, Energy -{TRAIN_COST_ENERGY}")

def act_network(player: Player):
    if player.energy < NETWORK_COST_ENERGY:
        print("Too tired to network.")
        return
    player.energy -= NETWORK_COST_ENERGY
    player.confidence += 1
    # v0.5: chance for warm intro
    if random.random() < NETWORK_WARM_INTRO_CHANCE:
        player.warm_intro = True
        print("You networked into a WARM INTRO for next Apply! (Better callback odds)")
    else:
        print("You networked. Confidence +1, Energy -2")

def act_selfcare(player: Player):
    if player.money < SELF_CARE_COST_MONEY:
        print("Not enough money for self-care.")
        return
    player.money -= SELF_CARE_COST_MONEY
    player.energy += SELF_CARE_GAIN_ENERGY
    player.confidence += SELF_CARE_GAIN_CONF
    print(f"Self-care day: -${SELF_CARE_COST_MONEY}, Energy +{SELF_CARE_GAIN_ENERGY}, Confidence +{SELF_CARE_GAIN_CONF}")

def act_interview_prep(player: Player):
    if player.money < INTERVIEW_PREP_COST_MONEY or player.energy < INTERVIEW_PREP_COST_ENERGY:
        print("You lack money or energy for interview prep.")
        return
    player.money -= INTERVIEW_PREP_COST_MONEY
    player.energy -= INTERVIEW_PREP_COST_ENERGY
    player.interview_prep_active = True
    print(f"You prepare for interviews: -${INTERVIEW_PREP_COST_MONEY}, Energy -{INTERVIEW_PREP_COST_ENERGY}, next interview gets +{int(INTERVIEW_PREP_TEMP_BOOST*100)}%")

def rejection_hit(player: Player):
    # Confidence loss reduced by resilience
    loss = max(1, int(REJECTION_CONFIDENCE_LOSS - player.resilience))
    player.confidence -= loss
    player.resilience += RESILIENCE_GAIN_ON_REJECT
    print(f"Rejection. Confidence -{loss}. Your resilience grows (+{RESILIENCE_GAIN_ON_REJECT}).")

def offer_received(player: Player, job_title: str, industry: str, dream: bool=False):
    if dream:
        player.win_reason = f"Landed Dream Job: {job_title} in {industry}"
        player.game_over = True
        print(f"▶ Victory! {player.win_reason}")
        return
    # Contract or regular offer: for prototype, treat as short contract
    player.contracts += 1
    gain = random.randint(200, 500)
    player.money += gain
    player.confidence += 2
    print(f"Offer! You secured a short contract in {industry}: +${gain}, Contracts {player.contracts}")

def apply_flow(player: Player):
    if player.energy < APPLY_COST_ENERGY:
        print("Too tired to apply.")
        return

    player.energy -= APPLY_COST_ENERGY
    # Recruiter emotion
    emotion, mod, flavor = random.choice(RECRUITER_EMOTIONS)

    # Callback odds
    match_count = player.industry_skill_match(player.target_industry)
    warm = 0.10 if player.warm_intro else 0.0
    prep = INTERVIEW_PREP_TEMP_BOOST if player.interview_prep_active else 0.0
    callback_odds = (
        BASE_CALLBACK_ODDS
        + player.confidence * CONF_CALLBACK_SCALE
        + match_count * SKILL_MATCH_BONUS
        + warm
        + mod * 0.5  # emotion has milder effect on callback than offer
    )
    callback_odds = clamp(callback_odds, 0.01, 0.90)

    print(f"You apply to a {player.target_industry} role. Recruiter is {emotion} ({flavor}).")
    player.warm_intro = False  # consumed
    player.interview_prep_active = False  # consumed even if no callback (you used it this cycle)

    if random.random() < callback_odds:
        print("Callback! You got an interview.")
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
        dream_bonus = 0.08 if (match_count >= 2 and player.confidence >= 14) else 0.0
        dream_odds = clamp(0.03 + dream_bonus, 0.0, 0.35)

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
        print(f"▶ Victory! {player.win_reason}")
        return
    # Portfolio
    if player.contracts >= PORTFOLIO_TARGET:
        player.win_reason = f"Portfolio Victory: {player.contracts} contracts."
        player.game_over = True
        print(f"▶ Victory! {player.win_reason}")
        return
    # Pivot (land a job in different industry) — here represented by any contract in target != start
    if player.contracts >= 1 and player.target_industry != player.start_industry:
        player.win_reason = f"Pivot Victory: broke into {player.target_industry} from {player.start_industry}."
        player.game_over = True
        print(f"▶ Victory! {player.win_reason}")
        return
    # Consultant victory: “network + skills + savings”
    # Approx: confidence 16+, at least 4 trained tags total, $1500+
    trained_tags = sum(1 for v in player.skills.values() if v >= 2)
    if player.confidence >= 16 and trained_tags >= 4 and player.money >= 1500:
        player.win_reason = "Consultant Victory: strong skills, network, and runway."
        player.game_over = True
        print(f"▶ Victory! {player.win_reason}")

def check_loss(player: Player):
    if player.any_stat_empty():
        player.loss_reason = "You ran out of a core stat (Energy, Money, or Confidence)."
        player.game_over = True
        print(f"✖ Defeat. {player.loss_reason}")

def show_actions():
    print("\nActions:")
    print("  1) Apply (Energy -2)  — Try for callbacks/offers")
    print("  2) Network (Energy -2) — Chance for warm intro next Apply")
    print("  3) Train (Energy -2)   — Improve a target-industry skill, +Confidence")
    print("  4) Rest                — Recover Energy, small Confidence")
    print("  5) Self-Care ($50)     — +Energy +Confidence")
    print("  6) Interview Prep ($60, Energy -2) — Big boost to next interview")
    print("  7) End week")

def game_loop(player: Player):
    while not player.game_over:
        print("\n" + "=" * 48)
        print(player.status_line())
        show_actions()
        choice = input("> ").strip()

        if choice == "1":
            apply_flow(player)
        elif choice == "2":
            act_network(player)
        elif choice == "3":
            act_train(player)
        elif choice == "4":
            act_rest(player)
        elif choice == "5":
            act_selfcare(player)
        elif choice == "6":
            act_interview_prep(player)
        elif choice == "7":
            # Weekly rollover
            print("\n— Week wrap-up —")
            weekly_costs(player)
            random_weekly_event(player)
            player.week += 1
        else:
            print("Pick 1–7.")

        check_loss(player)
        if not player.game_over:
            check_victory_conditions(player)

    # Exit screen (no flicker)
    print("\n=== Run Summary ===")
    print(player.status_line())
    if player.win_reason:
        print("Result:", player.win_reason)
    elif player.loss_reason:
        print("Result:", player.loss_reason)
    press_any_key_to_exit()

def main():
    try:
        p = intro()
        game_loop(p)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        press_any_key_to_exit()

if __name__ == "__main__":
    main()
