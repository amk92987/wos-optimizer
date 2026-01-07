"""
Strict OpenAI queries - no hallucination allowed.
"""

import os
import json
from openai import OpenAI

# Get API key
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    import subprocess
    result = subprocess.run(
        ['powershell', '-Command', "[Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')"],
        capture_output=True, text=True
    )
    api_key = result.stdout.strip()

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are an expert Whiteout Survival (WoS) mobile game advisor.

CRITICAL RULES:
1. ONLY provide information you are CERTAIN is accurate about WoS
2. If you don't know something specific, say "I don't have verified information on this"
3. DO NOT make up skill names, percentages, or mechanics
4. DO NOT invent hero abilities or synergies
5. If asked about specific skill effects, admit if you don't know the exact numbers

Real WoS heroes by generation (DO NOT reference any other heroes):
- Gen 1: Jeronimo, Natalia, Molly, Zinman, Sergey, Gina, Bahiti
- Gen 2: Flint, Philly, Alonso
- Gen 3: Logan, Mia, Greg
- Gen 4: Ahmose, Reina, Lynn
- Gen 5: Hector, Wu Ming, Jessie
- Gen 6: Patrick, Charlie, Cloris
- Gen 7: Gordon, Renee, Eugene
- Gen 8+: Blanchette, Nora

Key verified mechanics:
- World marches = 3 heroes (1 per class: Infantry, Lancer, Marksman)
- Arena = 5 heroes
- Rally = Rally leader (3 heroes) + up to 6 joiners (3 heroes each)
- Expedition Skills = PvP skills
- Exploration Skills = PvE skills
- Lead hero position applies full expedition skill effects

Be honest about the limits of your knowledge."""

def ask_wos_question(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message.content

def main():
    questions = [
        """Be completely honest: What do you ACTUALLY know with certainty about Jessie's expedition skills in WoS? If you don't know specific percentages or exact skill names, say so. What makes players consider her a good rally joiner?""",

        """Be completely honest: What do you ACTUALLY know with certainty about Jeronimo's role in WoS? Why do some guides recommend him as rally leader? What are the actual known facts about his skills?""",

        """For troop ratios in WoS, what is actually KNOWN versus what is speculation?
- What's the general consensus on attack ratios?
- What's the logic behind having more Infantry vs more Marksman?
- Are there official sources or is this all player-derived?""",

        """What is the verified meta consensus for these scenarios (only state what you're confident about):
1. Best Infantry hero for early-mid game
2. Best Marksman for damage
3. Best Lancer for support/healing
4. Most gear-dependent hero type""",

        """What should a medium spender on a Gen 4 server (day 200-280) prioritize? Only provide advice you're confident about. Acknowledge uncertainty where it exists."""
    ]

    print("=" * 80)
    print("WHITEOUT SURVIVAL - STRICT NO-HALLUCINATION QUERIES")
    print("=" * 80)

    results = {}

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}")
        print("="*80)
        print(question[:150] + "..." if len(question) > 150 else question)
        print("-"*80)

        try:
            answer = ask_wos_question(question)
            print(answer)
            results[f"q{i}"] = {"question": question, "answer": answer}
        except Exception as e:
            print(f"ERROR: {e}")
            results[f"q{i}"] = {"question": question, "error": str(e)}

    # Save results
    with open("data/openai_wos_strict.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("Results saved to data/openai_wos_strict.json")
    print("="*80)

if __name__ == "__main__":
    main()
