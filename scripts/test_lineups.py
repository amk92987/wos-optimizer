#!/usr/bin/env python3
"""
Lineup Engine Test Suite
========================

Comprehensive testing of the lineup recommendation engine by comparing
our rule-based engine against OpenAI and Claude AI recommendations.

COST TRACKING:
- All API calls are logged with token counts
- Estimated costs are calculated and displayed
- Raw responses are stored for debugging

PHASES:
1. Generate test profiles with varied characteristics
2. Run our lineup engine on each profile + scenario
3. Query OpenAI and Claude for their recommendations
4. Compare results and calculate match scores
5. Generate discrepancy report
6. (Optional) Get AI suggestions for engine improvements

Usage:
    python scripts/test_lineups.py --run-all
    python scripts/test_lineups.py --profile-group generation
    python scripts/test_lineups.py --analyze-run 1
    python scripts/test_lineups.py --suggest-improvements 1
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import (
    Hero, LineupTestRun, LineupTestResult, LineupEngineImprovement
)

# Initialize database
init_db()

# =============================================================================
# CONFIGURATION
# =============================================================================

# OpenAI pricing (as of Jan 2025)
OPENAI_PRICING = {
    'gpt-4o': {'input': 5.00 / 1_000_000, 'output': 15.00 / 1_000_000},
    'gpt-4o-mini': {'input': 0.15 / 1_000_000, 'output': 0.60 / 1_000_000},
}

# Scenarios to test
SCENARIOS = [
    'bear_trap',
    'crazy_joe',
    'garrison_defense',
    'garrison_joiner',
    'rally_lead',
    'rally_joiner',
    'svs_march',
    'alliance_championship',
    'polar_terror',
    'capital_clash',
]

# Scenarios where slot 1 (leftmost hero) matters
SLOT_ORDER_MATTERS = ['garrison_joiner', 'rally_lead', 'rally_joiner']

# Quality levels for gear
QUALITY_NAMES = {0: 'None', 1: 'Gray', 2: 'Green', 3: 'Blue', 4: 'Purple', 5: 'Gold', 6: 'Orange', 7: 'Mythic'}

# =============================================================================
# TEST PROFILE DEFINITIONS
# =============================================================================

def get_test_profiles():
    """
    Generate test profile configurations.

    Returns a list of profile configs that will be used to create
    synthetic test data for lineup testing.

    Groups:
    - A: Generation baseline (2 per gen)
    - B: Level impact (same roster, different levels)
    - C: Hero gear impact (same roster, different gear)
    - D: Chief gear impact
    - E: Charm impact
    - F: Edge cases
    """
    profiles = []

    # =========================================================================
    # GROUP A: Generation Baseline (14 profiles)
    # =========================================================================
    generation_profiles = [
        # Gen 2 - Very early game
        {'name': 'Gen2_Early', 'group': 'generation', 'gen': 2,
         'heroes': [
             {'name': 'Jessie', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Molly', 'level': 25, 'stars': 0, 'gear_quality': 2},
             {'name': 'Natalia', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Jeronimo', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Zinman', 'level': 20, 'stars': 0, 'gear_quality': 1},
             {'name': 'Sergey', 'level': 25, 'stars': 0, 'gear_quality': 2},
             {'name': 'Flint', 'level': 20, 'stars': 0, 'gear_quality': 1},
             {'name': 'Philly', 'level': 15, 'stars': 0, 'gear_quality': 1},
         ],
         'chief_gear_quality': 2, 'charm_level': 0},

        {'name': 'Gen2_Developed', 'group': 'generation', 'gen': 2,
         'heroes': [
             {'name': 'Jessie', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Molly', 'level': 45, 'stars': 2, 'gear_quality': 4},
             {'name': 'Natalia', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Jeronimo', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Zinman', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Sergey', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Flint', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Philly', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Alonso', 'level': 30, 'stars': 1, 'gear_quality': 2},
         ],
         'chief_gear_quality': 3, 'charm_level': 3},

        # Gen 4
        {'name': 'Gen4_Early', 'group': 'generation', 'gen': 4,
         'heroes': [
             {'name': 'Jessie', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Natalia', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Jeronimo', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Zinman', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Sergey', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Flint', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Logan', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Mia', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Ahmose', 'level': 25, 'stars': 0, 'gear_quality': 2},
             {'name': 'Reina', 'level': 20, 'stars': 0, 'gear_quality': 1},
         ],
         'chief_gear_quality': 3, 'charm_level': 3},

        {'name': 'Gen4_Developed', 'group': 'generation', 'gen': 4,
         'heroes': [
             {'name': 'Jessie', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Natalia', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Jeronimo', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Zinman', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Sergey', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Flint', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Logan', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Mia', 'level': 45, 'stars': 2, 'gear_quality': 4},
             {'name': 'Ahmose', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Reina', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Lynn', 'level': 35, 'stars': 1, 'gear_quality': 3},
         ],
         'chief_gear_quality': 4, 'charm_level': 6},

        # Gen 6
        {'name': 'Gen6_Early', 'group': 'generation', 'gen': 6,
         'heroes': [
             {'name': 'Jessie', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Natalia', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Jeronimo', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Zinman', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Sergey', 'level': 45, 'stars': 2, 'gear_quality': 4},
             {'name': 'Logan', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Ahmose', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Reina', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Wu Ming', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Hector', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Norah', 'level': 25, 'stars': 0, 'gear_quality': 2},
             {'name': 'Wayne', 'level': 20, 'stars': 0, 'gear_quality': 1},
         ],
         'chief_gear_quality': 4, 'charm_level': 5},

        {'name': 'Gen6_Developed', 'group': 'generation', 'gen': 6,
         'heroes': [
             {'name': 'Jessie', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Natalia', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Jeronimo', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Zinman', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Sergey', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Logan', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Ahmose', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Reina', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Wu Ming', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Hector', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Norah', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Wayne', 'level': 45, 'stars': 2, 'gear_quality': 3},
         ],
         'chief_gear_quality': 5, 'charm_level': 10},

        # Gen 8
        {'name': 'Gen8_Early', 'group': 'generation', 'gen': 8,
         'heroes': [
             {'name': 'Natalia', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Jeronimo', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Jessie', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Zinman', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Sergey', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Logan', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Ahmose', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Wu Ming', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Hector', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Norah', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Gordon', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Renee', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Edith', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Gatot', 'level': 25, 'stars': 0, 'gear_quality': 2},
         ],
         'chief_gear_quality': 4, 'charm_level': 6},

        {'name': 'Gen8_Developed', 'group': 'generation', 'gen': 8,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Jeronimo', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Jessie', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Zinman', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Sergey', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Logan', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Ahmose', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Wu Ming', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Hector', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Norah', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Gordon', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Renee', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Edith', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Gatot', 'level': 50, 'stars': 3, 'gear_quality': 4},
         ],
         'chief_gear_quality': 5, 'charm_level': 12},

        # Gen 10
        {'name': 'Gen10_Early', 'group': 'generation', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Jeronimo', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Jessie', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Zinman', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Sergey', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Logan', 'level': 60, 'stars': 4, 'gear_quality': 5},
             {'name': 'Ahmose', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Wu Ming', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Hector', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Gordon', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Edith', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Gatot', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Henrik', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Gwen', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Tristan', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Ling', 'level': 25, 'stars': 0, 'gear_quality': 2},
         ],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Gen10_Developed', 'group': 'generation', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Jeronimo', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Zinman', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Sergey', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Logan', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Ahmose', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Wu Ming', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Hector', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Gordon', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Edith', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Gatot', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Henrik', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Gwen', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Tristan', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Ling', 'level': 50, 'stars': 3, 'gear_quality': 4},
         ],
         'chief_gear_quality': 6, 'charm_level': 14},

        # Gen 12
        {'name': 'Gen12_Early', 'group': 'generation', 'gen': 12,
         'heroes': [
             {'name': 'Natalia', 'level': 75, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Jeronimo', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Jessie', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Zinman', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Logan', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Ahmose', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Wu Ming', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Hector', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Gordon', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Henrik', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Tristan', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Ling', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Kazuki', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Sofia', 'level': 35, 'stars': 1, 'gear_quality': 3},
             {'name': 'Bjorn', 'level': 30, 'stars': 1, 'gear_quality': 2},
             {'name': 'Yuki', 'level': 25, 'stars': 0, 'gear_quality': 2},
         ],
         'chief_gear_quality': 5, 'charm_level': 10},

        {'name': 'Gen12_Developed', 'group': 'generation', 'gen': 12,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 7, 'mythic': True},
             {'name': 'Jeronimo', 'level': 80, 'stars': 5, 'gear_quality': 7, 'mythic': True},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Zinman', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Logan', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Ahmose', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Wu Ming', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Hector', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Gordon', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Henrik', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Tristan', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Ling', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Kazuki', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Sofia', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Bjorn', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Yuki', 'level': 55, 'stars': 3, 'gear_quality': 4},
         ],
         'chief_gear_quality': 6, 'charm_level': 16},

        # Gen 14
        {'name': 'Gen14_Early', 'group': 'generation', 'gen': 14,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Jeronimo', 'level': 75, 'stars': 5, 'gear_quality': 6},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Zinman', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Logan', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Wu Ming', 'level': 65, 'stars': 4, 'gear_quality': 5},
             {'name': 'Hector', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Gordon', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Henrik', 'level': 60, 'stars': 4, 'gear_quality': 4},
             {'name': 'Tristan', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Kazuki', 'level': 55, 'stars': 3, 'gear_quality': 4},
             {'name': 'Bjorn', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Magnus', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Chen', 'level': 35, 'stars': 1, 'gear_quality': 2},
         ],
         'chief_gear_quality': 6, 'charm_level': 12},

        {'name': 'Gen14_Developed', 'group': 'generation', 'gen': 14,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 7, 'mythic': True},
             {'name': 'Jeronimo', 'level': 80, 'stars': 5, 'gear_quality': 7, 'mythic': True},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 7},
             {'name': 'Zinman', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Logan', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Wu Ming', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Hector', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Gordon', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Henrik', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Tristan', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Kazuki', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Bjorn', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Magnus', 'level': 65, 'stars': 4, 'gear_quality': 4},
             {'name': 'Chen', 'level': 60, 'stars': 4, 'gear_quality': 4},
         ],
         'chief_gear_quality': 7, 'charm_level': 16},
    ]
    profiles.extend(generation_profiles)

    # =========================================================================
    # GROUP B: Level Impact (6 profiles)
    # Same Gen 10 roster with different level distributions
    # =========================================================================
    base_roster = ['Natalia', 'Jeronimo', 'Jessie', 'Zinman', 'Sergey',
                   'Logan', 'Ahmose', 'Wu Ming', 'Hector', 'Gordon',
                   'Henrik', 'Tristan']

    level_profiles = [
        {'name': 'Levels_AllLow', 'group': 'level_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 30, 'stars': 1, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Levels_AllMid', 'group': 'level_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 50, 'stars': 3, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Levels_AllHigh', 'group': 'level_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 70, 'stars': 5, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Levels_MetaHigh', 'group': 'level_impact', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Jeronimo', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 4},
         ] + [{'name': h, 'level': 30, 'stars': 1, 'gear_quality': 4}
              for h in base_roster if h not in ['Natalia', 'Jeronimo', 'Jessie']],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Levels_NonMetaHigh', 'group': 'level_impact', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 30, 'stars': 1, 'gear_quality': 4},
             {'name': 'Jeronimo', 'level': 30, 'stars': 1, 'gear_quality': 4},
             {'name': 'Jessie', 'level': 30, 'stars': 1, 'gear_quality': 4},
             {'name': 'Sergey', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Logan', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Ahmose', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Hector', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Gordon', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Henrik', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Zinman', 'level': 30, 'stars': 1, 'gear_quality': 4},
             {'name': 'Wu Ming', 'level': 30, 'stars': 1, 'gear_quality': 4},
             {'name': 'Tristan', 'level': 30, 'stars': 1, 'gear_quality': 4},
         ],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Levels_Top5Max', 'group': 'level_impact', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Jeronimo', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Zinman', 'level': 80, 'stars': 5, 'gear_quality': 4},
             {'name': 'Logan', 'level': 80, 'stars': 5, 'gear_quality': 4},
         ] + [{'name': h, 'level': 40, 'stars': 2, 'gear_quality': 4}
              for h in base_roster if h not in ['Natalia', 'Jeronimo', 'Jessie', 'Zinman', 'Logan']],
         'chief_gear_quality': 5, 'charm_level': 8},
    ]
    profiles.extend(level_profiles)

    # =========================================================================
    # GROUP C: Hero Gear Impact (6 profiles)
    # Same Gen 10 roster, same levels, different gear
    # =========================================================================
    gear_profiles = [
        {'name': 'Gear_None', 'group': 'gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 0} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Gear_AllBlue', 'group': 'gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 3} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Gear_AllPurple', 'group': 'gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Gear_AllGold', 'group': 'gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 5} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Gear_MythicOnMeta', 'group': 'gear_impact', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 60, 'stars': 4, 'gear_quality': 5, 'mythic': True},
             {'name': 'Jeronimo', 'level': 60, 'stars': 4, 'gear_quality': 5, 'mythic': True},
             {'name': 'Jessie', 'level': 60, 'stars': 4, 'gear_quality': 5, 'mythic': True},
         ] + [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4}
              for h in base_roster if h not in ['Natalia', 'Jeronimo', 'Jessie']],
         'chief_gear_quality': 5, 'charm_level': 8},

        {'name': 'Gear_AllMythic', 'group': 'gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 6, 'mythic': True} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 8},
    ]
    profiles.extend(gear_profiles)

    # =========================================================================
    # GROUP D: Chief Gear Impact (4 profiles)
    # =========================================================================
    chief_gear_profiles = [
        {'name': 'ChiefGear_Gray', 'group': 'chief_gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 1, 'charm_level': 0},

        {'name': 'ChiefGear_Blue', 'group': 'chief_gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 3, 'charm_level': 0},

        {'name': 'ChiefGear_Purple', 'group': 'chief_gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 4, 'charm_level': 0},

        {'name': 'ChiefGear_Gold', 'group': 'chief_gear_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 0},
    ]
    profiles.extend(chief_gear_profiles)

    # =========================================================================
    # GROUP E: Charm Impact (4 profiles)
    # =========================================================================
    charm_profiles = [
        {'name': 'Charms_None', 'group': 'charm_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 0},

        {'name': 'Charms_Level5', 'group': 'charm_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 5},

        {'name': 'Charms_Level10', 'group': 'charm_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 10},

        {'name': 'Charms_Level16', 'group': 'charm_impact', 'gen': 10,
         'heroes': [{'name': h, 'level': 60, 'stars': 4, 'gear_quality': 4} for h in base_roster],
         'chief_gear_quality': 5, 'charm_level': 16},
    ]
    profiles.extend(charm_profiles)

    # =========================================================================
    # GROUP F: Edge Cases (5 profiles)
    # =========================================================================
    edge_profiles = [
        # All infantry focus
        {'name': 'Edge_InfantryFocus', 'group': 'edge_case', 'gen': 10,
         'heroes': [
             {'name': 'Jeronimo', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Zinman', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Ahmose', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Hector', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Natalia', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Jessie', 'level': 40, 'stars': 2, 'gear_quality': 3},
         ],
         'chief_gear_quality': 5, 'charm_level': 10},

        # All marksman focus
        {'name': 'Edge_MarksmanFocus', 'group': 'edge_case', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Jessie', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Logan', 'level': 75, 'stars': 5, 'gear_quality': 5},
             {'name': 'Gordon', 'level': 70, 'stars': 5, 'gear_quality': 5},
             {'name': 'Jeronimo', 'level': 40, 'stars': 2, 'gear_quality': 3},
             {'name': 'Zinman', 'level': 40, 'stars': 2, 'gear_quality': 3},
         ],
         'chief_gear_quality': 5, 'charm_level': 10},

        # Very few heroes (new player)
        {'name': 'Edge_FewHeroes', 'group': 'edge_case', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 50, 'stars': 3, 'gear_quality': 4},
             {'name': 'Jessie', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Jeronimo', 'level': 45, 'stars': 2, 'gear_quality': 3},
             {'name': 'Sergey', 'level': 30, 'stars': 1, 'gear_quality': 2},
         ],
         'chief_gear_quality': 3, 'charm_level': 2},

        # Spread thin (all heroes equal investment)
        {'name': 'Edge_SpreadThin', 'group': 'edge_case', 'gen': 10,
         'heroes': [{'name': h, 'level': 45, 'stars': 2, 'gear_quality': 3} for h in base_roster],
         'chief_gear_quality': 4, 'charm_level': 5},

        # Undergeared meta vs maxed non-meta
        {'name': 'Edge_UndergearedMeta', 'group': 'edge_case', 'gen': 10,
         'heroes': [
             {'name': 'Natalia', 'level': 40, 'stars': 2, 'gear_quality': 2},
             {'name': 'Jeronimo', 'level': 40, 'stars': 2, 'gear_quality': 2},
             {'name': 'Jessie', 'level': 40, 'stars': 2, 'gear_quality': 2},
             {'name': 'Sergey', 'level': 80, 'stars': 5, 'gear_quality': 6, 'mythic': True},
             {'name': 'Hector', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Gordon', 'level': 80, 'stars': 5, 'gear_quality': 6},
             {'name': 'Henrik', 'level': 80, 'stars': 5, 'gear_quality': 6},
         ],
         'chief_gear_quality': 5, 'charm_level': 10},
    ]
    profiles.extend(edge_profiles)

    return profiles


# =============================================================================
# SNAPSHOT GENERATION
# =============================================================================

def generate_profile_snapshot(profile_config: dict) -> dict:
    """
    Generate a complete profile snapshot for AI consumption.

    This creates the exact data structure that will be sent to OpenAI/Claude.
    """
    snapshot = {
        'profile_name': profile_config['name'],
        'generation': profile_config['gen'],
        'test_group': profile_config['group'],

        # Heroes with full details
        'heroes': [],

        # Chief gear (all slots same quality for simplicity)
        'chief_gear': {
            'helmet': {'quality': QUALITY_NAMES.get(profile_config['chief_gear_quality'], 'None')},
            'armor': {'quality': QUALITY_NAMES.get(profile_config['chief_gear_quality'], 'None')},
            'gloves': {'quality': QUALITY_NAMES.get(profile_config['chief_gear_quality'], 'None')},
            'boots': {'quality': QUALITY_NAMES.get(profile_config['chief_gear_quality'], 'None')},
            'ring': {'quality': QUALITY_NAMES.get(profile_config['chief_gear_quality'], 'None')},
            'amulet': {'quality': QUALITY_NAMES.get(profile_config['chief_gear_quality'], 'None')},
        },

        # Charms
        'charm_level': profile_config['charm_level'],
    }

    # Load hero reference data
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"
    with open(heroes_file, encoding='utf-8') as f:
        hero_data = json.load(f)

    hero_lookup = {h['name']: h for h in hero_data.get('heroes', [])}

    # Build hero list with details
    for hero_config in profile_config['heroes']:
        hero_name = hero_config['name']
        hero_ref = hero_lookup.get(hero_name, {})

        hero_entry = {
            'name': hero_name,
            'class': hero_ref.get('hero_class', 'Unknown'),
            'generation': hero_ref.get('generation', 1),
            'tier_overall': hero_ref.get('tier_overall', 'C'),
            'tier_expedition': hero_ref.get('tier_expedition', 'C'),
            'level': hero_config['level'],
            'stars': hero_config['stars'],
            'gear_quality': QUALITY_NAMES.get(hero_config['gear_quality'], 'None'),
            'has_mythic_gear': hero_config.get('mythic', False),

            # Skills (assume maxed for simplicity at high levels)
            'expedition_skills': {
                'skill_1': min(5, max(1, hero_config['level'] // 20)),
                'skill_2': min(5, max(1, hero_config['level'] // 20)),
                'skill_3': min(5, max(1, hero_config['level'] // 20)),
            }
        }
        snapshot['heroes'].append(hero_entry)

    return snapshot


# =============================================================================
# AI PROMPTS
# =============================================================================

def get_game_context_prompt() -> str:
    """
    Generate the game context dynamically from actual data files.
    NO hardcoded hero data - everything comes from heroes.json.
    """
    # Load actual hero data
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"
    with open(heroes_file, encoding='utf-8') as f:
        hero_data = json.load(f)

    # Build hero lists by class and tier from actual data
    heroes_by_class = {'Infantry': [], 'Lancer': [], 'Marksman': []}
    for h in hero_data.get('heroes', []):
        hero_class = h.get('hero_class', 'Unknown')
        if hero_class in heroes_by_class:
            heroes_by_class[hero_class].append({
                'name': h['name'],
                'tier': h.get('tier_overall', 'C'),
                'gen': h.get('generation', 1)
            })

    # Sort by tier (S+ > S > A > B > C > D)
    tier_order = {'S+': 0, 'S': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5}
    for class_name in heroes_by_class:
        heroes_by_class[class_name].sort(key=lambda x: tier_order.get(x['tier'], 5))

    # Format hero lists
    def format_heroes(hero_list, limit=8):
        return ', '.join([f"{h['name']}({h['tier']})" for h in hero_list[:limit]])

    infantry_list = format_heroes(heroes_by_class['Infantry'])
    lancer_list = format_heroes(heroes_by_class['Lancer'])
    marksman_list = format_heroes(heroes_by_class['Marksman'])

    return f"""# Whiteout Survival - Lineup Optimization

