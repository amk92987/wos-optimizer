"""Update lineup test results with Claude Code's direct answers."""
import json
from database.db import get_db, init_db
from database.models import LineupTestResult

init_db()
db = get_db()

# Claude's lineup recommendations for each result
claude_answers = {
    # Result 10: Gen2_Early, bear_trap
    10: {
        "lineup": [
            {"slot": 1, "hero": "Philly", "reason": "Only Marksman in roster - critical for Bear Trap as bear is slow and ranged DPS is king"},
            {"slot": 2, "hero": "Natalia", "reason": "Highest level hero (35) provides strong frontline protection for Philly"},
            {"slot": 3, "hero": "Jeronimo", "reason": "S+ tier Infantry, essential tank to keep bear occupied"},
            {"slot": 4, "hero": "Jessie", "reason": "Lancer provides balanced damage and her expedition skill adds value"},
            {"slot": 5, "hero": "Molly", "reason": "Second Lancer for additional damage support"}
        ],
        "reasoning": "This roster is weak for Bear Trap with only 1 Marksman. Optimal strategy: protect Philly at all costs. Troop ratio should be shifted toward Marksman (0/10/90) but hero lineup must compensate with strong Infantry frontline since Philly is underleveled.",
        "troop_ratio": "0/10/90"
    },

    # Result 11: Gen2_Early, garrison_joiner
    11: {
        "lineup": [
            {"slot": 1, "hero": "Sergey", "reason": "CRITICAL: Defenders' Edge skill reduces damage taken by up to 20% - MUST be slot 1 for garrison defense"},
            {"slot": 2, "hero": "Natalia", "reason": "Highest level Infantry (35) for maximum durability"},
            {"slot": 3, "hero": "Jeronimo", "reason": "S+ tier Infantry, excellent tank for sustained defense"},
            {"slot": 4, "hero": "Zinman", "reason": "Additional Infantry depth for garrison defense"},
            {"slot": 5, "hero": "Jessie", "reason": "Lancer provides some damage while maintaining survivability"}
        ],
        "reasoning": "Garrison defense requires damage mitigation. Sergey's Defenders' Edge in slot 1 is non-negotiable. Stack Infantry for survivability. This roster has 4 Infantry which is good for defense.",
        "troop_ratio": "50/30/20"
    },

    # Result 12: Gen2_Early, rally_joiner
    12: {
        "lineup": [
            {"slot": 1, "hero": "Jessie", "reason": "CRITICAL: Stand of Arms skill gives +5-25% DMG dealt - MUST be slot 1 for attack rallies"},
            {"slot": 2, "hero": "Natalia", "reason": "Highest level hero (35), provides frontline strength"},
            {"slot": 3, "hero": "Jeronimo", "reason": "S+ tier Infantry for rally durability"},
            {"slot": 4, "hero": "Philly", "reason": "Only Marksman, adds ranged DPS to the rally"},
            {"slot": 5, "hero": "Sergey", "reason": "Additional Infantry support"}
        ],
        "reasoning": "Rally joining prioritizes slot 1 expedition skill. Jessie's damage boost is the best attack option in this roster. Fill remaining slots with highest power heroes regardless of class since rally leader sets the composition.",
        "troop_ratio": "30/20/50"
    },

    # Result 13: Levels_AllLow, bear_trap
    13: {
        "lineup": [
            {"slot": 1, "hero": "Hendrik", "reason": "S tier Marksman - best ranged DPS option for slow bear target"},
            {"slot": 2, "hero": "Jeronimo", "reason": "S+ tier Infantry tank to protect Marksmen"},
            {"slot": 3, "hero": "Wu Ming", "reason": "S+ tier Infantry for additional frontline strength"},
            {"slot": 4, "hero": "Gordon", "reason": "S tier Lancer provides good damage and survivability"},
            {"slot": 5, "hero": "Jessie", "reason": "Lancer with valuable expedition skill"}
        ],
        "reasoning": "Only 1 Marksman (Hendrik) in roster limits Bear Trap effectiveness. Must maximize Hendrik's damage while keeping him alive. Strong Infantry frontline is essential. All heroes at same level (30), so prioritize tier rating.",
        "troop_ratio": "0/10/90"
    },

    # Result 14: Levels_AllLow, garrison_joiner
    14: {
        "lineup": [
            {"slot": 1, "hero": "Sergey", "reason": "Defenders' Edge -4-20% DMG taken is BEST defensive expedition skill - MUST be slot 1"},
            {"slot": 2, "hero": "Jeronimo", "reason": "S+ tier Infantry for maximum tankiness"},
            {"slot": 3, "hero": "Wu Ming", "reason": "S+ tier Infantry, excellent defensive stats"},
            {"slot": 4, "hero": "Ahmose", "reason": "A tier Infantry adds defensive depth"},
            {"slot": 5, "hero": "Hector", "reason": "Additional Infantry for garrison survivability"}
        ],
        "reasoning": "Garrison defense stacking: Sergey slot 1 for damage reduction, then fill with best Infantry. This roster has 7 Infantry which is excellent for defense. All levels equal so tier matters most.",
        "troop_ratio": "60/25/15"
    },

    # Result 15: Levels_AllLow, rally_joiner
    15: {
        "lineup": [
            {"slot": 1, "hero": "Jessie", "reason": "Stand of Arms +5-25% DMG dealt - BEST attack expedition skill, MUST be slot 1"},
            {"slot": 2, "hero": "Jeronimo", "reason": "S+ tier Infantry provides rally durability"},
            {"slot": 3, "hero": "Wu Ming", "reason": "S+ tier Infantry for frontline strength"},
            {"slot": 4, "hero": "Gordon", "reason": "S tier Lancer adds damage balance"},
            {"slot": 5, "hero": "Hendrik", "reason": "S tier Marksman for ranged DPS"}
        ],
        "reasoning": "Rally attack joining: Jessie slot 1 is critical for damage boost. Then pick highest tier heroes to maximize rally contribution. Mix of classes since rally leader determines optimal composition.",
        "troop_ratio": "30/20/50"
    },

    # Result 16: Gear_None, bear_trap
    16: {
        "lineup": [
            {"slot": 1, "hero": "Hendrik", "reason": "S tier Marksman - critical for Bear Trap ranged DPS"},
            {"slot": 2, "hero": "Jeronimo", "reason": "S+ tier Infantry tank to protect backline"},
            {"slot": 3, "hero": "Wu Ming", "reason": "S+ tier Infantry for sustained frontline"},
            {"slot": 4, "hero": "Gordon", "reason": "S tier Lancer for damage support"},
            {"slot": 5, "hero": "Logan", "reason": "A tier Lancer, adds survivability"}
        ],
        "reasoning": "High level roster (60) with 4 stars but only 1 Marksman limits Bear Trap potential. Hendrik must survive to maximize damage. Strong Infantry wall essential. No gear means hero tier and level are primary factors.",
        "troop_ratio": "0/10/90"
    },

    # Result 17: Gear_None, garrison_joiner
    17: {
        "lineup": [
            {"slot": 1, "hero": "Sergey", "reason": "Defenders' Edge expedition skill is ESSENTIAL for garrison defense - MUST be slot 1"},
            {"slot": 2, "hero": "Jeronimo", "reason": "S+ tier Infantry, best tank available"},
            {"slot": 3, "hero": "Wu Ming", "reason": "S+ tier Infantry for defensive strength"},
            {"slot": 4, "hero": "Zinman", "reason": "Infantry depth for garrison survivability"},
            {"slot": 5, "hero": "Ahmose", "reason": "A tier Infantry rounds out defensive lineup"}
        ],
        "reasoning": "Garrison defense is Infantry-heavy strategy. Sergey slot 1 for damage mitigation buff. At level 60 with no gear, hero tier determines effectiveness. Stack S+/A tier Infantry.",
        "troop_ratio": "60/25/15"
    },

    # Result 18: Gear_None, rally_joiner
    18: {
        "lineup": [
            {"slot": 1, "hero": "Jessie", "reason": "Stand of Arms +25% DMG at max skill - BEST attack joiner, MUST be slot 1"},
            {"slot": 2, "hero": "Jeronimo", "reason": "S+ tier Infantry provides rally staying power"},
            {"slot": 3, "hero": "Wu Ming", "reason": "S+ tier Infantry for frontline support"},
            {"slot": 4, "hero": "Gordon", "reason": "S tier Lancer adds balanced damage"},
            {"slot": 5, "hero": "Hendrik", "reason": "S tier Marksman for ranged contribution"}
        ],
        "reasoning": "Attack rally joining: Jessie slot 1 non-negotiable for damage buff. Fill with highest tier heroes. Class mix is acceptable since rally leader optimizes troop composition. Level 60/4 star heroes are strong contribution.",
        "troop_ratio": "30/20/50"
    }
}

# Update each result with Claude's answers
for result_id, answer in claude_answers.items():
    result = db.query(LineupTestResult).filter(LineupTestResult.id == result_id).first()
    if result:
        result.claude_lineup = json.dumps(answer["lineup"])
        result.claude_reasoning = answer["reasoning"]
        result.claude_raw_response = json.dumps({
            "lineup": answer["lineup"],
            "reasoning": answer["reasoning"],
            "troop_ratio": answer["troop_ratio"],
            "source": "Claude Code direct answer (no API)"
        })
        print(f"Updated result {result_id}: {result.profile_name} / {result.scenario}")
    else:
        print(f"Result {result_id} not found!")

db.commit()
print("\nAll 9 results updated with Claude answers!")
