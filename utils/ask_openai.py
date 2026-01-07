"""
Query OpenAI for Whiteout Survival game knowledge.
"""

import os
import json
from openai import OpenAI

# Get API key from Windows environment
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    # Try to get from Windows user environment via subprocess
    import subprocess
    result = subprocess.run(
        ['powershell', '-Command', "[Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')"],
        capture_output=True, text=True
    )
    api_key = result.stdout.strip()

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are an expert Whiteout Survival (WoS) player and strategist with deep knowledge of:
- Hero mechanics, skills (expedition vs exploration), and tier rankings
- Troop compositions and ratios for different game modes
- Rally mechanics (leader vs joiner roles)
- SvS (State vs State) strategies
- Arena and Alliance Championship meta
- Progression strategies for different spender levels (F2P, low, medium, heavy)
- Generation transitions (S1 -> S2 -> S3) and meta shifts

Provide specific, actionable advice based on current game meta. Be concise but thorough."""

def ask_wos_question(question: str) -> str:
    """Ask OpenAI a WoS-related question."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content

def main():
    questions = [
        """1. HERO SYNERGIES: Are there specific hero combinations in Whiteout Survival that have skill synergies beyond just "best in class"? For example, do certain heroes' expedition skills stack or complement each other in ways that make specific 3-hero combos better than just picking top-tier heroes?""",

        """2. TROOP RATIOS: I have these troop ratios - please validate or correct:
- Default Attack: 55% Infantry, 15% Lancer, 30% Marksman
- Castle Defense/Garrison: 60% Infantry, 15% Lancer, 25% Marksman
- Bear Trap Rally Leader: 20% Infantry, 20% Lancer, 60% Marksman
- Rally Joiner: 30% Infantry, 20% Lancer, 50% Marksman
Are these accurate? What's the reasoning behind optimal ratios?""",

        """3. MYTHIC GEAR PRIORITY: For a medium spender, what's the optimal order to give mythic gear to heroes? I currently have: Natalia, Alonso, Molly, Jeronimo, Flint. Should mythic go to Natalia first since she's the tank, or Alonso for damage?""",

        """4. JESSIE & SERGEY JOINER ROLES: I've read that Jessie is the best attack/rally joiner and Sergey is best for garrison joining due to their expedition skills. Can you explain exactly WHY and what their expedition skills do that makes them special joiners? Are there other heroes with similar joiner value?""",

        """5. GENERATION PROGRESSION: How does the meta shift from Gen 3-4 servers to Gen 7+ servers? Which early heroes remain relevant and which get power-crept? Specifically concerned about Jeronimo, Natalia, Alonso, and Molly longevity.""",

        """6. PETS & LINEUPS: How do pets factor into lineup decisions in WoS? Are there specific pet + hero combinations that are particularly strong? Should pet choice influence which heroes you run?"""
    ]

    print("=" * 80)
    print("WHITEOUT SURVIVAL - OPENAI KNOWLEDGE CHECK")
    print("=" * 80)

    results = {}

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}")
        print("="*80)
        print(question[:100] + "..." if len(question) > 100 else question)
        print("-"*80)

        try:
            answer = ask_wos_question(question)
            print(answer)
            results[f"q{i}"] = {"question": question, "answer": answer}
        except Exception as e:
            print(f"ERROR: {e}")
            results[f"q{i}"] = {"question": question, "error": str(e)}

    # Save results to file
    with open("data/openai_wos_knowledge.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("Results saved to data/openai_wos_knowledge.json")
    print("="*80)

if __name__ == "__main__":
    main()
