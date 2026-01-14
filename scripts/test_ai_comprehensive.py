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
                        gear_levels=(0, 0, 0, 0), ascension=0,
                        account_type='main', server_age=0):
    """Add a hero to a profile with specified progression.

    Args:
        profile: UserProfile to add hero to
        hero_name: Name of hero to add
        level: Hero level (1-80)
        stars: Star count (0-5)
        exploration_skills: Tuple of 3 exploration skill levels (1-5)
        expedition_skills: Tuple of 3 expedition skill levels (1-5)
        gear_levels: Tuple of 4 gear quality values (0=None, 3=Blue, 4=Purple, 5=Gold, 6=Legendary)
        ascension: Ascension tier (0-5), only relevant when stars < 5
        account_type: 'whale', 'main', 'dolphin', 'f2p', 'farm' - affects gear/mastery scaling
        server_age: Server age in days - affects progression scaling
    """
    import random

    hero = db.query(Hero).filter(Hero.name == hero_name).first()
    if not hero:
        print(f"  Warning: Hero '{hero_name}' not found in database!")
        return None

    # Account type multipliers for gear progression
    type_multipliers = {
        'whale': 1.3,
        'main': 1.0,
        'dolphin': 0.9,
        'f2p': 0.6,
        'farm': 0.4,
    }
    multiplier = type_multipliers.get(account_type, 1.0)

    # Server age factor (older = more progression)
    age_factor = min(server_age / 600, 1.5)  # Caps at 1.5x at 600+ days

    def calc_gear_level(quality):
        """Calculate gear level with randomization based on quality and account type."""
        if quality == 0:
            return 0

        # Base level ranges by quality
        base_ranges = {
            1: (5, 20),    # Gray
            2: (15, 40),   # Green
            3: (30, 60),   # Blue
            4: (40, 80),   # Purple
            5: (60, 100),  # Gold
            6: (80, 100),  # Legendary
        }
        min_lvl, max_lvl = base_ranges.get(quality, (1, 20))

        # Apply multipliers
        adjusted_max = int(max_lvl * multiplier * age_factor)
        adjusted_min = int(min_lvl * multiplier * age_factor * 0.7)

        # Clamp to valid range
        adjusted_min = max(1, min(adjusted_min, 100))
        adjusted_max = max(adjusted_min, min(adjusted_max, 100))

        return random.randint(adjusted_min, adjusted_max)

    def calc_mastery(quality, gear_level):
        """Calculate mastery level - only Gold+ gear at level 20+ can have mastery."""
        if quality < 5 or gear_level < 20:
            return 0

        # Mastery scales with account type and server age
        base_mastery = min(int((gear_level - 20) / 4), 20)  # 0-20 based on level
        adjusted = int(base_mastery * multiplier * age_factor)

        # Add some randomness
        variance = random.randint(-2, 3)
        return max(0, min(adjusted + variance, 20))

    # Calculate gear levels and mastery for each slot
    gear_data = []
    for quality in gear_levels:
        lvl = calc_gear_level(quality)
        mastery = calc_mastery(quality, lvl)
        gear_data.append((quality, lvl, mastery))

    # Check if hero is legendary (for exclusive gear)
    is_legendary = hero.rarity == 'Legendary' if hero.rarity else False

    # Calculate exclusive gear for legendary heroes
    mythic_unlocked = False
    mythic_quality = 0
    mythic_level = 0
    mythic_mastery = 0

    if is_legendary and stars >= 3:
        # Legendary heroes with 3+ stars may have exclusive gear
        unlock_chance = 0.3 + (stars * 0.15) + (multiplier * 0.2)  # Higher chance for whales/high stars
        if random.random() < unlock_chance:
            mythic_unlocked = True
            # Quality scales with stars and account type
            if account_type == 'whale':
                mythic_quality = min(3 + stars, 6)  # Up to legendary
            elif account_type in ('main', 'dolphin'):
                mythic_quality = min(2 + stars, 5)  # Up to gold
            else:
                mythic_quality = min(1 + stars, 4)  # Up to purple

            mythic_level = calc_gear_level(mythic_quality)
            mythic_mastery = calc_mastery(mythic_quality, mythic_level)

    user_hero = UserHero(
        profile_id=profile.id,
        hero_id=hero.id,
        level=level,
        stars=stars,
        ascension_tier=ascension if stars < 5 else 0,
        exploration_skill_1_level=exploration_skills[0],
        exploration_skill_2_level=exploration_skills[1],
        exploration_skill_3_level=exploration_skills[2] if len(exploration_skills) > 2 else 1,
        expedition_skill_1_level=expedition_skills[0],
        expedition_skill_2_level=expedition_skills[1],
        expedition_skill_3_level=expedition_skills[2] if len(expedition_skills) > 2 else 1,
        # Gear slot 1
        gear_slot1_quality=gear_data[0][0],
        gear_slot1_level=gear_data[0][1],
        gear_slot1_mastery=gear_data[0][2],
        # Gear slot 2
        gear_slot2_quality=gear_data[1][0],
        gear_slot2_level=gear_data[1][1],
        gear_slot2_mastery=gear_data[1][2],
        # Gear slot 3
        gear_slot3_quality=gear_data[2][0],
        gear_slot3_level=gear_data[2][1],
        gear_slot3_mastery=gear_data[2][2],
        # Gear slot 4
        gear_slot4_quality=gear_data[3][0],
        gear_slot4_level=gear_data[3][1],
        gear_slot4_mastery=gear_data[3][2],
        # Exclusive/Mythic gear
        mythic_gear_unlocked=mythic_unlocked,
        mythic_gear_quality=mythic_quality,
        mythic_gear_level=mythic_level,
        mythic_gear_mastery=mythic_mastery,
    )
    db.add(user_hero)
    db.commit()
    return user_hero


