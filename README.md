# Job Search Roguelike

*A text-based roguelike that turns job search trauma into gameplay*

## 🎮 The Experience
- Apply to jobs (and face rejection)
- Pay bills while savings drain  
- Manage energy, confidence, and sanity
- Different outcomes based on age and industry
- Try to land that dream job before you burn out

## 🚀 How to Play
**Python Version:**
Run: `python job_search_roguelike_V0.py`

Windows EXE: Available on itch.io - no installation needed!
Character Creation

Enter your name (or hit Enter for "Player")
Choose age bracket:

Young Grad: High energy, eager to learn, low money, manageable bills
Mid-Career: Balanced stats, no major advantages/disadvantages
Late-Career: High money reserves, strong confidence, but faces ageism


Pick your industry (affects available jobs and required skills)

Core Gameplay Loop
Each week, choose one action. Every choice costs energy and time:
🔍 Apply to Jobs (Energy: -8)

Random job postings appear with different salaries and skill requirements
Your callback chance depends on: skill overlap + confidence + leads
If you get an interview, face two skill checks: Hiring Manager + Panel
Outcomes: Rejection (confidence hit) → Interview invite → Job offer or failure

🤝 Network (Energy: -6)

Attend meetups, send LinkedIn messages, coffee chats
Gain 0-2 leads (max 5) which boost future application success
Small confidence boost/hit depending on how awkward it goes
Tip: Leads significantly improve your callback rates

📚 Train Skills (Energy: -8)

Random training options appear (Excel, Coding, Negotiation, etc.)
Costs money but adds permanent skills to your profile
More skill overlap with jobs = much better callback chances
Strategy: Invest early when you have money

😴 Rest (Energy: +10-20)

Recover energy and slight confidence boost
Sometimes you need to rest to avoid complete burnout
Balance: Don't rest too much or bills will crush you

💼 Gig Job (Energy: -6)

Quick cash from temp work or freelancing
Small confidence hit (soul-crushing work) but pays bills
Emergency option when money gets too low

Resources to Manage

💰 Money: Starts at $2000, drains from bills every 4 weeks ($1000)
⚡ Energy: Starts at 70, depletes with actions, recover by resting
😊 Confidence: Starts at 60, affected by rejections/successes
🎯 Leads: Start at 0, max 5, boost your application success rates
🛠️ Skills: Start with one, gain more through training

Victory Conditions
🏆 Dream Job Victory: Land a high-paying role ($120k+) that matches your skills
Defeat Conditions

💸 Evicted: Money drops below -$100
🔥 Burnout: Energy hits 0 (you're too exhausted to continue)
😔 Gave Up: Confidence drops to 0 (lost all hope)

Pro Tips

Early game: Focus on training skills when you have money
Mid game: Balance applications with networking for leads
Late game: If low on money, take gig work to survive
Bills: Every 4 weeks you pay $1000 - plan accordingly
Skill matching: Jobs requiring your exact skills have much higher callback rates
Confidence spiral: Rejections hurt confidence, which hurts future success - take breaks to rest

Sample Turn
Week 3 | Energy 45 | Money $1200 | Confidence 52 | Leads 2 | Skills ['Writing']
1) Apply  2) Network  3) Train  4) Rest

> 1
Interview invite! Recruiter sounded excited.
You crushed the interviews! HM check 65%, Panel check 78%.
OFFER: Decent role (Salary $75000). You accept a short-term contract. (+money, run continues)

🛠️ Built With

Python 3
Pure text interface
Roguelike mechanics applied to career struggles

🗺️ Development Roadmap

**V0 (Current)**: Core mechanics - prove the concept works
- Basic job search loop, simple victory condition

**V0.1 (Next)**: Quality of life improvements  
- Age brackets, industry variety, better balance

**V0.2 (Soon)**: Personality & flavor
- Recruiter emotions, more event variety, better text

**V0.3+**: Based on your feedback!
- Multiple victory paths, better economy, deeper systems

**What should we prioritize?** Join the discussion!

💬 Feedback Welcome!
This is V0 - built from real job search experience. What resonates? What's missing?
Found a bug? Open an issue
Have an idea? Start a discussion
Want to contribute? Fork and submit a PR!

"Disturbingly accurate" - Beta Tester
"Harder than Dark Souls" - Unemployed Developer
