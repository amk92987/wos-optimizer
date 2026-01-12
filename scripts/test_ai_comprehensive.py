"""
Comprehensive AI and Recommendation System Test Suite

Creates test users at different game stages and tests:
- Recommendation engine
- Lineup suggestions
- AI question handling (rules vs AI fallback)
- Response quality
"""

import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db
from database.models import User, UserProfile, Hero, UserHero, UserChiefGear, UserChiefCharm
from database.auth import hash_password
from engine import RecommendationEngine
from engine.ai_recommender import AIRecommender

# Initialize database
init_db()
db = get_db()

# Load hero data
with open(PROJECT_ROOT / "data" / "heroes.json", encoding='utf-8') as f:
    HERO_DATA = json.load(f)

HERO_LOOKUP = {h['name']: h for h in HERO_DATA['heroes']}


def ensure_heroes_in_db():
    """Make sure all heroes exist in the database."""
    existing = {h.name for h in db.query(Hero).all()}

    for hero_data in HERO_DATA['heroes']:
        if hero_data['name'] not in existing:
            hero = Hero(
                name=hero_data['name'],
                generation=hero_data['generation'],
                hero_class=hero_data['hero_class'],
                rarity=hero_data['rarity'],
                tier_overall=hero_data.get('tier_overall'),
                tier_expedition=hero_data.get('tier_expedition'),
                tier_exploration=hero_data.get('tier_exploration'),
                image_filename=hero_data.get('image_filename'),
                exploration_skill_1=hero_data.get('exploration_skill_1'),
                exploration_skill_2=hero_data.get('exploration_skill_2'),
                exploration_skill_3=hero_data.get('exploration_skill_3'),
                expedition_skill_1=hero_data.get('expedition_skill_1'),
                expedition_skill_2=hero_data.get('expedition_skill_2'),
                expedition_skill_3=hero_data.get('expedition_skill_3'),
                how_to_obtain=hero_data.get('how_to_obtain'),
                notes=hero_data.get('notes')
            )
            db.add(hero)

    db.commit()
    print(f"Heroes in database: {db.query(Hero).count()}")