## Hero Classes
- **Infantry**: Frontline tanks, high HP, absorb damage
- **Lancer**: Balanced fighters, good damage and survivability
- **Marksman**: Ranged DPS, high damage but fragile

## Heroes by Class (from game data, sorted by tier)
**Infantry**: {infantry_list}
**Lancer**: {lancer_list}
**Marksman**: {marksman_list}

## Key Mechanics

### Rally/Garrison Joining (LEFTMOST hero matters!)
When joining, only the LEFTMOST hero's top-right expedition skill applies to the battle.
- For ATTACK joining: Put hero with damage buff skill in slot 1
- For DEFENSE joining: Put hero with damage reduction skill in slot 1

### Event Strategies

**Bear Trap**: Bear is SLOW. Use Marksman heroes + 0/10/90 troop ratio.
**Crazy Joe**: Joe attacks BACKLINE first. Use Infantry heroes + 90/10/0 ratio.
**Garrison Defense**: Infantry-heavy for survival. 60/25/15 ratio.
**Garrison Joiner**: Defense skill in slot 1. 50/30/20 ratio.
**Rally Joiner (Attack)**: Attack buff skill in slot 1. 30/20/50 ratio.
**SvS March**: Balanced composition. 40/20/40 ratio.
**Alliance Championship**: Need 3 separate 5-hero lineups.
**Polar Terror**: Single target DPS, Marksman-focused.
**Capital Clash**: Balanced like SvS. 40/20/40 ratio.

