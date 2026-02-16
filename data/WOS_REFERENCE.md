# Whiteout Survival - Complete Reference Guide

*Compiled from verified sources: WoS Wiki, Century Games Help Center, BlueStacks, LootBar, One Chilled Gamer*

---

## Table of Contents
1. [Hero Skill System](#hero-skill-system)
2. [Rally Mechanics](#rally-mechanics)
3. [Battle Mechanics & Combat Stats](#battle-mechanics--combat-stats)
4. [Chief Gear](#chief-gear)
5. [Hero Skills Database](#hero-skills-database)
6. [Troop Ratios](#troop-ratios)
7. [Server Timeline](#server-timeline)
8. [Hero Tier Rankings](#hero-tier-rankings)
9. [Event Strategies](#event-strategies)
10. [Recommendation Explanation System](#recommendation-explanation-system)

---

## Hero Skill System

Each hero has two types of skills, visible on separate sides of the skill screen:

### Exploration Skills (Left Side)
- Upgraded with **Exploration Manuals**
- Used for PvE content (exploration, events)
- Levels 1-5 with equal % increase per level
- Example: If max effect is 25%, each level gives +5%

### Expedition Skills (Right Side)
- Upgraded with **Expedition Manuals**
- Used for PvP content (rallies, garrison, SvS)
- Levels 1-5 with equal % increase per level
- **Top-right skill** is specifically used when joining rallies

### Manual Costs
Increasing amount of manuals required per level upgrade (exact amounts vary by hero rarity).

---

## Rally Mechanics

### Rally Leader (Captain)
**Source:** LootBar Rally Guide, WoS Wiki Advanced Rally Guide

- Rally leader's **3 heroes** provide buffs to the entire rally
- **9 expedition skills total** (3 right-side skills per hero × 3 heroes)
- All 9 skills activate regardless of hero positioning
- The higher your hero skills, the better the buffs

### Rally Joiner (Member)
**Source:** BlueStacks Rally Joiner Guide, Century Games Help Center

**CRITICAL:** Only your **leftmost hero's TOP-RIGHT expedition skill** contributes!
- **Leftmost hero**: First hero in your march lineup (slot 1, marked with blue flag)
- **Top-right skill**: The expedition skill in top-right position on hero skill screen
- Your other 2 heroes and their skills DON'T count when joining
- Top **4 highest SKILL LEVEL** expedition skills from all joiners apply
- Member skills **CAN stack** if they are the same effect

### Joiner Skill Selection
**Source:** WoS Wiki Advanced Rally Guide

"Only the 4 highest-leveled FIRST SKILL of the Hero Captain will be selected for battle."

### Best Joiner Heroes
| Role | Hero | Top-Right Skill | Effect per Level (1-5) |
|------|------|-----------------|------------------------|
| **Attack Joiner** | Jessie | Stand of Arms | +5/10/15/20/25% DMG dealt |
| **Garrison Joiner** | Sergey | Defenders' Edge | -4/8/12/16/20% DMG taken |

**Why Jessie is best for attack:** Her "damage dealt" buff affects ALL damage types including normal attacks, hero skills, pet abilities, and teammate buffs. This is superior to heroes that only boost basic auto-attack damage.

**Why Sergey is best for garrison:** Universal damage reduction is the most straightforward defensive joiner effect.

**Note:** Skill effects scale with level. A level 5 Jessie provides +25% DMG, while level 1 only provides +5%.

---

## Battle Mechanics & Combat Stats

**Source:** In-game battle reports (2026-02-14), verified from user screenshots.

### The 12 Combat Stats

Every battle is governed by **4 stats per troop type × 3 troop types = 12 stat bonuses**:

| Stat | What It Does | Sources |
|------|-------------|---------|
| **Attack** | Base damage output | Hero skills, Chief Gear, Charms, Research, VIP, Daybreak, Pets, Alliance |
| **Defense** | Damage mitigation/reduction | Same sources as Attack |
| **Lethality** | Armor penetration (ignores portion of enemy Defense) | Same sources; separate from Attack |
| **Health** | Total HP pool for troops | Same sources; separate from Defense |

These 4 stats apply independently to each troop type:
- **Infantry** Attack, Defense, Lethality, Health
- **Lancer** Attack, Defense, Lethality, Health
- **Marksman** Attack, Defense, Lethality, Health

### Stat Bonus Magnitudes

Stat bonuses are **cumulative percentages** from ALL sources stacked together. At high levels of play:
- Bonuses range from **300% to 800%+** (meaning troops are 4-9× their base stats)
- A well-invested account can have **2× the stat bonuses** of a mid-tier account across all 12 stats
- The largest gaps tend to be in **Lethality** (up to 3× advantage observed)
- Even "small" hero skill percentages (+5-25%) are meaningful multipliers on top of 300-800% base bonuses

### Real Battle Report Example (Feb 2026)

| Stat | Strong Account | Weaker Account | Advantage |
|------|---------------|----------------|-----------|
| Infantry Attack | +745.8% | +357.3% | 2.09× |
| Infantry Defense | +715.8% | +359.8% | 1.99× |
| Infantry Lethality | +585.7% | +261.7% | 2.24× |
| Infantry Health | +518.3% | +288.1% | 1.80× |
| Lancer Attack | +703.0% | +324.7% | 2.17× |
| Lancer Defense | +682.6% | +310.9% | 2.20× |
| Lancer Lethality | +401.2% | +238.7% | 1.68× |
| Lancer Health | +376.1% | +266.6% | 1.41× |
| Marksman Attack | +801.8% | +333.6% | 2.40× |
| Marksman Defense | +758.9% | +324.4% | 2.34× |
| Marksman Lethality | +757.8% | +244.3% | 3.10× |
| Marksman Health | +543.6% | +281.1% | 1.93× |

### How Stats Stack (Sources of Combat Bonuses)

All these sources combine **additively** into the final stat percentage:

1. **Hero Skills** — Expedition skills (PvP) or Exploration skills (PvE). Each hero provides buffs from their 3 active skills. Skill effects can be:
   - **Self buffs**: atk_buff, def_buff, hp_buff, dmg_dealt_buff, lethality_buff, shield, dodge, crit_rate, crit_dmg
   - **Enemy debuffs**: enemy_vuln (take more damage), enemy_def_debuff, enemy_atk_debuff, enemy_lethality_debuff
   - **Rally-wide**: enemy debuffs benefit ALL rally participants (not just your troops)
2. **Chief Gear** — 6 pieces, each with base stats + set bonus. Troop-type-specific: Coat/Pants = Infantry, Belt/Shortstaff = Marksman, Hat/Watch = Lancer
3. **Chief Charms** — Unlocked at Furnace 25. 3 slots per gear piece, same type. Levels 1-16 with sub-levels.
4. **Daybreak Island Decorations** — Mythic decorations give up to 10% per troop stat. Tree of Life gives universal buffs.
5. **Research** — Multiple research trees contribute stat bonuses
6. **VIP Level** — Passive stat increases
7. **Pets** — Pet skills provide additional stat buffs
8. **Alliance Technology** — Alliance-wide stat contributions

### Key Battle Mechanics

- **Attack vs Defense**: Attack determines raw damage, Defense reduces it. Lethality penetrates Defense.
- **Health vs Damage Reduction**: Health is the HP pool. Damage reduction (from skills like Wu Ming's -25%) applies BEFORE damage is dealt, reducing the effective hit.
- **Hero Power**: Each hero has individual power. In battle reports, heroes show individual power (e.g., lead hero at 100,807 vs support heroes at 33,602).
- **Battle outcome** depends on: stat advantages, troop composition, hero skill synergy, and troop count.

---

## Chief Gear

**Source:** WoS Wiki - Chief Gear, Chief Gear Upgrading & Forging

Chief Gear provides **global combat buffs** that apply to ALL heroes and troops. Unlike hero gear, Chief Gear is **always active** once equipped.

### The 6 Chief Gear Pieces

| Gear Piece | Troop Type | Stats | Priority |
|------------|------------|-------|----------|
| **Coat** | Infantry | Attack/Defense | 1 (when pushing next tier) |
| **Pants** | Infantry | Attack/Defense | 2 |
| **Belt** | Marksman | Attack/Defense | 3 |
| **Weapon** | Marksman | Attack/Defense | 4 |
| **Cap** | Lancer | Attack/Defense | 5 |
| **Watch** | Lancer | Attack/Defense | 6 (lowest) |

### Set Bonuses (CRITICAL)

- **3-piece bonus:** Defense boost for ALL troop types
- **6-piece bonus:** Attack boost for ALL troop types

**CRITICAL RULE:** Keep all 6 pieces at the SAME TIER to maintain set bonuses!

### Quality Tiers (Lowest → Highest)

1. Common → 2. Uncommon → 3. Rare → 4. Epic → 5. Legendary → 6. **Mythic**

**Long-term goal:** All 6 pieces to Legendary first (for 6-piece bonus), then push to Mythic starting with Infantry.

### Upgrade Priority Strategy

**Step 1 - Set Bonus First:**
- Keep ALL 6 pieces at the SAME TIER
- Don't max one piece while others lag behind
- The 6-piece Attack bonus benefits ALL your troops

**Step 2 - When Pushing to Next Tier (Infantry First):**
1. **Coat** (Infantry) - Frontline engages first, needs survivability
2. **Pants** (Infantry) - Frontline support
3. **Belt** (Marksman) - Key damage dealers
4. **Weapon** (Marksman) - Damage dealers
5. **Cap** (Lancer) - Mid-line support
6. **Watch** (Lancer) - Lowest priority

### Why Set Bonus First?

- 6-piece Attack bonus affects **ALL troops** (not just one class)
- Applies to rallies, field PvP, defense, SvS scoring
- Stacks with hero expedition buffs

### Common Mistakes

| Mistake | Why It's Wrong |
|---------|----------------|
| Maxing one piece while others lag | You lose the 6-piece set bonus that helps ALL troops |
| Upgrading Lancer/Marksman before Infantry | Infantry engage first - frontline survivability is critical |
| Not maintaining same tier across all 6 pieces | Missing out on Attack bonus for ALL troop types |

---

## Chief Gear vs Hero Gear ROI

**ROI = Return on Investment**: For each scarce resource spent, how much combat power gained and in how many modes?

### Chief Gear ROI (HIGHEST)

| Attribute | Value |
|-----------|-------|
| Scope | Global - all troops, all heroes |
| Scaling | Multiplicative |
| Mode Coverage | 100% (rallies, PvP, garrison, events, SvS) |
| Replacement Risk | None |
| Long-term Relevance | Permanent |

**Chief Gear is "foundational power" - no condition where it's inactive.**

### Hero Gear ROI (CONDITIONAL)

| Attribute | Value |
|-----------|-------|
| Scope | Single hero only |
| Scaling | Additive + conditional |
| Mode Coverage | Limited |
| Replacement Risk | HIGH (generation-bound) |
| Long-term Relevance | Hero-dependent |

**Hero Gear ROI requires ALL THREE conditions:**
1. Hero is used often
2. Hero is used in modes where gear matters
3. Hero is NOT about to be replaced by newer generation

If ANY condition fails → ROI collapses.

### Rally Context Changes Everything

| Context | Chief Gear ROI | Hero Gear ROI |
|---------|----------------|---------------|
| Rally Leader | High (multiplies entire rally) | Medium (only your 3 heroes) |
| Rally Joiner | High (still applies to your troops) | **Very Low** (barely matters) |
| Field PvP | High | High |
| Arena | High | High |

**Critical insight:** For rally joiners, hero gear ROI is extremely low. Chief Gear ROI is unchanged.

### Correct Investment Hierarchy

1. **Chief Gear: All 6 pieces to same tier** (for 6-piece Attack set bonus)
2. **Chief Gear: Push Infantry first** (Coat/Pants when upgrading to next tier)
3. **Chief Gear: Marksman second** (Belt/Weapon)
4. **Chief Gear: Lancer last** (Cap/Watch)
5. **Hero Gear on long-term core heroes** (if conditions met)
6. **Hero Gear on situational heroes**

**Only whales can safely violate this order.**

### Before Investing in Hero Gear, Verify:

- [ ] Hero is used as rally LEADER (not just joiner)
- [ ] Hero remains relevant next generation
- [ ] All 6 Chief Gear pieces at target tier FIRST (for set bonus)

---

## Spender-Level Gear Paths

**Core Principle:** Spender level determines how much inefficiency you can afford.

| Spender | Chief Gear | Hero Gear | Mistake Tolerance |
|---------|------------|-----------|-------------------|
| F2P | Mandatory | Minimal (1 hero max) | None |
| Low | Dominant | Limited (2 heroes) | Low |
| Medium | Balanced | Strategic (3-4 heroes) | Medium |
| Whale | Maxed | Everything | High |

### F2P (Free-to-Play)

**Reality:** Very limited resources. Cannot recover from mistakes quickly.

**Chief Gear:** ABSOLUTE priority
- Keep all 6 pieces at SAME TIER for set bonuses
- 6-piece Attack bonus helps ALL troops
- When pushing to next tier: Infantry (Coat/Pants) first

**Hero Gear:** Extremely limited
- Only 1 hero (primary field damage dealer)
- Must remain relevant 2+ generations
- NEVER gear rally joiners
- Targets: Molly OR Alonso (not both)

### Low Spender (Battle Pass / small packs)

**Reality:** Steady but slow income. Still punished by major misallocations.

**Chief Gear:** Still #1 priority
- Keep all 6 pieces at same tier for set bonuses
- Push Infantry (Coat/Pants) to next tier first

**Hero Gear:** Selective (2 heroes max)
- Must be used daily across multiple modes
- NOT purely rally joiner
- Targets: Alonso, Jeronimo (if rally leader), Molly
- AVOID: Gearing defensive heroes early

### Medium Spender

**Reality:** Can sustain upgrades. Can recover from mistakes.

**Chief Gear:** Foundational
- All 6 pieces to Legendary (for 6-piece Attack bonus)
- Push Infantry to Mythic first, then Marksman

**Hero Gear:** Strategic (3-4 heroes)
- Priority: Rally leader → Primary DPS → Secondary DPS → Situational
- Targets: Jeronimo, Alonso, Molly, 1 situational

### Whale

**Reality:** Resource constraints removed. Speed > efficiency.

**Chief Gear:** Max everything fast

**Hero Gear:** All core heroes
- Can gear heroes before optimal
- Can gear heroes knowing they'll be replaced
- ROI constraints ignored

---

## Combat Synergy Model

**Core Question:** Where does my power actually come from in this fight?

### Synergy Weights by Context (★ = importance, max 5)

#### Rally Leader
| Component | Weight | Why |
|-----------|--------|-----|
| Chief Gear | ★★★★★ | Full global multiplier |
| Leader Hero Selection | ★★★★★ | 9 skills define rally |
| Leader Hero Gear | ★★★☆☆ | Affects skill scaling |
| Joiner Hero Gear | ☆☆☆☆☆ | Irrelevant |

**Key:** Rally leaders chosen for EXPEDITION SKILL QUALITY, not DPS.

#### Rally Joiner
| Component | Weight |
|-----------|--------|
| Chief Gear | ★★★★★ |
| First Hero Skill | ★★★★☆ |
| Hero Gear | ★☆☆☆☆ |

**Key:** Joiners are SKILL CARRIERS, not damage dealers.

#### Field PvP
| Component | Weight |
|-----------|--------|
| Hero Gear | ★★★★★ |
| Hero DPS kit | ★★★★★ |
| Chief Gear | ★★★☆☆ |

**Key:** ONLY mode where hero gear rivals chief gear ROI.

#### Garrison
| Component | Weight |
|-----------|--------|
| Damage reduction skills | ★★★★★ |
| Chief Gear (defensive) | ★★★★☆ |
| Hero Gear | ★★☆☆☆ |
| DPS | ★☆☆☆☆ |

### Hero Role Tags

| Hero | Roles |
|------|-------|
| Jeronimo | rally_leader, attack_buffer |
| Jessie | attack_joiner |
| Sergey | defense_joiner, garrison |
| Molly | field_dps, solo |
| Alonso | field_dps, hybrid |
| Natalia | tank, garrison, rally_leader |

### Never Recommend

- DPS heroes as joiners (waste of slot)
- Defensive heroes as rally leaders
- Gearing joiner-only heroes

### Power Illusion Warning

> **Hero gear increases visible damage numbers.**
> **Chief gear increases battle outcomes.**

Warn users when they:
- Over-invest in hero gear
- Gear joiners
- Don't keep all 6 Chief Gear pieces at same tier (losing set bonus)

### Core Truths

1. Rallies are won by **buffs**, not DPS
2. Joiners carry **skills**, not damage
3. Chief Gear is **universal** power
4. Hero Gear is **situational** power
5. Spender level determines allowed inefficiency

---

## Hero Skills Database

### Jeronimo (Infantry, Gen 1)
**Source:** WoS Wiki

#### Expedition Skills
| Skill | Effect | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 |
|-------|--------|-----|-----|-----|-----|-----|
| Swordmentor | +ATK for all troops | 5% | 10% | 15% | 20% | 25% |
| Expert Swordsmanship | +DMG dealt (2 turns/4 turns) | 6% | 12% | 18% | 24% | 30% |
| Natural Leader | +Lethality & Health (all troops) | 3% | 6% | 9% | 12% | 15% |

#### Exploration Skills
| Skill | Effect | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 |
|-------|--------|-----|-----|-----|-----|-----|
| Battle Manifesto | +DMG dealt for all troops | 5% | 10% | 15% | 20% | 25% |
| Lone Wolf | +ATK when over 50% HP | 16% | 24% | 32% | 40% | 48% |

**Why Jeronimo is recommended as rally leader:**
- Multiple "all troops" offensive effects (damage dealt + attack)
- Periodic damage boost every 4 turns
- His kit is unusually valuable for rally-leading

---

### Jessie (Marksman, Gen 1)
**Source:** WoS Wiki

#### Expedition Skills
| Skill | Effect | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 |
|-------|--------|-----|-----|-----|-----|-----|
| **Stand of Arms** ⭐ | +DMG dealt (all troops) | 5% | 10% | 15% | 20% | 25% |
| Bulwarks | -DMG taken (all troops) | 4% | 8% | 12% | 16% | 20% |
| Defense Upgrade | +DEF | 25% | 37.5% | 50% | 62.5% | 70% |
| Weapon Upgrade | +ATK | 8% | 12% | 16% | 20% | 24% |

⭐ = Top-right skill (used when joining rallies)

---

### Sergey (Infantry, Gen 1)
**Source:** WoS Wiki

#### Expedition Skills
| Skill | Effect | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 |
|-------|--------|-----|-----|-----|-----|-----|
| **Defenders' Edge** ⭐ | -DMG taken (all troops) | 4% | 8% | 12% | 16% | 20% |
| Weaken | -Enemy ATK (all troops) | 4% | 8% | 12% | 16% | 20% |
| Shield Block | -DMG taken | 10% | 15% | 20% | 25% | 30% |
| Joint Defense | +DEF (all friendly heroes) | 5% | 7.5% | 10% | 12.5% | 15% |

⭐ = Top-right skill (used when joining garrisons)

---

### Natalia (Infantry, Gen 1)
**Source:** WoS Wiki

#### Expedition Skills
| Skill | Effect | Max Level |
|-------|--------|-----------|
| Unity | +30% damage dealt | Lv5 |
| Invincibles | +15% Lethality (rally troops) | Lv5 |

#### Exploration Skills
| Skill | Effect | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 |
|-------|--------|-----|-----|-----|-----|-----|
| Queen of the Wild | +ATK (all troops) | 5% | 10% | 15% | 20% | 25% |
| Call of the Wild | +DMG dealt (all troops) | 5% | 10% | 15% | 20% | 25% |
| Feral Protection | 40% chance to reduce troop DMG | 10% | 20% | 30% | 40% | 50% |
| Ursus Strength | +ATK & DEF (all troops) | 2% | 4% | 6% | 8% | 10% |

---

## Troop Ratios

**Source:** A Jack Of Everything Guide

### Combat Order
Infantry fights first → Lancers → Marksmen

### Class Counters
- Infantry beats Lancer
- Lancer beats Marksman
- Marksman beats Infantry

### Recommended Ratios by Activity

| Activity | Infantry | Lancer | Marksman | Notes |
|----------|----------|--------|----------|-------|
| **Default Formation** | 50% | 20% | 30% | Balanced for most content |
| **Castle Battle** | 50% | 20% | 30% | Standard PvP |
| **Bear Hunt** | 0% | 10% | 90% | Maximum DPS |
| **Crazy Joe** | 90% | 10% | 0% | Infantry kills before others engage |
| **Labyrinth** | 60% | 15% | 25% | Tanky for PvE |
| **Alliance Championship** | 45% | 25% | 35% | Balanced competitive |

### Strategy Notes
- Analyze battle reports to check if infantry survives
- If infantry dies too fast, increase infantry %
- If carrying excess troops, reduce infantry %
- For fast battles (Crazy Joe), back row may never engage

---

## Server Timeline

**Source:** WoS Wiki Server Timeline

### Hero Generations

| Gen | Day | Heroes |
|-----|-----|--------|
| Gen 1 | 0 | Natalia, Jeronimo, Molly, Zinman, Sergey, Gina, Bahiti |
| Gen 2 | 40 | Flint, Philly, Alonso |
| Gen 3 | 120 | Logan, Mia, Greg |
| Gen 4 | 195 | Ahmose, Reina, Lynn |
| Gen 5 | 270 | Hector, Nora, Gwen |
| Gen 6 | 360 | Wu Ming, Renee, Wayne |
| Gen 7 | 440 | Edith, Gordon, Bradley |
| Gen 8 | 520 | Gatot, Sonya, Hendrik |
| Gen 9 | 600 | Magnus, Fred, Xura |

### Key Milestones

| Day | Milestone |
|-----|-----------|
| 40 | Gen 2 + Legendary Hero Gear |
| 53 | Sunfire Castle |
| 54 | First Pets |
| 60 | Fire Crystal Age |
| 80 | State vs State / King of Ice |
| 120 | Gen 3 + Vision of Dawn |
| 150 | Fire Crystal 5 + Laboratory |
| 180 | Legendary Chief Gear |
| 220 | War Academy |
| 315 | Fire Crystal 8 |

---

## Hero Tier Rankings

**Source:** One Chilled Gamer Expedition Tier List

### By Role

#### Rally Joining (Most Critical)
Top performers: **Jessie**, **Jeronimo**
- Their 1st Expedition Skill provides strong rally buffs

#### Rally Leading
Use your **3 strongest heroes** (one per class)
- Latest generation heroes typically perform best
- Jeronimo remains optimal through Gen 3 for P2P players

#### Defending
Heroes with durability-enhancing skills:
- Walis Bokan
- Ling Xue
- Sergey

#### Beast Hunting
**Gina** is the premier choice

### Generation Power Ranking
Latest generations (7-9) automatically rank highest due to superior stats and abilities.

**Gen 1 heroes that remain valuable:**
- Jeronimo (rally leading)
- Natalia (tank)
- Jessie (attack joiner)
- Sergey (garrison joiner)

---

## Event Strategies

### Crazy Joe
**Source:** One Chilled Gamer Crazy Joe Guide

**Troop Ratio:** 90% Infantry / 10% Lancer / 0% Marksman

**Why Infantry?**
Infantry engage first. If their stats are high enough, they defeat all bandits before Lancers or Marksmen have a chance to attack.

**Scoring:**
- 20 waves total
- Waves 7, 14, 17: Online players only, ~2x points
- Waves 10, 20: Alliance HQ only
- 2 losses = elimination

**Tips:**
- Coordinate troop exchanges with allies
- Stay online during high-value waves
- Send Infantry when reinforcing for maximum kill participation
- Don't heal during event (reduces reinforcer opportunities)

### Bear Hunt
**Troop Ratio:** 0% Infantry / 10% Lancer / 90% Marksman

Maximum damage output since Bear doesn't kill your troops quickly.

### Castle Battle
**Troop Ratio:** 50% Infantry / 20% Lancer / 30% Marksman

Standard balanced PvP composition.

---

## Common Misconceptions

**Source:** Century Games Help Center, BlueStacks

### ❌ "All joiner skills apply with reduced effect"
**✅ TRUTH:** Only your first hero's TOP-RIGHT skill contributes. Other skills don't apply at all.

### ❌ "Joiner hero gear matters a lot"
**✅ TRUTH:** For joining rallies, only the first hero's single skill matters. Gear/chief buffs have minimal impact on join contribution.

### ❌ "Damage taken reduced" = "Enemy damage reduced"
**✅ TRUTH:** These are different subjects calculated differently. Stacking isn't simple addition.

---

## Sources

1. **WoS Wiki** - https://www.whiteoutsurvival.wiki/
   - Hero skill pages (Jeronimo, Jessie, Sergey, Natalia)
   - Server Timeline
   - Advanced Rally Guide

2. **Century Games Help Center** - https://centurygames.helpshift.com/
   - Rally skill stacking FAQ
   - Skill description clarifications

3. **BlueStacks Guides** - https://www.bluestacks.com/blog/game-guides/white-out-survival/
   - Rally Joiner Guide
   - Hero Combinations Guide
   - Crazy Joe Event Guide

4. **LootBar** - https://lootbar.gg/
   - Rally Heroes Formation Guide

5. **One Chilled Gamer** - https://onechilledgamer.com/
   - Expedition Hero Tier List
   - Crazy Joe Guide

6. **A Jack Of Everything** - https://www.ajackof.com/
   - Troop Formation Ratios Guide

---

## Recommendation Explanation System

The optimizer uses an evidence-based explanation system to build user trust and prevent hallucination.

### Reason Types

Every recommendation claim is tagged with a type:

| Type | Description | Trust Level |
|------|-------------|-------------|
| **mechanic** | Game rules (leader vs joiner, stacking limits) | Strongest |
| **data** | Verified database entries (skills/stats) | Strongest |
| **context** | Event/mode logic (SvS vs Bear vs CJ) | Strong |
| **economy** | Spender constraints (F2P vs whale) | Strong |
| **meta** | Community consensus (version-sensitive) | Weaker |
| **personalized** | User-specific inputs (their heroes/gear) | Strong |

### Confidence Grades

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 85%+ | Mechanics-backed + verified data |
| B | 70-84% | Strong evidence, minor assumptions |
| C | 50-69% | Some assumptions or meta-based |
| D | <50% | Speculative or user-dependent |

### Two-Level UX

**Level 1 (Short):** One sentence for casual users
> "Jessie is best because rally joiners only apply one top-right skill, and hers boosts all-troops damage."

**Level 2 (Expandable):** Full breakdown for power users
- Mechanic explanation
- Skill evidence
- Tradeoffs
- What to do next
- Scoring breakdown

### Core Claims (Evidence-Backed)

| Claim ID | Claim | Type |
|----------|-------|------|
| `claim_joiner_top_right_only` | Rally joiners only contribute the first hero's top-right expedition skill | mechanic |
| `claim_leader_9_skills` | Rally leaders provide 9 expedition skills (3 heroes x 3 skills each) | mechanic |
| `claim_top_4_joiner_skills` | Top 4 highest level expedition skills from all joiners are applied | mechanic |
| `claim_jessie_dmg_boost` | Jessie's top-right skill gives +5/10/15/20/25% DMG dealt per level | data |
| `claim_sergey_dmg_reduction` | Sergey's top-right skill gives -4/8/12/16/20% DMG taken per level | data |
| `claim_chief_gear_global` | Chief Gear provides global buffs in ALL combat modes | mechanic |
| `claim_hero_gear_personal` | Hero Gear only affects the individual hero equipped | mechanic |
| `claim_joiner_gear_low_roi` | Hero gear on rally joiners has minimal impact (skills matter, not damage) | economy |
| `claim_dps_personal_not_rally` | DPS is personal damage; rally outcomes scale with buffs | mechanic |

### Example Explanations

#### Jessie as Attack Joiner
- **Why:** Joiner uses only top-right skill; Jessie's buffs all-troops damage
- **Do:** Jessie in slot #1, level her top-right skill
- **Don't:** Sink hero gear into Jessie unless she's also field PvP core

#### Sergey as Defense Joiner
- **Why:** Joiner top-right skill; Sergey provides universal damage reduction
- **Do:** Sergey in slot #1 when joining defense/garrison rallies

#### Jeronimo as Rally Leader
- **Why:** Leader uses 9 skills; Jeronimo has multiple all-troops offensive effects
- **Do:** Prioritize as rally lead; Chief Gear first, then consider Jeronimo hero gear

#### Molly for Field, Not Rally
- **Why:** DPS is personal damage; rallies scale with buffs, not individual damage
- **Do:** Gear Molly for field/solo PvP only; don't expect rally improvement

#### Chief Gear Priority
- **Why:** 6-piece set bonus gives Attack to ALL troops
- **Do:** Keep all 6 pieces at same tier; when pushing next tier: Infantry → Marksman → Lancer