def add_prior_gen_heroes(profile, max_gen, added_heroes=None, account_type='main', server_age=0):
    """Auto-add all heroes from generations prior to max_gen that aren't already added.

    When a state reaches Gen N, players typically have all prior gen heroes unlocked.
    This adds them with baseline progression appropriate for their generation.

    Args:
        profile: UserProfile to add heroes to
        max_gen: Current generation of the state (will add heroes from Gen 1 to max_gen-1)
        added_heroes: Set of hero names already added (to avoid duplicates)
        account_type: 'whale', 'main', 'dolphin', 'f2p', 'farm' - affects gear scaling
        server_age: Server age in days - affects progression scaling

    Returns:
        Count of heroes added
    """
    import random

    if added_heroes is None:
        added_heroes = set()

    # Account type affects base gear quality
    gear_bonus = {'whale': 2, 'main': 1, 'dolphin': 1, 'f2p': 0, 'farm': -1}.get(account_type, 0)

    count = 0
    for hero_data in HERO_DATA['heroes']:
        hero_name = hero_data['name']
        hero_gen = hero_data['generation']

        # Skip if already added or if gen is >= max_gen
        if hero_name in added_heroes or hero_gen >= max_gen:
            continue

        # Calculate baseline progression based on how old the hero generation is
        gen_age = max_gen - hero_gen  # How many gens ago this hero was released

        # Older heroes = more time to level up
        if gen_age >= 4:
            # Very old heroes - should be well developed
            level = min(60 + (gen_age * 3) + random.randint(-5, 10), 80)
            stars = min(3 + (gen_age // 2), 5)
            skills = tuple(min(3 + gen_age // 2 + random.randint(-1, 1), 5) for _ in range(3))
            base_gear = 3 + gear_bonus  # Blue+ gear
            gear = tuple(max(0, min(base_gear + random.randint(-1, 1), 6)) for _ in range(4))
            ascension = 3 if stars < 5 else 0
        elif gen_age >= 2:
            # Medium age heroes
            level = 45 + (gen_age * 5) + random.randint(-5, 10)
            stars = 2 + gen_age // 2
            skills = tuple(min(2 + gen_age // 2 + random.randint(0, 1), 5) for _ in range(3))
            base_gear = 2 + gear_bonus  # Green+ gear
            gear = tuple(max(0, min(base_gear + random.randint(-1, 1), 5)) for _ in range(4))
            ascension = 2 if stars < 5 else 0
        else:
            # Recent heroes - just started
            level = 30 + (gen_age * 10) + random.randint(0, 10)
            stars = 1 + gen_age
            skills = tuple(min(1 + gen_age + random.randint(0, 1), 5) for _ in range(3))
            base_gear = max(0, gear_bonus)  # Maybe no gear for f2p/farm
            gear = tuple(max(0, min(base_gear + random.randint(0, 1), 3)) for _ in range(4))
            ascension = 1 if stars < 5 else 0

        add_hero_to_profile(
            profile, hero_name, level, stars,
            skills, skills, gear, ascension,
            account_type=account_type, server_age=server_age
        )
        added_heroes.add(hero_name)
        count += 1

    return count


def add_chief_gear(profile, account_type='main', server_age=0):
    """Add chief gear to profile with randomized values based on account type.

    Chief gear tiers: 1-42 (stored in quality field)
    - 1-2: Green (0-1★)
    - 3-6: Blue (0-3★)
    - 7-14: Purple (0-3★, T1 0-3★)
    - 15-26: Gold (0-3★, T1 0-3★, T2 0-3★)
    - 27-42: Pink (0-3★, T1 0-3★, T2 0-3★, T3 0-3★)
    """
    import random

    # Base tier by account type
    base_tiers = {
        'whale': 35,    # Pink T2+
        'main': 22,     # Gold T1-T2
        'dolphin': 18,  # Gold base
        'f2p': 10,      # Purple
        'farm': 5,      # Blue
    }
    base = base_tiers.get(account_type, 15)

    # Adjust by server age (older = more progression)
    age_bonus = int(server_age / 100)  # +1 tier per 100 days

    def calc_tier():
        tier = base + age_bonus + random.randint(-3, 5)
        return max(1, min(tier, 42))

    # Generate 6 gear pieces with slight variation
    tiers = {slot: calc_tier() for slot in ['ring', 'amulet', 'helmet', 'armor', 'gloves', 'boots']}

    gear = UserChiefGear(
        profile_id=profile.id,
        ring_quality=tiers['ring'],
        ring_level=tiers['ring'],
        amulet_quality=tiers['amulet'],
        amulet_level=tiers['amulet'],
        helmet_quality=tiers['helmet'],
        helmet_level=tiers['helmet'],
        armor_quality=tiers['armor'],
        armor_level=tiers['armor'],
        gloves_quality=tiers['gloves'],
        gloves_level=tiers['gloves'],
        boots_quality=tiers['boots'],
        boots_level=tiers['boots'],
    )
    db.add(gear)
    db.commit()
    return gear


def add_chief_charms(profile, account_type='main', server_age=0):
    """Add chief charms to profile with randomized values based on account type.

    Each gear has 3 charm slots of the SAME type:
    - Cap/Watch: Keenness (Lancer)
    - Coat/Pants: Protection (Infantry)
    - Belt/Weapon: Vision (Marksman)

    Charm levels: 1-3 are simple, 4-16 have sub-levels (e.g., "4-1", "4-2", "4-3")
    """
    import random

    # Base charm level by account type
    base_levels = {
        'whale': 12,
        'main': 8,
        'dolphin': 6,
        'f2p': 4,
        'farm': 2,
    }
    base = base_levels.get(account_type, 5)

    # Adjust by server age
    age_bonus = int(server_age / 150)  # +1 level per 150 days

    def calc_charm_level():
        """Generate a charm level with sub-level for 4+."""
        level = base + age_bonus + random.randint(-2, 3)
        level = max(1, min(level, 16))

        if level < 4:
            return str(level)
        else:
            # For levels 4+, add sub-level
            sub = random.randint(1, 3)
            return f"{level}-{sub}"

    def calc_gear_charms():
        """Generate 3 charm levels for a gear piece."""
        return (calc_charm_level(), calc_charm_level(), calc_charm_level())

    cap = calc_gear_charms()
    watch = calc_gear_charms()
    coat = calc_gear_charms()
    pants = calc_gear_charms()
    belt = calc_gear_charms()
    weapon = calc_gear_charms()

    charms = UserChiefCharm(
        profile_id=profile.id,
        # Cap - Keenness slots
        cap_slot_1=cap[0],
        cap_slot_2=cap[1],
        cap_slot_3=cap[2],
        # Watch - Keenness slots
        watch_slot_1=watch[0],
        watch_slot_2=watch[1],
        watch_slot_3=watch[2],
        # Coat - Protection slots
        coat_slot_1=coat[0],
        coat_slot_2=coat[1],
        coat_slot_3=coat[2],
        # Pants - Protection slots
        pants_slot_1=pants[0],
        pants_slot_2=pants[1],
        pants_slot_3=pants[2],
        # Belt - Vision slots
        belt_slot_1=belt[0],
        belt_slot_2=belt[1],
        belt_slot_3=belt[2],
        # Weapon - Vision slots
        weapon_slot_1=weapon[0],
        weapon_slot_2=weapon[1],
        weapon_slot_3=weapon[2],
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
        server_age_days=700,
        furnace_level=30,  # FC level
        spending_profile="dolphin",
        alliance_role="filler",
        priorities={'svs': 5, 'rally': 5, 'castle': 4, 'exploration': 2, 'gathering': 1}
    )

    # Track added heroes for auto-fill
    added_heroes = set()

    # Add heroes - Gen 1-10 progression for a dolphin
    # Format: (name, level, stars, exp_skills, exped_skills, gear, ascension)
    heroes_to_add = [
        # Gen 1 - All maxed (5 stars = no ascension needed)
        ("Jeronimo", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5), 0),  # S+ tier, maxed
        ("Natalia", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5), 0),
        ("Molly", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5), 0),
        ("Sergey", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4), 0),  # Best garrison joiner
        ("Jessie", 70, 5, (4, 4, 4), (5, 5, 5), (4, 4, 4, 4), 0),  # Best attack joiner
        ("Bahiti", 60, 4, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 3),
        ("Patrick", 60, 4, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 3),

        # Gen 2-4 - High stars
        ("Flint", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5), 0),
        ("Philly", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5), 0),
        ("Alonso", 80, 5, (5, 5, 5), (5, 5, 5), (5, 5, 5, 5), 0),
        ("Logan", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4), 0),
        ("Mia", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4), 0),
        ("Greg", 75, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 4),
        ("Ahmose", 80, 5, (5, 5, 5), (5, 5, 5), (4, 4, 4, 4), 0),
        ("Reina", 75, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 4),
        ("Lynn", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 3),

        # Gen 5-6 - Good progress
        ("Hector", 75, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 4),
        ("Norah", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 3),
        ("Gwen", 70, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 3),
        ("Wu Ming", 75, 4, (4, 4, 4), (4, 4, 4), (4, 4, 4, 4), 4),  # S+ tier
        ("Renee", 65, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),

        # Gen 7-8 - Medium progress
        ("Gordon", 60, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),
        ("Edith", 60, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),
        ("Bradley", 55, 2, (2, 2, 2), (2, 2, 2), (2, 2, 2, 2), 1),
        ("Gatot", 55, 2, (2, 2, 2), (2, 2, 2), (2, 2, 2, 2), 1),
        ("Hendrik", 50, 2, (2, 2, 2), (2, 2, 2), (2, 2, 2, 2), 1),

        # Gen 9-10 - Just started
        ("Magnus", 45, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0), 0),  # S+ tier, new
        ("Blanchette", 40, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0), 0),  # S+ tier, new
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear, ascension = hero_data
        add_hero_to_profile(main_profile, name, level, stars, exp_skills, exped_skills, gear, ascension,
                           account_type='dolphin', server_age=700)
        added_heroes.add(name)

    # Auto-add remaining prior gen heroes (Gen 1-9) that weren't explicitly listed
    prior_count = add_prior_gen_heroes(main_profile, max_gen=10, added_heroes=added_heroes,
                                        account_type='dolphin', server_age=700)
    print(f"  Auto-added {prior_count} prior gen heroes")

    # Chief gear and charms - scaled by account type and server age
    add_chief_gear(main_profile, account_type='dolphin', server_age=700)
    add_chief_charms(main_profile, account_type='dolphin', server_age=700)

    print(f"  Created main profile: {main_profile.name} (ID: {main_profile.id})")
    print(f"  Heroes added: {len(heroes_to_add)}")

    # Farm account - same state, lower furnace
    farm_profile = create_profile(
        user=user,
        name="FrostKnight_Farm",
        state_number=456,  # Same state
        server_age_days=700,
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
        add_hero_to_profile(farm_profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='farm', server_age=700)

    print(f"  Created farm profile: {farm_profile.name} (ID: {farm_profile.id})")

    return user, main_profile, farm_profile


def setup_gen4_f2p():
    """
    Gen 4 F2P Player - Day 240
    - Furnace 26-28
    - Gen 1-3 heroes fully unlocked, starting Gen 4
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

    # Track added heroes to avoid duplicates when adding prior gen heroes
    added_heroes = set()

    # F2P Gen 4 heroes - limited resources, focused upgrades on key heroes
    # Format: (name, level, stars, exp_skills, exped_skills, gear, ascension)
    heroes_to_add = [
        # Gen 1 - Core heroes upgraded (3 gens old = well developed)
        ("Jeronimo", 60, 4, (4, 4, 3), (4, 4, 3), (4, 4, 3, 3), 3),  # Main infantry
        ("Natalia", 55, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),
        ("Molly", 55, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),
        ("Sergey", 50, 3, (3, 3, 3), (4, 3, 3), (3, 3, 3, 3), 2),  # Garrison joiner
        ("Jessie", 45, 3, (2, 2, 2), (4, 3, 3), (3, 3, 3, 3), 1),  # Attack joiner
        ("Bahiti", 45, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 1),  # Best Epic marksman

        # Gen 2 - Progressing (2 gens old)
        ("Flint", 50, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),
        ("Philly", 50, 3, (3, 3, 3), (3, 3, 3), (3, 3, 3, 3), 2),
        ("Alonso", 55, 3, (4, 4, 3), (4, 4, 3), (4, 4, 4, 4), 3),  # F2P focus hero

        # Gen 3 - Starting (1 gen old)
        ("Logan", 40, 2, (2, 2, 2), (2, 2, 2), (2, 2, 2, 2), 1),
        ("Mia", 40, 2, (2, 2, 2), (2, 2, 2), (2, 2, 2, 2), 1),

        # Gen 4 - Just unlocked (current gen)
        ("Ahmose", 35, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0), 0),
        ("Reina", 30, 1, (1, 1, 1), (1, 1, 1), (0, 0, 0, 0), 0),
    ]

    for hero_data in heroes_to_add:
        name, level, stars, exp_skills, exped_skills, gear, ascension = hero_data
        add_hero_to_profile(profile, name, level, stars, exp_skills, exped_skills, gear, ascension,
                           account_type='f2p', server_age=240)
        added_heroes.add(name)

    # Auto-add remaining prior gen heroes (Gen 1-3) that weren't explicitly listed
    prior_count = add_prior_gen_heroes(profile, max_gen=4, added_heroes=added_heroes,
                                        account_type='f2p', server_age=240)
    print(f"  Auto-added {prior_count} prior gen heroes")

    # Chief gear and charms - scaled by account type and server age
    add_chief_gear(profile, account_type='f2p', server_age=240)
    add_chief_charms(profile, account_type='f2p', server_age=240)

    total_heroes = len(heroes_to_add) + prior_count
    print(f"  Created profile: {profile.name} (ID: {profile.id})")
    print(f"  Total heroes: {total_heroes}")

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
        add_hero_to_profile(main_profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='whale', server_age=80)

    # Chief gear and charms - scaled by account type and server age
    add_chief_gear(main_profile, account_type='whale', server_age=80)
    add_chief_charms(main_profile, account_type='whale', server_age=80)

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
        add_hero_to_profile(farm_profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='farm', server_age=80)

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
        add_hero_to_profile(main_profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='main', server_age=400)

    add_chief_gear(main_profile, account_type='main', server_age=400)
    add_chief_charms(main_profile, account_type='main', server_age=400)

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
        add_hero_to_profile(new_state_profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='f2p', server_age=60)

    add_chief_gear(new_state_profile, account_type='f2p', server_age=60)
    add_chief_charms(new_state_profile, account_type='f2p', server_age=60)

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
        add_hero_to_profile(profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='f2p', server_age=7)

    # Minimal chief gear - scaled for new player
    add_chief_gear(profile, account_type='f2p', server_age=7)

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
        add_hero_to_profile(profile, name, level, stars, exp_skills, exped_skills, gear,
                           account_type='whale', server_age=380)

    # Chief gear and charms - orca/whale level
    add_chief_gear(profile, account_type='whale', server_age=380)
    add_chief_charms(profile, account_type='whale', server_age=380)

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