## Selection Priority
1. Match hero CLASS to event needs (Marksman for Bear Trap, Infantry for Crazy Joe)
2. Higher TIER heroes are generally better (S+ > S > A > B > C > D)
3. Higher LEVEL/GEAR heroes outperform lower ones of same tier
4. For joining scenarios, slot 1 hero's expedition skill is critical

## IMPORTANT
Use the hero CLASS listed in the profile data. Each hero shows: Name (Class, Gen, Tier)
"""


def get_scenario_prompt(scenario: str) -> str:
    """Get specific prompt for a scenario."""
    prompts = {
        'bear_trap': "Build the optimal lineup for BEAR TRAP event. Bear is slow, maximize Marksman DPS.",
        'crazy_joe': "Build the optimal lineup for CRAZY JOE event. Joe attacks backline, need Infantry.",
        'garrison_defense': "Build the optimal lineup for GARRISON DEFENSE. You're defending your city.",
        'garrison_joiner': "Build the optimal lineup for GARRISON JOINER (reinforcing ally). Leftmost hero's expedition skill matters!",
        'rally_lead': "Build the optimal lineup for RALLY LEAD. You're leading the rally attack.",
        'rally_joiner': "Build the optimal lineup for RALLY JOINER (attack). Leftmost hero's expedition skill matters!",
        'svs_march': "Build the optimal lineup for SVS MARCH (field battle).",
        'alliance_championship': "Build 3 optimal lineups for ALLIANCE CHAMPIONSHIP (need 15 heroes across 3 teams).",
        'polar_terror': "Build the optimal lineup for POLAR TERROR boss fight.",
        'capital_clash': "Build the optimal lineup for CAPITAL CLASH large-scale war.",
    }
    return prompts.get(scenario, f"Build the optimal lineup for {scenario}.")


def build_ai_prompt(snapshot: dict, scenario: str) -> str:
    """Build the complete prompt for AI."""
    heroes_text = "\n".join([
        f"- {h['name']} ({h['class']}, Gen {h['generation']}, Tier {h['tier_overall']}): "
        f"Level {h['level']}, {h['stars']} stars, {h['gear_quality']} gear"
        f"{', MYTHIC' if h['has_mythic_gear'] else ''}"
        for h in snapshot['heroes']
    ])

    return f"""
{get_game_context_prompt()}

