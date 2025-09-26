#!/usr/bin/env python3
# Job Search Roguelike — v0.4
# Adds multiple win paths: Survival, Portfolio (3+ contracts), Pivot, Consultant.

import random
from dataclasses import dataclass, field
from typing import Optional

WEEKS_TO_SURVIVE = 26
RENT_CYCLE_WEEKS = 6
UNEMPLOY_BENEFIT = 200
UNEMPLOY_WEEKS_MAX = 4
PORTFOLIO_TARGET = 3

BILLS_BY_AGE = {"Young": 80, "Mid": 140, "Late": 200}
RENT_BY_AGE  = {"Young": 600, "Mid": 900, "Late": 1200}

INDUSTRIES = {
    "Tech":{"skills":{"coding","product","data"},"flavor":"fast-paced, ambiguous"},
    "Finance":{"skills":{"excel","analysis","risk"},"flavor":"formal, metrics-driven"},
    "Healthcare":{"skills":{"compliance","patient","ops"},"flavor":"process-heavy, safety first"},
    "Creative":{"skills":{"design","portfolio","story"},"flavor":"portfolio-forward, references matter"},
}

RECRUITER_EMOTIONS=[("cheery",+0.07,"sounds excited"),
                    ("rushed",-0.03,"is juggling calls"),
                    ("skeptical",-0.07,"probes your gaps")]

BASE_CALLBACK_ODDS=0.18; BASE_OFFER_ODDS=0.22
CONF_SCALE=0.004; SKILL_MATCH_BONUS=0.02
REJECTION_CONF_LOSS=4; RESILIENCE_GAIN=0.5

@dataclass
class Player:
    name:str; age_bracket:str; start_industry:str; target_industry:str
    week:int=1; energy:int=10; money:int=400; confidence:int=10
    resilience:float=0.0; unemployed_weeks_paid:int=0
    contracts:int=0
    skills:dict = field(default_factory=lambda:{k:0 for k in {"coding","product","data","excel","analysis","risk","compliance","patient","ops","design","portfolio","story"}})
    game_over:bool=False; win_reason:Optional[str]=None; loss_reason:Optional[str]=None
    def any_stat_empty(self): return self.energy<=0 or self.money<=0 or self.confidence<=0
    def status(self): return f"Week {self.week} | E{self.energy} | ${self.money} | Conf {self.confidence} | Res {self.resilience:.1f} | Contracts {self.contracts}"

def clamp(v,lo,hi): return max(lo,min(hi,v))
def choose(prompt, options):
    print(prompt); [print(f"  {i}. {o}") for i,o in enumerate(options,1)]
    while True:
        s=input("> ").strip()
        if s.isdigit() and 1<=int(s)<=len(options): return options[int(s)-1]
        print("Pick a number from the list.")

def intro()->Player:
    print("=== Job Search Roguelike — v0.4 ===")
    name=input("Your name: ").strip() or "Player"
    age=choose("Choose age bracket:", list(BILLS_BY_AGE.keys()))
    inds=list(INDUSTRIES.keys())
    start=choose("Pick current background industry:", inds)
    target=choose("Pick target industry:", inds)
    p=Player(name,age,start,target)
    for t in INDUSTRIES[start]["skills"]: p.skills[t]=1
    print("Flavor:", INDUSTRIES[target]["flavor"])
    print("Win paths: Dream offer, survive 26w, 3+ contracts, pivot, consultant.\n")
    print(p.status()); return p

def weekly_rollover(p:Player):
    bills=BILLS_BY_AGE[p.age_bracket]; p.money-=bills; print(f"Weekly bills: -${bills}")
    if p.week % RENT_CYCLE_WEEKS == 0:
        rent=RENT_BY_AGE[p.age_bracket]; p.money-=rent; print(f"Rent due: -${rent}")
    if p.unemployed_weeks_paid < UNEMPLOY_WEEKS_MAX:
        p.money += UNEMPLOY_BENEFIT; p.unemployed_weeks_paid += 1
        print(f"Unemployment benefit: +${UNEMPLOY_BENEFIT} ({p.unemployed_weeks_paid}/{UNEMPLOY_WEEKS_MAX})")
    # Weekly event variety
    r=random.random()
    if r<0.33:
        amt=random.randint(40,120); p.money-=amt; print(f"Event: Surprise bill -${amt}")
    elif r<0.66:
        pay=random.randint(70,150); p.money+=pay; p.energy=max(0,p.energy-3); print(f"Event: Temp gig +${pay}, Energy -3")
    else:
        m=random.randint(20,80); c=random.randint(1,3); p.money+=m; p.confidence+=c; print(f"Event: Good news +${m}, +{c} Conf")

