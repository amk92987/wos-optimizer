"""
Follow-up OpenAI queries with specific WoS hero names.
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

SYSTEM_PROMPT = """You are an expert Whiteout Survival (WoS) player.

IMPORTANT: Only use REAL hero names from the game. Here are the actual heroes by generation:
- Gen 1: Jeronimo (Infantry), Natalia (Infantry), Molly (Lancer), Zinman (Lancer), Sergey (Infantry), Gina (Marksman), Bahiti (Lancer), Jessie (Marksman)
- Gen 2: Flint (Infantry), Philly (Marksman), Alonso (Marksman)
- Gen 3: Logan (Marksman), Mia (Marksman), Greg (Infantry)
- Gen 4: Ahmose (Infantry), Reina (Lancer), Lynn (Marksman)
- Gen 5: Hector (Lancer), Wu Ming (Infantry)
- Gen 6: Patrick (Lancer), Charlie (Marksman), Cloris (Lancer)
- Gen 7: Gordon (Infantry), Renee (Marksman), Eugene (Lancer)
- Gen 8+: Blanchette (Lancer), Nora, and newer heroes

Each hero has TWO skill types:
- Expedition Skills: Apply in PvP (SvS, rallies, garrison)
- Exploration Skills: Apply in PvE (frozen stages, exploration)

DO NOT make up hero names. Only reference the heroes listed above."""

def ask_wos_question(question: str) -> str:
    """Ask OpenAI a WoS-related question."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        temperature=0.5,
        max_tokens=1500
    )
    return response.choices[0].message.content

def main():
    questions = [
        """Using ONLY the real WoS heroes I listed, what are the best 3-hero combinations for:
1. SvS Castle Attack (as rally leader)
2. SvS Castle Defense (garrison)
3. Bear Trap Rally (leader)
Explain WHY these specific heroes work together based on their actual expedition skills.""",

        """For the real WoS heroes: Jeronimo, Natalia, Alonso, Molly, and Flint - what is the correct mythic gear priority order and why? Consider:
- Who benefits most from the stat increases?
- Which hero's performance is most gear-dependent?
- What's the diminishing returns situation?""",

        """Explain Jessie's actual expedition skills and why she's considered the best attack/rally joiner in WoS. Then explain Sergey's expedition skills and why he's best for garrison joining. Be specific about the skill effects.""",

        """For a Gen 4-5 server (around day 200-360), what's the optimal hero investment priority assuming you have access to:
- Gen 1: Jeronimo, Natalia, Molly, Zinman, Sergey, Bahiti
- Gen 2: Flint, Philly, Alonso
- Gen 3: Logan, Mia, Greg
- Gen 4: Ahmose
Which heroes should get resources first? Which are "good enough" at lower investment?""",

        """What specific synergies exist between these real WoS hero combinations:
1. Jeronimo (lead) + Molly + Alonso
2. Natalia (lead) + Molly + Alonso
3. Natalia (lead) + Zinman + Philly
How do their expedition skills interact when in the same march?"""
    ]

    print("=" * 80)
    print("WHITEOUT SURVIVAL - TARGETED FOLLOW-UP QUERIES")
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
    with open("data/openai_wos_followup.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("Results saved to data/openai_wos_followup.json")
    print("="*80)

if __name__ == "__main__":
    main()
