#!/usr/bin/env python3
# Job Search Roguelike — v0.1
# Adds: Age brackets, Industries with skill tags & flavor, bills scale with age.

import random
from dataclasses import dataclass, field
from typing import Optional

BILLS_BY_AGE = {"Young": 80, "Mid": 140, "Late": 200}

INDUSTRIES = {
    "Tech": {"skills": {"coding", "product", "data"}, "flavor": "fast-paced, ambiguous requirements"},
    "Finance": {"skills": {"excel", "analysis", "risk"}, "flavor": "formal, metrics-driven"},
    "Healthcare": {"skills": {"compliance", "patient", "ops"}, "flavor": "process-heavy, safety first"},
    "Creative": {"skills": {"design", "portfolio", "story"}, "flavor": "portfolio-forward, references matter"},
}

BASE_CALLBACK_ODDS = 0.18
BASE_OFFER_ODDS = 0.22
CONF_SCALE = 0.004
SKILL_MATCH_BONUS = 0.02

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
    skills: dict = field(default_factory=lambda: {k:0 for k in {"coding","product","data","excel","analysis","risk","compliance","patient","ops","design","portfolio","story"}})
    game_over: bool = False
    win_reason: Optional[str] = None
    loss_reason: Optional[str] = None

    def any_stat_empty(self):
        return self.energy <= 0 or self.money <= 0 or self.confidence <= 0

    def status(self):
        return f"Week {self.week} | Energy {self.energy} | Money ${self.money} | Confidence {self.confidence}"

def clamp(v, lo, hi): return max(lo, min(hi, v))

def choose(prompt, options):
    print(prompt)
    for i, o in enumerate(options, 1): print(f"  {i}. {o}")
    while True:
        s = input("> ").strip()
        if s.isdigit() and 1 <= int(s) <= len(options): return options[int(s)-1]
        print("Pick a number from the list.")

def intro() -> Player:
    print("=== Job Search Roguelike — v0.1 ===")
    name = input("Your name: ").strip() or "Player"
    age = choose("Choose age bracket:", list(BILLS_BY_AGE.keys()))
    inds = list(INDUSTRIES.keys())
    start = choose("Pick current background industry:", inds)
    target = choose("Pick target industry:", inds)
    p = Player(name, age, start, target)
    for tag in INDUSTRIES[start]["skills"]:
        p.skills[tag] = 1  # tiny head start
    print("Flavor:", INDUSTRIES[target]["flavor"])
    print("Goal: Land the dream job. Loss if any stat hits 0.")
    print(p.status())
    return p

def weekly_rollover(p: Player):
    bills = BILLS_BY_AGE[p.age_bracket]
    p.money -= bills
    print(f"Weekly bills: -${bills}")

def random_event(p: Player):
    r = random.random()
    if r < 0.33:
        p.money -= random.randint(20, 60); print("Random bill arrives: -$")
    elif r < 0.66:
        p.money += random.randint(20, 60); print("Small win: +$")
    else:
        p.confidence += 1; print("Encouraging message: Confidence +1")

def industry_match(p: Player) -> int:
    return sum(p.skills.get(t,0) > 0 for t in INDUSTRIES[p.target_industry]["skills"])

def act_apply(p: Player):
    if p.energy < 2: print("Too tired to apply."); return
    p.energy -= 2
    match = industry_match(p)
    cb_odds = clamp(BASE_CALLBACK_ODDS + p.confidence*CONF_SCALE + match*SKILL_MATCH_BONUS, 0.02, 0.9)
    if random.random() < cb_odds:
        offer_odds = clamp(BASE_OFFER_ODDS + p.confidence*CONF_SCALE + match*SKILL_MATCH_BONUS, 0.02, 0.85)
        if random.random() < offer_odds:
            p.win_reason = f"Offer in {p.target_industry}! You win."
            p.game_over = True
        else:
            p.confidence -= 3; print("Interview went okay… but no offer. Confidence -3")
    else:
        p.confidence -= 4; print("No callback. Confidence -4")

def act_network(p: Player):
    if p.energy < 2: print("Too tired to network."); return
    p.energy -= 2; p.confidence += 1
    print("You networked. Confidence +1")

def act_train(p: Player):
    if p.energy < 2: print("Too tired to train."); return
    p.energy -= 2
    tag = random.choice(list(INDUSTRIES[p.target_industry]["skills"]))
    p.skills[tag] = p.skills.get(tag,0) + 1
    p.confidence += 1
    print(f"You trained {tag}. Skill +1, Confidence +1")

def act_rest(p: Player):
    p.energy += 4; p.confidence += 1
    print("You rested. Energy +4, Confidence +1")

def turn_menu(p: Player):
    print("\nActions:\n 1) Apply (E-2)\n 2) Network (E-2)\n 3) Train (E-2)\n 4) Rest\n 5) End week")
    c = input("> ").strip()
    if   c=="1": act_apply(p)
    elif c=="2": act_network(p)
    elif c=="3": act_train(p)
    elif c=="4": act_rest(p)
    elif c=="5":
        weekly_rollover(p); random_event(p); p.week += 1
    else: print("Pick 1–5")

def check_end(p: Player):
    if p.any_stat_empty():
        p.game_over=True; p.loss_reason="A core stat hit zero."
    if p.game_over:
        print("\n=== Run Summary ===")
        print(p.status())
        print("Result:", p.win_reason or p.loss_reason or "Unknown")
        input("Press ENTER to exit…")

def main():
    p = intro()
    while not p.game_over:
        print("\n", p.status())
        turn_menu(p)
        check_end(p)

if __name__ == "__main__":
    main()