def create_test_user(username, password="test123"):
    """Get or create a test user. Reuses existing test accounts."""
    user = db.query(User).filter(User.username == username).first()
    if user:
        # Ensure test flag is set on existing users
        if not user.is_test_account:
            user.is_test_account = True
            db.commit()
        return user

    user = User(
        username=username,
        email=f"{username}@test.com",
        password_hash=hash_password(password),
        role='user',
        is_active=True,
        is_test_account=True  # Flag as test account for easy filtering
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_profile(user, name, state_number, server_age_days, furnace_level,
                   spending_profile, alliance_role, priorities, is_farm=False,
                   linked_main_id=None):
    """Create a profile for a user."""
    profile = UserProfile(
        user_id=user.id,
        name=name,
        state_number=state_number,
        server_age_days=server_age_days,
        furnace_level=furnace_level,
        spending_profile=spending_profile,
        alliance_role=alliance_role,
        priority_svs=priorities.get('svs', 5),
        priority_rally=priorities.get('rally', 4),
        priority_castle_battle=priorities.get('castle', 3),
        priority_exploration=priorities.get('exploration', 3),
        priority_gathering=priorities.get('gathering', 2),
        is_farm_account=is_farm,
        linked_main_profile_id=linked_main_id
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def add_hero_to_profile(profile, hero_name, level, stars,
                        exploration_skills=(1, 1, 1), expedition_skills=(1, 1, 1),
                        gear_levels=(0, 0, 0, 0)):
    """Add a hero to a profile with specified progression."""
    hero = db.query(Hero).filter(Hero.name == hero_name).first()
    if not hero:
        print(f"  Warning: Hero '{hero_name}' not found in database!")
        return None

    user_hero = UserHero(
        profile_id=profile.id,
        hero_id=hero.id,
        level=level,
        stars=stars,
        exploration_skill_1_level=exploration_skills[0],
        exploration_skill_2_level=exploration_skills[1],
        exploration_skill_3_level=exploration_skills[2] if len(exploration_skills) > 2 else 1,
        expedition_skill_1_level=expedition_skills[0],
        expedition_skill_2_level=expedition_skills[1],
        expedition_skill_3_level=expedition_skills[2] if len(expedition_skills) > 2 else 1,
        gear_slot1_quality=gear_levels[0],
        gear_slot1_level=gear_levels[0] * 10 if gear_levels[0] else 0,
        gear_slot2_quality=gear_levels[1],
        gear_slot2_level=gear_levels[1] * 10 if gear_levels[1] else 0,
        gear_slot3_quality=gear_levels[2],
        gear_slot3_level=gear_levels[2] * 10 if gear_levels[2] else 0,
        gear_slot4_quality=gear_levels[3],
        gear_slot4_level=gear_levels[3] * 10 if gear_levels[3] else 0,
    )
    db.add(user_hero)
    db.commit()
    return user_hero


def add_chief_gear(profile, gear_levels):
    """Add chief gear to profile."""
    # gear_levels = {'ring': (quality, level), 'amulet': (quality, level), ...}
    gear = UserChiefGear(
        profile_id=profile.id,
        ring_quality=gear_levels.get('ring', (1, 1))[0],
        ring_level=gear_levels.get('ring', (1, 1))[1],
        amulet_quality=gear_levels.get('amulet', (1, 1))[0],
        amulet_level=gear_levels.get('amulet', (1, 1))[1],
        helmet_quality=gear_levels.get('helmet', (1, 1))[0],
        helmet_level=gear_levels.get('helmet', (1, 1))[1],
        armor_quality=gear_levels.get('armor', (1, 1))[0],
        armor_level=gear_levels.get('armor', (1, 1))[1],
        gloves_quality=gear_levels.get('gloves', (1, 1))[0],
        gloves_level=gear_levels.get('gloves', (1, 1))[1],
        boots_quality=gear_levels.get('boots', (1, 1))[0],
        boots_level=gear_levels.get('boots', (1, 1))[1],
    )
    db.add(gear)
    db.commit()
    return gear


def add_chief_charms(profile, charm_levels):
    """Add chief charms to profile.

    charm_levels format: {'cap': (prot, keen, vis), 'watch': (prot, keen, vis), ...}
    where each value is a tuple of (protection, keenness, vision) levels.
    """
    defaults = (1, 1, 1)
    charms = UserChiefCharm(
        profile_id=profile.id,
        cap_protection=charm_levels.get('cap', defaults)[0],
        cap_keenness=charm_levels.get('cap', defaults)[1],
        cap_vision=charm_levels.get('cap', defaults)[2],
        watch_protection=charm_levels.get('watch', defaults)[0],
        watch_keenness=charm_levels.get('watch', defaults)[1],
        watch_vision=charm_levels.get('watch', defaults)[2],
        coat_protection=charm_levels.get('coat', defaults)[0],
        coat_keenness=charm_levels.get('coat', defaults)[1],
        coat_vision=charm_levels.get('coat', defaults)[2],
        pants_protection=charm_levels.get('pants', defaults)[0],
        pants_keenness=charm_levels.get('pants', defaults)[1],
        pants_vision=charm_levels.get('pants', defaults)[2],
        belt_protection=charm_levels.get('belt', defaults)[0],
        belt_keenness=charm_levels.get('belt', defaults)[1],
        belt_vision=charm_levels.get('belt', defaults)[2],
        weapon_protection=charm_levels.get('weapon', defaults)[0],
        weapon_keenness=charm_levels.get('weapon', defaults)[1],
        weapon_vision=charm_levels.get('weapon', defaults)[2],
    )
    db.add(charms)
    db.commit()
    return charms


def setup_gen10_dolphin():
    """
    Gen 10 Middle Spender (Dolphin) - Day 560
    - FC6-FC8 level
    - Has all Gen 1-8 heroes, working on Gen 9-10
    - Strong heroes with good skills
    - Mythic chief gear on ring/amulet
    """
    print("\n" + "="*60)
    print("Setting up Gen 10 Dolphin Main Account")
    print("="*60)

    user = create_test_user("test_gen10_dolphin")

    # Main profile
    main_profile = create_profile(
        user=user,
        name="FrostKnight_560",
        state_number=456,
        server_age_days=560,
        furnace_level=30,  # FC level
        spending_profile="dolphin",
        alliance_role="filler",
        priorities={'svs': 5, 'rally': 5, 'castle': 4, 'exploration': 2, 'gathering': 1}
    )

    # Add heroes - Gen 1-10 progression for a dolphin
    heroes_to_add = [
        # Gen 1 - All maxed
        ("Jeronimo", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),  # S+ tier, maxed
        ("Natalia", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Molly", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Sergey", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),  # Best garrison joiner
        ("Jessie", 70, 5, (4, 4, 4), (5, 5, 5), (3, 3, 3, 3)),  # Best attack joiner
        ("Bahiti", 60, 4, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
        ("Patrick", 60, 4, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),

        # Gen 2-4 - High stars
        ("Flint", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Philly", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Alonso", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Logan", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Mia", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Greg", 75, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Ahmose", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Reina", 75, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Lynn", 70, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),

        # Gen 5-6 - Good progress
        ("Hector", 75, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),
        ("Norah", 70, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Gwen", 70, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Wu Ming", 75, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),  # S+ tier
        ("Renee", 65, 3, (3, 3, 3), (3, 3, 3), (2, 2, 2, 2)),

        # Gen 7-8 - Medium progress
        ("Gordon", 60, 3, (3, 3, 3), (3, 3, 3), (2, 2, 2, 2)),
        ("Edith", 60, 3, (3, 3, 3), (3, 3, 3), (2, 2, 2, 2)),
        ("Bradley", 55, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Gatot", 55, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Hendrik", 50, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),

        # Gen 9-10 - Just started
        ("Magnus", 45, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),  # S+ tier, new
        ("Blanchette", 40, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),  # S+ tier, new
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(main_profile, name, level, stars, exp_skills, exped_skills, gear)

    # Chief gear - Mythic ring/amulet, Legendary on others
    add_chief_gear(main_profile, {
        'ring': (7, 50),      # Mythic
        'amulet': (7, 50),    # Mythic
        'helmet': (6, 40),    # Legendary
        'armor': (6, 40),     # Legendary
        'gloves': (6, 35),    # Legendary
        'boots': (6, 35),     # Legendary
    })

    # Chief charms - Gen 10 dolphin has good charm progression
    add_chief_charms(main_profile, {
        'cap': (10, 8, 8),      # Protection focus (infantry defense)
        'watch': (10, 8, 8),
        'coat': (10, 8, 8),
        'pants': (10, 8, 8),
        'belt': (8, 8, 10),     # Vision focus (marksman attack)
        'weapon': (8, 8, 10),
    })

    print(f"  Created main profile: {main_profile.name} (ID: {main_profile.id})")
    print(f"  Heroes added: {len(heroes_to_add)}")

    # Farm account - same state, lower furnace
    farm_profile = create_profile(
        user=user,
        name="FrostKnight_Farm",
        state_number=456,  # Same state
        server_age_days=560,
        furnace_level=25,  # Lower furnace
        spending_profile="f2p",
        alliance_role="farmer",
        priorities={'svs': 1, 'rally': 1, 'castle': 1, 'exploration': 1, 'gathering': 5},
        is_farm=True,
        linked_main_id=main_profile.id
    )

    # Farm heroes - minimal, just for gathering
    farm_heroes = [
        ("Smith", 50, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
        ("Eugene", 50, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
        ("Charlie", 50, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
        ("Cloris", 50, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
    ]

    for hero_data in farm_heroes:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(farm_profile, name, level, stars, exp_skills, exped_skills, gear)

    print(f"  Created farm profile: {farm_profile.name} (ID: {farm_profile.id})")

    return user, main_profile, farm_profile


def setup_gen4_f2p():
    """
    Gen 4 F2P Player - Day 240
    - Furnace 26-28
    - Gen 1-3 heroes, starting Gen 4
    - Limited resources, careful upgrades
    """
    print("\n" + "="*60)
    print("Setting up Gen 4 F2P Account")
    print("="*60)

    user = create_test_user("test_gen4_f2p")

    profile = create_profile(
        user=user,
        name="IceWarrior_240",
        state_number=789,
        server_age_days=240,
        furnace_level=27,
        spending_profile="f2p",
        alliance_role="filler",
        priorities={'svs': 5, 'rally': 4, 'castle': 3, 'exploration': 3, 'gathering': 3}
    )

    # F2P Gen 4 heroes - limited resources, focused upgrades
    heroes_to_add = [
        # Gen 1 - Core heroes upgraded
        ("Jeronimo", 60, 4, (4, 4, 3), (4, 4, 3), (4, 4, 3, 3)),  # Main infantry
        ("Natalia", 55, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3)),
        ("Molly", 55, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3)),
        ("Sergey", 50, 3, (3, 3, 3), (4, 3, 3), (0, 0, 0, 0)),  # Garrison joiner
        ("Jessie", 45, 3, (2, 2, 2), (4, 3, 3), (0, 0, 0, 0)),  # Attack joiner
        ("Bahiti", 45, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),  # Best Epic marksman

        # Gen 2 - Progressing
        ("Flint", 50, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3)),
        ("Philly", 50, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3)),
        ("Alonso", 55, 3, (4, 4, 3), (4, 4, 3), (4, 4, 4, 4)),  # F2P focus hero

        # Gen 3 - Starting
        ("Logan", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Mia", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),

        # Gen 4 - Just unlocked
        ("Ahmose", 35, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
        ("Reina", 30, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(profile, name, level, stars, exp_skills, exped_skills, gear)

    # Chief gear - Epic on ring/amulet, Rare on others (F2P progression)
    add_chief_gear(profile, {
        'ring': (4, 30),      # Epic
        'amulet': (4, 25),    # Epic
        'helmet': (3, 20),    # Rare
        'armor': (3, 20),     # Rare
        'gloves': (3, 15),    # Rare
        'boots': (3, 15),     # Rare
    })

    # Chief charms - F2P Gen 4 has lower charm levels
    add_chief_charms(profile, {
        'cap': (4, 3, 3),
        'watch': (4, 3, 3),
        'coat': (4, 3, 3),
        'pants': (4, 3, 3),
        'belt': (3, 3, 4),
        'weapon': (3, 3, 4),
    })

    print(f"  Created profile: {profile.name} (ID: {profile.id})")
    print(f"  Heroes added: {len(heroes_to_add)}")

    return user, profile


def setup_gen2_whale():
    """
    Gen 2 Whale - Day 80
    - Furnace 24-25 (whales progress faster)
    - Gen 1-2 heroes, some Gen 3 early access from spending
    - Maximum investment in available heroes
    """
    print("\n" + "="*60)
    print("Setting up Gen 2 Whale Account")
    print("="*60)

    user = create_test_user("test_gen2_whale")

    # Main profile
    main_profile = create_profile(
        user=user,
        name="ArcticKing_80",
        state_number=999,
        server_age_days=80,
        furnace_level=25,  # Faster progression for whale
        spending_profile="whale",
        alliance_role="rally_lead",
        priorities={'svs': 5, 'rally': 5, 'castle': 5, 'exploration': 2, 'gathering': 1}
    )

    # Whale Gen 2 - maxed available heroes, some early Gen 3
    heroes_to_add = [
        # Gen 1 - All maxed or near max
        ("Jeronimo", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),  # Fully maxed
        ("Natalia", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Molly", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Sergey", 75, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Jessie", 70, 5, (4, 4, 4), (5, 5, 5), (3, 3, 3, 3)),
        ("Bahiti", 70, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Gina", 65, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Patrick", 65, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Zinman", 60, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Ling Xue", 60, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),

        # Gen 2 - High investment
        ("Flint", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),
        ("Philly", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),
        ("Alonso", 75, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),  # Main focus

        # Gen 3 - Early access from whale spending
        ("Logan", 50, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Mia", 45, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(main_profile, name, level, stars, exp_skills, exped_skills, gear)

    # Chief gear - Legendary everything (whale spending)
    add_chief_gear(main_profile, {
        'ring': (6, 45),      # Legendary
        'amulet': (6, 45),    # Legendary
        'helmet': (6, 40),    # Legendary
        'armor': (6, 40),     # Legendary
        'gloves': (5, 35),    # Gold
        'boots': (5, 35),     # Gold
    })

    # Chief charms - Whale Gen 2 has high investment despite being early
    add_chief_charms(main_profile, {
        'cap': (8, 6, 6),
        'watch': (8, 6, 6),
        'coat': (8, 6, 6),
        'pants': (8, 6, 6),
        'belt': (6, 6, 8),
        'weapon': (6, 6, 8),
    })

    print(f"  Created main profile: {main_profile.name} (ID: {main_profile.id})")
    print(f"  Heroes added: {len(heroes_to_add)}")

    # Farm account
    farm_profile = create_profile(
        user=user,
        name="ArcticKing_Farm",
        state_number=999,  # Same state
        server_age_days=80,
        furnace_level=18,  # Lower furnace
        spending_profile="f2p",
        alliance_role="farmer",
        priorities={'svs': 1, 'rally': 1, 'castle': 1, 'exploration': 1, 'gathering': 5},
        is_farm=True,
        linked_main_id=main_profile.id
    )

    # Farm heroes - minimal
    farm_heroes = [
        ("Smith", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Eugene", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Charlie", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Cloris", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
    ]

    for hero_data in farm_heroes:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(farm_profile, name, level, stars, exp_skills, exped_skills, gear)

    print(f"  Created farm profile: {farm_profile.name} (ID: {farm_profile.id})")

    return user, main_profile, farm_profile


def setup_multi_state_player():
    """
    Multi-State Player - Plays on two different servers
    - Main account on older state (State 200, Day 400)
    - Secondary account on newer state (State 850, Day 60)
    - Tests user with profiles in DIFFERENT states
    """
    print("\n" + "="*60)
    print("Setting up Multi-State Player")
    print("="*60)

    user = create_test_user("test_multi_state")

    # Main account on older state - established minnow
    main_profile = create_profile(
        user=user,
        name="Nomad_OldState",
        state_number=200,
        server_age_days=400,
        furnace_level=29,
        spending_profile="minnow",
        alliance_role="filler",
        priorities={'svs': 5, 'rally': 4, 'castle': 3, 'exploration': 3, 'gathering': 2}
    )

    # Older state heroes - good progression
    main_heroes = [
        ("Jeronimo", 70, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Natalia", 65, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Molly", 65, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Sergey", 60, 4, (4, 4, 4), (5, 4, 4), (0, 0, 0, 0)),
        ("Jessie", 55, 4, (3, 3, 3), (5, 4, 4), (0, 0, 0, 0)),
        ("Flint", 60, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Philly", 60, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Alonso", 65, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),
        ("Logan", 55, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
        ("Hector", 50, 3, (3, 3, 3), (3, 3, 3), (0, 0, 0, 0)),
    ]

    for hero_data in main_heroes:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(main_profile, name, level, stars, exp_skills, exped_skills, gear)

    add_chief_gear(main_profile, {
        'ring': (5, 35), 'amulet': (5, 30), 'helmet': (4, 25),
        'armor': (4, 25), 'gloves': (4, 20), 'boots': (4, 20),
    })

    add_chief_charms(main_profile, {
        'cap': (6, 5, 5), 'watch': (6, 5, 5), 'coat': (6, 5, 5),
        'pants': (6, 5, 5), 'belt': (5, 5, 6), 'weapon': (5, 5, 6),
    })

    print(f"  Created main profile: {main_profile.name} (State {main_profile.state_number}, ID: {main_profile.id})")
    print(f"  Heroes added: {len(main_heroes)}")

    # Secondary account on newer state - fresh start, F2P approach
    new_state_profile = create_profile(
        user=user,
        name="Nomad_NewState",
        state_number=850,  # Different state!
        server_age_days=60,
        furnace_level=20,
        spending_profile="f2p",
        alliance_role="filler",
        priorities={'svs': 4, 'rally': 3, 'castle': 3, 'exploration': 4, 'gathering': 3}
    )

    # New state heroes - early game
    new_state_heroes = [
        ("Jeronimo", 40, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Natalia", 35, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Molly", 35, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
        ("Sergey", 30, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
        ("Bahiti", 30, 2, (2, 2, 2), (2, 2, 2), (0, 0, 0, 0)),
    ]

    for hero_data in new_state_heroes:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(new_state_profile, name, level, stars, exp_skills, exped_skills, gear)

    add_chief_gear(new_state_profile, {
        'ring': (3, 15), 'amulet': (3, 10), 'helmet': (2, 10),
        'armor': (2, 10), 'gloves': (2, 5), 'boots': (2, 5),
    })

    add_chief_charms(new_state_profile, {
        'cap': (2, 1, 1), 'watch': (2, 1, 1), 'coat': (2, 1, 1),
        'pants': (2, 1, 1), 'belt': (1, 1, 2), 'weapon': (1, 1, 2),
    })

    print(f"  Created new state profile: {new_state_profile.name} (State {new_state_profile.state_number}, ID: {new_state_profile.id})")
    print(f"  Heroes added: {len(new_state_heroes)}")

    return user, main_profile, new_state_profile


def setup_brand_new_player():
    """
    Brand New Player - Day 7, just started
    - Very early game, F18
    - Only starter heroes
    - Tests recommendations for absolute beginners
    """
    print("\n" + "="*60)
    print("Setting up Brand New Player")
    print("="*60)

    user = create_test_user("test_new_player")

    profile = create_profile(
        user=user,
        name="FreshChief_7",
        state_number=900,
        server_age_days=7,
        furnace_level=18,
        spending_profile="f2p",
        alliance_role="casual",
        priorities={'svs': 2, 'rally': 2, 'castle': 2, 'exploration': 5, 'gathering': 4}
    )

    # New player heroes - just the basics
    heroes_to_add = [
        ("Jeronimo", 20, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
        ("Natalia", 15, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
        ("Molly", 15, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(profile, name, level, stars, exp_skills, exped_skills, gear)

    # Minimal chief gear
    add_chief_gear(profile, {
        'ring': (2, 5), 'amulet': (1, 1), 'helmet': (1, 1),
        'armor': (1, 1), 'gloves': (1, 1), 'boots': (1, 1),
    })

    # No charms yet (unlocks at F25)
    # Skip add_chief_charms

    print(f"  Created profile: {profile.name} (ID: {profile.id})")
    print(f"  Heroes added: {len(heroes_to_add)}")

    return user, profile


def setup_rally_leader():
    """
    Dedicated Rally Leader - Gen 6, Orca spender
    - Focuses on leading rallies, not joining
    - Tests role-specific recommendations
    """
    print("\n" + "="*60)
    print("Setting up Rally Leader")
    print("="*60)

    user = create_test_user("test_rally_leader")

    profile = create_profile(
        user=user,
        name="RallyCommander_380",
        state_number=350,
        server_age_days=380,
        furnace_level=30,
        spending_profile="orca",
        alliance_role="rally_lead",  # Key difference - rally leader role
        priorities={'svs': 5, 'rally': 5, 'castle': 4, 'exploration': 1, 'gathering': 1}
    )

    # Rally leader heroes - optimized for leading, not joining
    heroes_to_add = [
        # Rally lead heroes - maxed
        ("Jeronimo", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),  # Main rally leader
        ("Natalia", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Molly", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Alonso", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5)),
        ("Philly", 75, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),
        ("Logan", 75, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4)),

        # Still has joiner heroes but less invested
        ("Jessie", 50, 3, (2, 2, 2), (3, 2, 2), (0, 0, 0, 0)),
        ("Sergey", 50, 3, (2, 2, 2), (3, 2, 2), (0, 0, 0, 0)),

        # Gen 5-6 heroes
        ("Hector", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),
        ("Wu Ming", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4)),
        ("Norah", 65, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
        ("Gwen", 65, 4, (4, 4, 4), (4, 4, 4), (3, 3, 3, 3)),
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear = hero_data
        add_hero_to_profile(profile, name, level, stars, exp_skills, exped_skills, gear)

    add_chief_gear(profile, {
        'ring': (7, 60), 'amulet': (7, 55), 'helmet': (6, 45),
        'armor': (6, 45), 'gloves': (6, 40), 'boots': (6, 40),
    })

    add_chief_charms(profile, {
        'cap': (12, 10, 10), 'watch': (12, 10, 10), 'coat': (12, 10, 10),
        'pants': (12, 10, 10), 'belt': (10, 10, 12), 'weapon': (10, 10, 12),
    })

    print(f"  Created profile: {profile.name} (ID: {profile.id})")
    print(f"  Heroes added: {len(heroes_to_add)}")

    return user, profile


def run_recommendation_tests(profile, description):
    """Test recommendation engine for a profile."""
    print(f"\n{'='*60}")
    print(f"Testing Recommendations: {description}")
    print(f"Profile: {profile.name} | FC{profile.furnace_level} | {profile.spending_profile}")
    print("="*60)

    engine = RecommendationEngine(PROJECT_ROOT / "data")
    user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()

    # Get chief gear and charms
    chief_gear = db.query(UserChiefGear).filter(UserChiefGear.profile_id == profile.id).first()
    chief_charms = db.query(UserChiefCharm).filter(UserChiefCharm.profile_id == profile.id).first()

    # Convert gear to dict format expected by GearAdvisor
    gear_dict = None
    if chief_gear:
        gear_dict = {
            'chief_gear': {
                'ring': chief_gear.ring_quality,
                'amulet': chief_gear.amulet_quality,
                'helmet': chief_gear.helmet_quality,
                'armor': chief_gear.armor_quality,
                'gloves': chief_gear.gloves_quality,
                'boots': chief_gear.boots_quality,
            }
        }

    # Get recommendations
    recommendations = engine.get_recommendations(profile, user_heroes, gear_dict=gear_dict, limit=10)

    print(f"\nTop {len(recommendations)} Recommendations:")
    print("-" * 50)

    results = []
    for i, rec in enumerate(recommendations, 1):
        result = {
            'rank': i,
            'priority': rec.priority,
            'category': rec.category,
            'action': rec.action,
            'hero': rec.hero,
            'reason': rec.reason,
            'source': rec.source
        }
        results.append(result)

        # Replace Unicode arrows with ASCII for console output
        action_safe = rec.action.replace('→', '->').replace('★', '*').replace('☆', 'o')
        reason_safe = rec.reason.replace('→', '->').replace('★', '*').replace('☆', 'o')[:80]

        print(f"{i}. [P{rec.priority}] [{rec.category}] {action_safe}")
        print(f"   Hero: {rec.hero or 'N/A'} | Source: {rec.source}")
        print(f"   Reason: {reason_safe}...")
        print()

    return results


def run_lineup_tests(profile, description):
    """Test lineup suggestions for a profile."""
    print(f"\n{'='*60}")
    print(f"Testing Lineups: {description}")
    print(f"Profile: {profile.name}")
    print("="*60)

    engine = RecommendationEngine(PROJECT_ROOT / "data")
    user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()

    game_modes = [
        "rally_joiner_attack",
        "rally_joiner_defense",
        "bear_trap",
        "crazy_joe",
        "garrison",
        "svs_march"
    ]

    results = []
    for mode in game_modes:
        lineup = engine.get_lineup(mode, user_heroes, profile)

        result = {
            'mode': mode,
            'confidence': lineup['confidence'],
            'heroes': [h['hero'] for h in lineup['heroes']],
            'troop_ratio': lineup['troop_ratio'],
            'notes': lineup['notes'][:100]
        }
        results.append(result)

        print(f"\n{mode}:")
        print(f"  Confidence: {lineup['confidence']}")
        print(f"  Heroes: {', '.join(h['hero'] for h in lineup['heroes'][:3])}")
        print(f"  Troops: I:{lineup['troop_ratio'].get('infantry', 0)}% L:{lineup['troop_ratio'].get('lancer', 0)}% M:{lineup['troop_ratio'].get('marksman', 0)}%")

    return results


def run_ai_question_tests(profile, description):
    """Test AI with various questions to see rules vs AI fallback."""
    print(f"\n{'='*60}")
    print(f"Testing AI Questions: {description}")
    print(f"Profile: {profile.name}")
    print("="*60)

    engine = RecommendationEngine(PROJECT_ROOT / "data")
    ai_recommender = AIRecommender()
    user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()

    test_questions = [
        # Should hit rules engine
        ("Best rally joiner?", "rules"),
        ("Best garrison joiner?", "rules"),
        ("What hero should I use when joining attack rallies?", "rules"),
        ("Bear trap lineup?", "rules"),
        ("What troop ratio for Crazy Joe?", "rules"),

        # May need AI (complex/contextual)
        ("What should I upgrade next?", "depends"),
        ("How do I prepare for SvS?", "depends"),
        ("Is Jessie worth investing in?", "depends"),
        ("Should I focus on chief gear or hero gear?", "depends"),
        ("What's my biggest weakness?", "ai"),

        # Definitely needs AI (contextual analysis)
        ("Analyze my account and tell me what I'm doing wrong", "ai"),
        ("How do I maximize my power for SvS?", "ai"),
        ("What should a F2P player prioritize?", "ai"),
    ]

    results = []
    for question, expected_source in test_questions:
        print(f"\nQ: {question}")
        print(f"   Expected: {expected_source}")

        try:
            result = engine.ask(profile, user_heroes, question, force_ai=False)

            actual_source = result.get('source', 'unknown')
            answer_preview = result.get('answer', '')[:150] + "..."

            print(f"   Actual: {actual_source}")
            print(f"   Answer: {answer_preview}")

            results.append({
                'question': question,
                'expected': expected_source,
                'actual': actual_source,
                'match': expected_source == actual_source or expected_source == 'depends',
                'answer_length': len(result.get('answer', ''))
            })
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({
                'question': question,
                'expected': expected_source,
                'actual': 'error',
                'match': False,
                'error': str(e)
            })

    return results


def cleanup_test_users():
    """Clean up test profile data but keep the user accounts."""
    print("\nCleaning up existing test data...")

    test_usernames = [
        "test_gen10_dolphin", "test_gen4_f2p", "test_gen2_whale",
        "test_multi_state", "test_new_player", "test_rally_leader"
    ]

    for username in test_usernames:
        user = db.query(User).filter(User.username == username).first()
        if user:
            # Delete profiles and related data (but keep the user!)
            for profile in user.profiles:
                # Delete user heroes
                db.query(UserHero).filter(UserHero.profile_id == profile.id).delete()
                # Delete chief gear
                db.query(UserChiefGear).filter(UserChiefGear.profile_id == profile.id).delete()
                # Delete chief charms
                db.query(UserChiefCharm).filter(UserChiefCharm.profile_id == profile.id).delete()

            # Delete profiles (but NOT the user - we reuse them)
            db.query(UserProfile).filter(UserProfile.user_id == user.id).delete()

    db.commit()
    print("Cleanup complete.")


def main():
    """Run the comprehensive test suite."""
    print("="*70)
    print("COMPREHENSIVE AI AND RECOMMENDATION SYSTEM TEST SUITE")
    print("="*70)

    # Ensure heroes are in database
    ensure_heroes_in_db()

    # Cleanup any existing test data
    cleanup_test_users()

    # Setup test accounts
    gen10_user, gen10_main, gen10_farm = setup_gen10_dolphin()
    gen4_user, gen4_profile = setup_gen4_f2p()
    gen2_user, gen2_main, gen2_farm = setup_gen2_whale()
    multi_user, multi_main, multi_new_state = setup_multi_state_player()
    new_user, new_profile = setup_brand_new_player()
    rally_user, rally_profile = setup_rally_leader()

    # Run tests on each profile
    all_results = {
        'recommendations': {},
        'lineups': {},
        'ai_questions': {}
    }

    test_profiles = [
        # Original profiles
        (gen10_main, "Gen 10 Dolphin (Main)"),
        (gen10_farm, "Gen 10 Dolphin (Farm)"),
        (gen4_profile, "Gen 4 F2P"),
        (gen2_main, "Gen 2 Whale (Main)"),
        (gen2_farm, "Gen 2 Whale (Farm)"),
        # New profiles
        (multi_main, "Multi-State (Old State)"),
        (multi_new_state, "Multi-State (New State)"),
        (new_profile, "Brand New Player"),
        (rally_profile, "Rally Leader"),
    ]

    for profile, desc in test_profiles:
        all_results['recommendations'][desc] = run_recommendation_tests(profile, desc)
        all_results['lineups'][desc] = run_lineup_tests(profile, desc)

    # Only run AI tests on main profiles (not farms, not edge cases)
    ai_test_profiles = [
        (gen10_main, "Gen 10 Dolphin"),
        (gen4_profile, "Gen 4 F2P"),
        (gen2_main, "Gen 2 Whale"),
        (rally_profile, "Rally Leader"),
    ]

    for profile, desc in ai_test_profiles:
        all_results['ai_questions'][desc] = run_ai_question_tests(profile, desc)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    print("\n--- Recommendation Results ---")
    for profile_name, recs in all_results['recommendations'].items():
        print(f"\n{profile_name}: {len(recs)} recommendations")
        categories = {}
        for r in recs:
            cat = r['category']
            categories[cat] = categories.get(cat, 0) + 1
        print(f"  Categories: {categories}")

    print("\n--- Lineup Results ---")
    for profile_name, lineups in all_results['lineups'].items():
        print(f"\n{profile_name}:")
        for l in lineups:
            print(f"  {l['mode']}: {l['confidence']} - {', '.join(l['heroes'][:2])}...")

    print("\n--- AI Question Routing ---")
    total_questions = 0
    rules_count = 0
    ai_count = 0
    errors = 0

    for profile_name, questions in all_results['ai_questions'].items():
        print(f"\n{profile_name}:")
        for q in questions:
            total_questions += 1
            if q['actual'] == 'rules':
                rules_count += 1
            elif q['actual'] == 'ai':
                ai_count += 1
            elif q['actual'] == 'error':
                errors += 1

            status = "[OK]" if q.get('match', False) else "[X]"
            print(f"  {status} {q['question'][:40]}... -> {q['actual']}")

    print(f"\nQuestion Routing Summary:")
    print(f"  Total: {total_questions}")
    print(f"  Rules: {rules_count} ({rules_count/total_questions*100:.1f}%)")
    print(f"  AI: {ai_count} ({ai_count/total_questions*100:.1f}%)")
    print(f"  Errors: {errors}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

    return all_results


if __name__ == "__main__":
    results = main()