def match_count(p:Player)->int:
    return sum(p.skills.get(t,0)>0 for t in INDUSTRIES[p.target_industry]["skills"])

def rejection(p:Player):
    loss=max(1,int(REJECTION_CONF_LOSS - p.resilience))
    p.confidence -= loss; p.resilience += RESILIENCE_GAIN
    print(f"Rejection. Confidence -{loss}. Resilience +{RESILIENCE_GAIN}")

def offer_contract(p:Player, industry:str):
    p.contracts += 1
    pay = random.randint(200, 500)
    p.money += pay; p.confidence += 2
    print(f"Contract secured in {industry}: +${pay}, Contracts {p.contracts}")

def act_apply(p:Player):
    if p.energy<2: print("Too tired to apply."); return
    p.energy-=2
    emotion,mod,flavor=random.choice(RECRUITER_EMOTIONS)
    print(f"Apply → Recruiter is {emotion} and {flavor}.")
    m=match_count(p)
    cb=clamp(BASE_CALLBACK_ODDS + p.confidence*CONF_SCALE + m*SKILL_MATCH_BONUS + 0.5*mod, 0.02, 0.9)
    if random.random()<cb:
        print("Callback! Interview scheduled.")
        offer=clamp(BASE_OFFER_ODDS + p.confidence*CONF_SCALE + m*SKILL_MATCH_BONUS + mod, 0.02, 0.85)
        r=random.random()
        if r < offer*0.35:   # a slice is a full-time "dream" style offer
            p.win_reason=f"Dream Offer in {p.target_industry}!"; p.game_over=True
        elif r < offer:
            offer_contract(p, p.target_industry)
        else:
            rejection(p)
    else:
        rejection(p)

def act_network(p:Player):
    if p.energy<2: print("Too tired to network."); return
    p.energy-=2; p.confidence+=1; print("You networked. Confidence +1")

def act_train(p:Player):
    if p.energy<2: print("Too tired to train."); return
    p.energy-=2; tag=random.choice(list(INDUSTRIES[p.target_industry]["skills"]))
    p.skills[tag]=p.skills.get(tag,0)+1; p.confidence+=1
    print(f"You trained {tag}. Skill +1, Confidence +1")

def act_rest(p:Player):
    p.energy+=4; p.confidence+=1; print("You rested. Energy +4, Confidence +1")

def menu(p:Player):
    print("\nActions:\n 1) Apply (E-2)\n 2) Network (E-2)\n 3) Train (E-2)\n 4) Rest\n 5) End week")
    c=input("> ").strip()
    if   c=="1": act_apply(p)
    elif c=="2": act_network(p)
    elif c=="3": act_train(p)
    elif c=="4": act_rest(p)
    elif c=="5": weekly_rollover(p); p.week+=1
    else: print("Pick 1–5")

def check_wins(p:Player):
    if p.week>WEEKS_TO_SURVIVE:
        p.game_over=True; p.win_reason=f"Survival Victory: {WEEKS_TO_SURVIVE} weeks."
        return
    if p.contracts >= PORTFOLIO_TARGET:
        p.game_over=True; p.win_reason=f"Portfolio Victory: {p.contracts} contracts."
        return
    if p.contracts>=1 and p.target_industry!=p.start_industry:
        p.game_over=True; p.win_reason=f"Pivot Victory: broke into {p.target_industry}."
        return
    trained_tags = sum(1 for v in p.skills.values() if v>=2)
    if p.confidence>=16 and trained_tags>=4 and p.money>=1500:
        p.game_over=True; p.win_reason="Consultant Victory: skills+network+savings."

def end_check(p:Player):
    if p.any_stat_empty(): p.game_over=True; p.loss_reason="A core stat hit zero."
    if not p.game_over: check_wins(p)
    if p.game_over:
        print("\n=== Run Summary ==="); print(p.status())
        print("Result:", p.win_reason or p.loss_reason or "Unknown")
        input("Press ENTER to exit…")

def main():
    print("Tip: Win paths = Survive / Portfolio / Pivot / Consultant / Dream Offer.")
    name=input("Your name: ").strip() or "Player"
    age=choose("Choose age bracket:", list(BILLS_BY_AGE.keys()))
    inds=list(INDUSTRIES.keys())
    start=choose("Pick current background industry:", inds)
    target=choose("Pick target industry:", inds)
    p=Player(name,age,start,target)
    for t in INDUSTRIES[start]["skills"]: p.skills[t]=1
    print("Flavor:", INDUSTRIES[target]["flavor"])
    print(p.status())
    while not p.game_over:
        print("\n", p.status()); menu(p); end_check(p)

if __name__=="__main__":
    main()