---

## Player Profile: {snapshot['profile_name']}

**Available Heroes:**
{heroes_text}

**Chief Gear:** All slots {snapshot['chief_gear']['helmet']['quality']} quality
**Charm Level:** {snapshot['charm_level']}

---

## Task: {get_scenario_prompt(scenario)}

Provide your recommendation in this EXACT format:

LINEUP:
1. [Hero Name] - [Reason for this slot]
2. [Hero Name] - [Reason]
3. [Hero Name] - [Reason]
4. [Hero Name] - [Reason]
5. [Hero Name] - [Reason]

TROOP_RATIO: [Infantry%]/[Lancer%]/[Marksman%]

REASONING:
[2-3 sentences explaining your overall strategy and why these heroes were chosen]
"""


# =============================================================================
# API CALLS
# =============================================================================

def call_openai(prompt: str, model: str = 'gpt-4o') -> dict:
    """
    Call OpenAI API and return structured response with token tracking.
    """
    import openai

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return {'error': 'OPENAI_API_KEY not set', 'tokens_input': 0, 'tokens_output': 0}

    client = openai.OpenAI(api_key=api_key)

    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Whiteout Survival expert helping optimize hero lineups."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent recommendations
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            'content': response.choices[0].message.content,
            'tokens_input': response.usage.prompt_tokens,
            'tokens_output': response.usage.completion_tokens,
            'model': model,
            'time_ms': elapsed_ms,
            'raw_response': response.model_dump_json(),
        }
    except Exception as e:
        return {
            'error': str(e),
            'tokens_input': 0,
            'tokens_output': 0,
            'time_ms': int((time.time() - start_time) * 1000),
        }


def call_claude(prompt: str, model: str = 'claude-sonnet-4-20250514') -> dict:
    """
    Call Claude API and return structured response.
    """
    import anthropic

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {'error': 'ANTHROPIC_API_KEY not set', 'tokens_input': 0, 'tokens_output': 0}

    client = anthropic.Anthropic(api_key=api_key)

    start_time = time.time()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are a Whiteout Survival expert helping optimize hero lineups.",
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            'content': response.content[0].text,
            'tokens_input': response.usage.input_tokens,
            'tokens_output': response.usage.output_tokens,
            'model': model,
            'time_ms': elapsed_ms,
            'raw_response': json.dumps({
                'id': response.id,
                'model': response.model,
                'usage': {'input_tokens': response.usage.input_tokens, 'output_tokens': response.usage.output_tokens}
            }),
        }
    except Exception as e:
        return {
            'error': str(e),
            'tokens_input': 0,
            'tokens_output': 0,
            'time_ms': int((time.time() - start_time) * 1000),
        }


# =============================================================================
# RESPONSE PARSING
# =============================================================================

def parse_ai_response(response_text: str) -> dict:
    """
    Parse AI response into structured lineup data.
    """
    result = {
        'lineup': [],
        'troop_ratio': None,
        'reasoning': None,
    }

    if not response_text:
        return result

    lines = response_text.strip().split('\n')

    # Parse lineup
    in_lineup = False
    for line in lines:
        line = line.strip()

        if line.startswith('LINEUP:'):
            in_lineup = True
            continue

        if line.startswith('TROOP_RATIO:'):
            in_lineup = False
            ratio_text = line.replace('TROOP_RATIO:', '').strip()
            result['troop_ratio'] = ratio_text
            continue

        if line.startswith('REASONING:'):
            in_lineup = False
            # Get everything after REASONING:
            reasoning_start = response_text.find('REASONING:')
            if reasoning_start != -1:
                result['reasoning'] = response_text[reasoning_start + 10:].strip()
            break

        if in_lineup and line and line[0].isdigit():
            # Parse "1. Hero Name - Reason"
            parts = line.split('.', 1)
            if len(parts) == 2:
                hero_part = parts[1].strip()
                if ' - ' in hero_part:
                    hero_name, reason = hero_part.split(' - ', 1)
                else:
                    hero_name = hero_part
                    reason = ''
                result['lineup'].append({
                    'slot': int(parts[0]),
                    'hero': hero_name.strip(),
                    'reason': reason.strip()
                })

    return result


# =============================================================================
# COMPARISON LOGIC
# =============================================================================

def calculate_match_score(lineup1: list, lineup2: list, scenario: str) -> dict:
    """
    Compare two lineups and return match metrics.
    """
    if not lineup1 or not lineup2:
        return {
            'score': 0.0,
            'hero_overlap': 0,
            'slot1_match': False,
        }

    # Extract hero names
    heroes1 = set(h['hero'] for h in lineup1)
    heroes2 = set(h['hero'] for h in lineup2)

    # Hero overlap
    overlap = len(heroes1 & heroes2)
    hero_score = overlap / max(len(heroes1), len(heroes2), 1)

    # Slot 1 match (for rally scenarios)
    slot1_match = False
    if lineup1 and lineup2:
        h1_slot1 = next((h['hero'] for h in lineup1 if h['slot'] == 1), None)
        h2_slot1 = next((h['hero'] for h in lineup2 if h['slot'] == 1), None)
        slot1_match = h1_slot1 == h2_slot1

    # Calculate final score
    if scenario in SLOT_ORDER_MATTERS:
        score = (hero_score * 0.7) + (0.3 if slot1_match else 0)
    else:
        score = hero_score

    return {
        'score': round(score, 3),
        'hero_overlap': overlap,
        'slot1_match': slot1_match,
    }


# =============================================================================
# MAIN RUNNER
# =============================================================================

def run_lineup_tests(
    profile_groups: list = None,
    scenarios: list = None,
    openai_model: str = 'gpt-4o',
    run_name: str = None,
    dry_run: bool = False,
    test_batch: bool = False,
    batch_size: int = 3,
) -> int:
    """
    Run the lineup test suite.

    Args:
        profile_groups: List of groups to test (e.g., ['generation', 'level_impact'])
        scenarios: List of scenarios to test (default: all)
        openai_model: OpenAI model to use
        run_name: Name for this test run
        dry_run: If True, don't make API calls, just show what would be tested
        test_batch: If True, only run a small batch for validation
        batch_size: Number of profiles to test in batch mode (default: 3)

    Returns:
        Test run ID
    """
    db = get_db()

    # Get profiles
    all_profiles = get_test_profiles()

    # Filter by group if specified
    if profile_groups:
        profiles = [p for p in all_profiles if p['group'] in profile_groups]
    else:
        profiles = all_profiles

    # For test batch, pick a diverse sample
    if test_batch:
        # Pick profiles from different groups for variety
        batch_profiles = []
        groups_seen = set()
        for p in profiles:
            if p['group'] not in groups_seen and len(batch_profiles) < batch_size:
                batch_profiles.append(p)
                groups_seen.add(p['group'])
        # Fill remaining with any profiles
        for p in profiles:
            if len(batch_profiles) >= batch_size:
                break
            if p not in batch_profiles:
                batch_profiles.append(p)
        profiles = batch_profiles
        print(f"\n*** TEST BATCH MODE: Running {len(profiles)} profiles only ***\n")

    # Filter scenarios
    test_scenarios = scenarios or SCENARIOS

    # For test batch, limit scenarios too
    if test_batch:
        # Pick key scenarios that cover different mechanics
        test_scenarios = ['bear_trap', 'garrison_joiner', 'rally_joiner'][:min(3, len(test_scenarios))]
        print(f"*** TEST BATCH MODE: Running {len(test_scenarios)} scenarios only ***\n")

    print(f"\n{'='*60}")
    print(f"LINEUP ENGINE TEST SUITE")
    print(f"{'='*60}")
    print(f"Profiles to test: {len(profiles)}")
    print(f"Scenarios per profile: {len(test_scenarios)}")
    print(f"Total comparisons: {len(profiles) * len(test_scenarios)}")
    print(f"OpenAI model: {openai_model}")

    # Estimate cost
    estimated_input_tokens = len(profiles) * len(test_scenarios) * 4000
    estimated_output_tokens = len(profiles) * len(test_scenarios) * 1500
    pricing = OPENAI_PRICING.get(openai_model, OPENAI_PRICING['gpt-4o'])
    estimated_cost = (estimated_input_tokens * pricing['input']) + (estimated_output_tokens * pricing['output'])
    print(f"\nEstimated OpenAI cost: ${estimated_cost:.2f}")
    print(f"(Claude is free on Max plan)")

    if dry_run:
        print("\n[DRY RUN - No API calls will be made]")
        print("\nProfiles that would be tested:")
        for p in profiles:
            print(f"  - {p['name']} ({p['group']}, Gen {p['gen']})")
        return 0

    # Create test run record
    test_run = LineupTestRun(
        name=run_name or f"Test Run {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        total_profiles=len(profiles),
        total_scenarios=len(test_scenarios),
        test_groups=json.dumps(list(set(p['group'] for p in profiles))),
        status='running',
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    print(f"\nTest Run ID: {test_run.id}")
    print(f"{'='*60}\n")

    total_openai_input = 0
    total_openai_output = 0
    results_count = 0

    try:
        for profile in profiles:
            print(f"\n[Profile: {profile['name']}]")
            snapshot = generate_profile_snapshot(profile)

            for scenario in test_scenarios:
                print(f"  Testing {scenario}...", end=' ', flush=True)

                # Build prompt
                prompt = build_ai_prompt(snapshot, scenario)

                # Call OpenAI
                openai_response = call_openai(prompt, openai_model)
                total_openai_input += openai_response.get('tokens_input', 0)
                total_openai_output += openai_response.get('tokens_output', 0)

                # Call Claude
                claude_response = call_claude(prompt)

                # Parse responses
                openai_parsed = parse_ai_response(openai_response.get('content', ''))
                claude_parsed = parse_ai_response(claude_response.get('content', ''))

                # TODO: Run our engine and compare
                engine_lineup = []  # Placeholder - integrate with actual engine

                # Calculate match scores
                openai_vs_claude = calculate_match_score(
                    openai_parsed['lineup'],
                    claude_parsed['lineup'],
                    scenario
                )

                # Store result
                result = LineupTestResult(
                    test_run_id=test_run.id,
                    profile_name=profile['name'],
                    profile_snapshot=json.dumps(snapshot),
                    generation=profile['gen'],
                    test_group=profile['group'],
                    scenario=scenario,

                    # TRAINING DATA: Store exact prompt sent
                    prompt_sent=prompt,

                    # Engine results (placeholder)
                    engine_lineup=json.dumps(engine_lineup),
                    engine_troop_ratio=None,
                    engine_reasoning=None,

                    # OpenAI results
                    openai_model=openai_model,
                    openai_lineup=json.dumps(openai_parsed['lineup']),
                    openai_troop_ratio=openai_parsed['troop_ratio'],
                    openai_reasoning=openai_parsed['reasoning'],
                    openai_tokens_input=openai_response.get('tokens_input'),
                    openai_tokens_output=openai_response.get('tokens_output'),
                    openai_time_ms=openai_response.get('time_ms'),
                    openai_raw_response=openai_response.get('raw_response'),

                    # Claude results
                    claude_model=claude_response.get('model', 'claude-sonnet-4-20250514'),
                    claude_lineup=json.dumps(claude_parsed['lineup']),
                    claude_troop_ratio=claude_parsed['troop_ratio'],
                    claude_reasoning=claude_parsed['reasoning'],
                    claude_time_ms=claude_response.get('time_ms'),
                    claude_raw_response=claude_response.get('raw_response'),

                    # Comparison
                    openai_vs_claude_score=openai_vs_claude['score'],
                    hero_overlap_openai=openai_vs_claude['hero_overlap'],
                    slot1_match_openai=openai_vs_claude['slot1_match'],

                    needs_review=openai_vs_claude['score'] < 0.6,
                )
                db.add(result)
                results_count += 1

                print(f"OpenAI/Claude match: {openai_vs_claude['score']:.0%}")

                # Commit periodically
                if results_count % 10 == 0:
                    db.commit()

        # Final commit
        db.commit()

        # Update test run stats
        actual_cost = (total_openai_input * pricing['input']) + (total_openai_output * pricing['output'])
        test_run.openai_tokens_input = total_openai_input
        test_run.openai_tokens_output = total_openai_output
        test_run.openai_cost_usd = actual_cost
        test_run.status = 'completed'
        test_run.completed_at = datetime.utcnow()

        # Calculate averages
        from sqlalchemy import func
        avg_scores = db.query(
            func.avg(LineupTestResult.openai_vs_claude_score)
        ).filter(LineupTestResult.test_run_id == test_run.id).first()
        test_run.avg_openai_vs_claude = avg_scores[0]

        db.commit()

        print(f"\n{'='*60}")
        print(f"TEST RUN COMPLETE")
        print(f"{'='*60}")
        print(f"Results stored: {results_count}")
        print(f"OpenAI tokens: {total_openai_input:,} input, {total_openai_output:,} output")
        print(f"Actual OpenAI cost: ${actual_cost:.2f}")
        print(f"OpenAI/Claude agreement: {test_run.avg_openai_vs_claude:.1%}")

        return test_run.id

    except Exception as e:
        test_run.status = 'failed'
        db.commit()
        print(f"\nERROR: {e}")
        raise


def view_result_detail(result_id: int):
    """View detailed information about a single test result - for debugging and review."""
    db = get_db()

    result = db.query(LineupTestResult).filter(LineupTestResult.id == result_id).first()
    if not result:
        print(f"Result {result_id} not found")
        return

    print(f"\n{'='*70}")
    print(f"DETAILED RESULT #{result.id}")
    print(f"{'='*70}")
    print(f"Profile: {result.profile_name} (Gen {result.generation}, Group: {result.test_group})")
    print(f"Scenario: {result.scenario}")
    print(f"Created: {result.created_at}")

    print(f"\n{'─'*70}")
    print("PROMPT SENT TO AI:")
    print(f"{'─'*70}")
    print(result.prompt_sent[:2000] + "..." if len(result.prompt_sent or '') > 2000 else result.prompt_sent)

    print(f"\n{'─'*70}")
    print("OPENAI RESPONSE:")
    print(f"{'─'*70}")
    print(f"Model: {result.openai_model}")
    print(f"Tokens: {result.openai_tokens_input} in / {result.openai_tokens_output} out")
    print(f"Time: {result.openai_time_ms}ms")
    print(f"\nLineup: {result.openai_lineup}")
    print(f"Troop Ratio: {result.openai_troop_ratio}")
    print(f"\nReasoning:\n{result.openai_reasoning}")

    print(f"\n{'─'*70}")
    print("CLAUDE RESPONSE:")
    print(f"{'─'*70}")
    print(f"Model: {result.claude_model}")
    print(f"Time: {result.claude_time_ms}ms")
    print(f"\nLineup: {result.claude_lineup}")
    print(f"Troop Ratio: {result.claude_troop_ratio}")
    print(f"\nReasoning:\n{result.claude_reasoning}")

    print(f"\n{'─'*70}")
    print("COMPARISON:")
    print(f"{'─'*70}")
    print(f"OpenAI vs Claude Match: {result.openai_vs_claude_score:.1%}")
    print(f"Hero Overlap: {result.hero_overlap_openai}/5")
    print(f"Slot 1 Match: {result.slot1_match_openai}")
    print(f"Needs Review: {result.needs_review}")

    # Show profile snapshot
    print(f"\n{'─'*70}")
    print("PROFILE SNAPSHOT (sent to AI):")
    print(f"{'─'*70}")
    snapshot = json.loads(result.profile_snapshot)
    print(f"Heroes ({len(snapshot['heroes'])}):")
    for h in snapshot['heroes'][:10]:  # Show first 10
        print(f"  - {h['name']}: Lvl {h['level']}, {h['stars']}★, {h['gear_quality']} gear")
    if len(snapshot['heroes']) > 10:
        print(f"  ... and {len(snapshot['heroes']) - 10} more")


def list_results(test_run_id: int, limit: int = 20):
    """List results from a test run for review."""
    db = get_db()

    results = db.query(LineupTestResult).filter(
        LineupTestResult.test_run_id == test_run_id
    ).order_by(LineupTestResult.openai_vs_claude_score.asc()).limit(limit).all()

    print(f"\n{'='*70}")
    print(f"RESULTS FOR TEST RUN #{test_run_id} (sorted by match score, lowest first)")
    print(f"{'='*70}")
    print(f"{'ID':>5} {'Profile':<25} {'Scenario':<20} {'Match':>6} {'Review'}")
    print(f"{'─'*70}")

    for r in results:
        review_flag = "⚠ YES" if r.needs_review else ""
        print(f"{r.id:>5} {r.profile_name:<25} {r.scenario:<20} {r.openai_vs_claude_score*100:>5.1f}% {review_flag}")

    print(f"\nUse --view-result <ID> to see detailed information")


def generate_report(test_run_id: int):
    """Generate a detailed report for a test run."""
    db = get_db()

    test_run = db.query(LineupTestRun).filter(LineupTestRun.id == test_run_id).first()
    if not test_run:
        print(f"Test run {test_run_id} not found")
        return

    results = db.query(LineupTestResult).filter(
        LineupTestResult.test_run_id == test_run_id
    ).all()

    print(f"\n{'='*60}")
    print(f"LINEUP TEST REPORT - Run #{test_run_id}")
    print(f"{'='*60}")
    print(f"Name: {test_run.name}")
    print(f"Status: {test_run.status}")
    print(f"Created: {test_run.created_at}")

    print(f"\nCOST SUMMARY")
    print(f"{'─'*40}")
    print(f"OpenAI tokens: {test_run.openai_tokens_input:,} in / {test_run.openai_tokens_output:,} out")
    print(f"OpenAI cost: ${test_run.openai_cost_usd:.2f}")
    print(f"Claude cost: $0.00 (Max plan)")

    print(f"\nOVERALL MATCH RATES")
    print(f"{'─'*40}")
    print(f"OpenAI vs Claude: {test_run.avg_openai_vs_claude:.1%}")

    # By scenario
    print(f"\nBY SCENARIO")
    print(f"{'─'*40}")
    from sqlalchemy import func
    scenario_stats = db.query(
        LineupTestResult.scenario,
        func.avg(LineupTestResult.openai_vs_claude_score),
        func.count(LineupTestResult.id)
    ).filter(
        LineupTestResult.test_run_id == test_run_id
    ).group_by(LineupTestResult.scenario).all()

    for scenario, avg_score, count in sorted(scenario_stats, key=lambda x: x[1] or 0):
        score_pct = (avg_score or 0) * 100
        status = "✓" if score_pct >= 80 else "⚠" if score_pct >= 60 else "✗"
        print(f"{scenario:25} {score_pct:5.1f}% {status} ({count} tests)")

    # Items needing review
    needs_review = [r for r in results if r.needs_review]
    if needs_review:
        print(f"\nITEMS NEEDING REVIEW ({len(needs_review)})")
        print(f"{'─'*40}")
        for r in needs_review[:10]:  # Show first 10
            print(f"- {r.profile_name} / {r.scenario}: {r.openai_vs_claude_score:.0%} match")


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Lineup Engine Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a small test batch first (recommended!)
  python scripts/test_lineups.py --test-batch

  # Run full test suite
  python scripts/test_lineups.py --run-all

  # Run specific profile group
  python scripts/test_lineups.py --profile-group generation

  # View results from a test run
  python scripts/test_lineups.py --list-results 1
  python scripts/test_lineups.py --view-result 42

  # Generate report
  python scripts/test_lineups.py --analyze-run 1

  # Dry run (no API calls, just show what would be tested)
  python scripts/test_lineups.py --run-all --dry-run
"""
    )

    # Run options
    parser.add_argument('--run-all', action='store_true', help='Run full test suite (all profiles, all scenarios)')
    parser.add_argument('--test-batch', action='store_true', help='Run small batch (3 profiles, 3 scenarios) for validation')
    parser.add_argument('--profile-group', type=str, help='Test specific profile group (generation, level_impact, gear_impact, etc.)')
    parser.add_argument('--scenario', type=str, help='Test specific scenario (bear_trap, rally_joiner, etc.)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be tested without making API calls')

    # Configuration
    parser.add_argument('--model', type=str, default='gpt-4o', help='OpenAI model to use (default: gpt-4o)')
    parser.add_argument('--name', type=str, help='Name for this test run')

    # Analysis options
    parser.add_argument('--analyze-run', type=int, metavar='RUN_ID', help='Generate summary report for a test run')
    parser.add_argument('--list-results', type=int, metavar='RUN_ID', help='List results from a test run')
    parser.add_argument('--view-result', type=int, metavar='RESULT_ID', help='View detailed info for a single result')

    args = parser.parse_args()

    # Handle analysis commands
    if args.view_result:
        view_result_detail(args.view_result)
    elif args.list_results:
        list_results(args.list_results)
    elif args.analyze_run:
        generate_report(args.analyze_run)
    # Handle run commands
    elif args.run_all or args.test_batch or args.profile_group or args.scenario:
        profile_groups = [args.profile_group] if args.profile_group else None
        scenarios = [args.scenario] if args.scenario else None

        run_lineup_tests(
            profile_groups=profile_groups,
            scenarios=scenarios,
            openai_model=args.model,
            run_name=args.name,
            dry_run=args.dry_run,
            test_batch=args.test_batch,
        )
    else:
        parser.print_help()
