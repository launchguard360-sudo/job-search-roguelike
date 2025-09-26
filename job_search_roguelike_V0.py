#!/usr/bin/env python3
# Job Search Roguelike - V0 (MVP) - exit pause fixed
import random, sys
VERSION = "V0"
def clamp(v, lo, hi): return max(lo, min(hi, v))
def chance(p): return random.random() < p/100.0
def generate_job():
    salary = random.randint(50000, 150000)
    skills = random.sample(["Excel","Coding","Writing","Negotiation","Project","Compliance"], k=2)
    return {"title": random.choice(["Analyst","Associate","Coordinator","Manager"]), "salary": salary, "skills": skills}
def salary_threshold(): return 120000
def apply(player):
    player["energy"] -= 8
    job = generate_job()
    cb = 20 + len(set(job["skills"]) & set(player["skills"])) * 15 + (player["confidence"] - 50) * 0.2
    cb = int(clamp(cb, 5, 80))
    if chance(cb):
        hm = int(clamp(40 + len(set(job["skills"]) & set(player["skills"])) * 15 + (player["confidence"] - 50) * 0.2, 10, 90))
        panel = int(clamp(35 + (player["energy"] - 50) * 0.1, 5, 95))
        if chance(hm) and chance(panel):
            if job["salary"] >= salary_threshold():
                return f"Dream job offer! ${job['salary']} — YOU WIN.", True
            else:
                player["money"] += job["salary"]//26
                player["confidence"] = clamp(player["confidence"]+5, 0, 100)
                return f"Short contract accepted (+${job['salary']//26}).", False
        else:
            player["confidence"] = clamp(player["confidence"]-5, 0, 100)
            return f"Interview fizzled (HM {hm}%, Panel {panel}%).", False
    else:
        player["confidence"] = clamp(player["confidence"]-3, 0, 100)
        return "Rejection email.", False
def network(player):
    player["energy"] -= 6
    gained = random.choice([0,1,1,2])
    player["leads"] = clamp(player["leads"]+gained, 0, 5)
    player["confidence"] = clamp(player["confidence"] + random.choice([+1,+2,-1]), 0, 100)
    return f"Networking: leads +{gained}."
def train(player):
    player["energy"] -= 8
    option = random.choice([("Excel",150),("Coding",400),("Negotiation",200),("Compliance",100),("Project",150)])
    if player["money"] < option[1]:
        return f"Couldn't afford training ({option[0]} costs ${option[1]})."
    player["money"] -= option[1]
    player["skills"].append(option[0])
    player["confidence"] = clamp(player["confidence"]+2, 0, 100)
    return f"Trained: {option[0]} (-${option[1]})."
def rest(player):
    gain = random.randint(10,20)
    player["energy"] = clamp(player["energy"]+gain, 0, 100)
    player["confidence"] = clamp(player["confidence"]+1, 0, 100)
    return f"Rested +{gain} energy."
def pay_bills(player):
    if player["week"] % 4 == 0:
        player["money"] -= 1000
        return "Paid bills: -$1000."
    return ""
def check_end(player):
    if player["money"] <= -100: return True, "Evicted (money)."
    if player["energy"] <= 0: return True, "Burnout (energy)."
    if player["confidence"] <= 0: return True, "Gave up (confidence)."
    return False, ""
def main():
    random.seed()
    name = input("Your name: ").strip() or "Player"
    player = {"name": name, "energy": 70, "money": 2000, "confidence": 60, "skills": ["Writing"], "week": 1, "leads": 0}
    print(f"\nJob Search Roguelike {VERSION}\n")
    while True:
        print("="*60)
        print(f"Week {player['week']} | Energy {player['energy']} | Money ${player['money']} | Confidence {player['confidence']} | Leads {player['leads']} | Skills {sorted(set(player['skills']))}")
        msg = pay_bills(player)
        if msg: print(msg)
        over, why = check_end(player)
        if over:
            print("GAME OVER —", why)
            break
        print("1) Apply  2) Network  3) Train  4) Rest")
        choice = input("> ").strip()
        if choice == "1":
            m, win = apply(player); print(m); 
            if win: break
        elif choice == "2":
            print(network(player))
        elif choice == "3":
            print(train(player))
        elif choice == "4":
            print(rest(player))
        else:
            print("Do nothing.")
        player["week"] += 1
    try:
        input("\nPress any key to exit...")
    except (EOFError, KeyboardInterrupt):
        pass
if __name__ == "__main__":
    main()
