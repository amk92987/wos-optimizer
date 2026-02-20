'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

type TabKey = 'critical' | 'hidden-gems' | 'hero-investment' | 'alliance' | 'mistakes' | 'by-category';

// Priority colors
const priorityColors: Record<string, { border: string; badge: string; label: string }> = {
  critical: { border: 'border-l-red-500', badge: 'bg-red-500/20 text-red-400', label: 'MUST KNOW' },
  high: { border: 'border-l-orange-500', badge: 'bg-orange-500/20 text-orange-400', label: 'Important' },
  medium: { border: 'border-l-blue-500', badge: 'bg-blue-500/20 text-blue-400', label: 'Good to Know' },
  low: { border: 'border-l-green-500', badge: 'bg-green-500/20 text-green-400', label: 'FYI' },
};

// Investment level colors
const investmentColors: Record<string, string> = {
  'MAX': 'bg-red-500/20 text-red-400 border-red-500/30',
  'MAX EXPEDITION': 'bg-red-500/20 text-red-400 border-red-500/30',
  'HIGH': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  'HIGH (Expedition only)': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  'HIGH (Exploration)': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  'MEDIUM-HIGH': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'MEDIUM': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'LOW-MEDIUM': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  'LOW': 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  'SKIP': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

// Tier colors
const tierColors: Record<string, string> = {
  'S+': 'bg-red-500 text-white',
  'S': 'bg-orange-500 text-white',
  'A': 'bg-blue-500 text-white',
  'B': 'bg-green-500 text-white',
  'C': 'bg-slate-500 text-white',
  'D': 'bg-gray-500 text-white',
};

// Class icons
const classIcons: Record<string, string> = {
  'Infantry': '🛡️',
  'Lancer': '⚔️',
  'Marksman': '🏹',
};

// Category icons
const categoryIcons: Record<string, string> = {
  daybreak_island: '🏝️',
  svs_prep: '⚔️',
  svs_battle: '⚔️',
  research: '🔬',
  chief_gear: '⚙️',
  chief_charms: '💎',
  combat: '🎯',
  pets: '🐻',
  events: '📅',
  packs: '📦',
  heroes: '🦸',
  alliance: '🏰',
  new_player: '🆕',
  upgrade_priorities: '📈',
  farm_accounts: '🌾',
};

// Hero niche uses - special badges for heroes with specific game mode value
const heroNicheUses: Record<string, { badge: string; tooltip: string }[]> = {
  'Mia': [{ badge: 'Bear Trap Star', tooltip: 'All 3 skills work regardless of Lancer count. Bad Luck Streak (+50% enemy dmg taken) + Lucky Charm (+50% extra dmg) = massive burst with RNG.' }],
  'Greg': [{ badge: 'Arena Strong', tooltip: "Law and Order gives guaranteed +25% HP to all troops. Deterrence of Law reduces enemy damage. Great for sustained PvP fights." }],
  'Jessie': [{ badge: 'Best Attack Joiner', tooltip: 'Stand of Arms: +25% damage dealt for ALL troops. Put in leftmost slot when joining rallies.' }],
  'Sergey': [{ badge: 'Best Defense Joiner', tooltip: "Defender's Edge: -20% damage taken for ALL troops. Put in leftmost slot when reinforcing garrisons." }],
  'Norah': [{ badge: 'Best Rally Joiner', tooltip: 'Sneak Strike: 20% chance for 20-100% extra damage to ALL enemies. Top-tier rally support.' }],
  'Wayne': [{ badge: 'Mia Synergy', tooltip: 'Thunder Strike: Extra attack every 4 turns + Fleet: 5-25% crit rate. Pairs with Mia for explosive Bear Trap damage.' }],
  'Bahiti': [{ badge: 'F2P Bear Trap', tooltip: 'Fluorescence: 50% chance of +10-50% damage for all troops. Similar RNG mechanics to Mia but Gen 1.' }],
  'Patrick': [{ badge: 'Early Utility', tooltip: 'Super Nutrients: +25% HP for all troops. Caloric Booster: +25% Attack. Solid early-game buffs.' }],
  'Natalia': [{ badge: 'Sustain Tank', tooltip: 'Feral Protection: 40% chance to reduce damage taken by 10-50%. Great for extended fights and garrison defense.' }],
  'Jeronimo': [{ badge: 'Best Rally Lead', tooltip: 'Battle Manifesto + Swordmentor + Expert Swordsmanship: Triple damage/attack buffs for ALL troops. #1 rally leader forever.' }],
  'Alonso': [{ badge: 'Poison DPS', tooltip: 'Poison Harpoon: 50% chance to deal 10-50% additional damage. Iron Strength: 20% chance to reduce enemy damage.' }],
  'Hector': [{ badge: 'Bear Trap Tank', tooltip: 'Rampant: +100-200% Infantry damage AND +20-100% Marksman damage. Great for Mia Bear Trap comps.' }],
  'Logan': [{ badge: 'Garrison Defense', tooltip: 'Lion Intimidation: -20% enemy Attack. Leader Inspiration: +20% Defense for all troops. Sustain tank for defense.' }],
  'Flint': [{ badge: 'Infantry DPS', tooltip: 'Pyromaniac: +100% Infantry Damage. Immolation: +25% Lethality for all troops. High damage output.' }],
  'Bradley': [{ badge: 'Attack Booster', tooltip: "Veteran's Might: +25% Attack for all troops. Tactical Assistance: +30% offense boost every 4 turns. Solid Marksman." }],
  'Blanchette': [{ badge: 'Crit DPS', tooltip: 'Crimson Sniper: +20% Crit Rate and +50% Crit Damage for all troops. Blood Hunter: +25% vs wounded. Top Marksman damage.' }],
  'Hervor': [{ badge: 'Top Infantry', tooltip: 'Call For Blood: +25% damage for all. Undying: -30% Infantry damage taken. Battlethirsty: +100% Infantry damage. S+ tier Infantry.' }],
  'Lloyd': [{ badge: 'Lethality King', tooltip: "Ingenious Mastery: +50% Lethality for all troops. Bird Invasion: -20% enemy Lethality. Top late-game Lancer." }],
};

// Critical tips data (aggregated from all categories)
const criticalTips = [
  { category: 'Daybreak Island', icon: '🏝️', tip: 'Mythic decorations give +10% stats, Epic only +2.5%', detail: 'Epic = 5 levels × 0.5% = 2.5% max. Mythic = 10 levels × 1% = 10% max. Skip straight to Mythic.' },
  { category: 'Daybreak Island', icon: '🏝️', tip: 'Build BOTH Attack and Defense Mythics for your main troop type', detail: 'Infantry: Floating Market (+10% ATK) + Snow Castle (+10% DEF). Lancer: Amphitheatre + Elegant Villa. Marksman: Observation Deck + Art Gallery.' },
  { category: 'SvS Prep', icon: '⚔️', tip: 'SPEEDUPS ONLY GIVE POINTS ON DAY 1, 2, AND 5', detail: 'Day 3 (Beast Slay) and Day 4 (Hero Development) give ZERO points for speedups. Save them!' },
  { category: 'SvS Prep', icon: '⚔️', tip: 'General Hero Shards do NOT give points', detail: 'Only NAMED hero shards (Jeronimo, Natalia, etc.) count. General shards = 0 points.' },
  { category: 'SvS Prep', icon: '⚔️', tip: "Day 4: Promote troops, don't train new ones", detail: 'T9→T10 promotion: 0.71 pts/sec. T8→T9: 0.64 pts/sec. Training NEW T10: only 0.39 pts/sec. Promoting beats speedups.' },
  { category: 'Research', icon: '🔬', tip: 'Prioritize Tool Enhancement at each tier (I-VII)', detail: 'Each level gives incremental research speed bonuses (0.4%-2.5% per level). Total across I-VII is ~35%. Do Tool Enhancement before other research at each tier.' },
  { category: 'Research', icon: '🔬', tip: 'Lethality research is a damage MULTIPLIER', detail: 'Attack and Lethality multiply together. +10% each = +21% damage. Prioritize Lethality over raw Attack.' },
  { category: 'Chief Gear', icon: '⚙️', tip: 'Keep all 6 Chief Gear pieces at SAME TIER for set bonuses', detail: "6-piece set bonus gives Attack to ALL troops. Don't max one piece while others lag behind - keep them even, then upgrade Infantry first." },
  { category: 'Chief Gear', icon: '⚙️', tip: 'Chief Gear priority: Infantry (Coat/Pants) > Marksman (Belt/Weapon) > Lancer (Cap/Watch)', detail: "When upgrading to next tier, do Infantry first. They're frontline and engage first in battle. Marksman are damage dealers. Lancer last." },
  { category: 'Combat', icon: '🎯', tip: "Rally joining: ONLY leftmost hero's expedition skill applies", detail: "Put Jessie (+25% DMG) or Jeronimo in leftmost slot. Other heroes' expedition skills are wasted." },
  { category: 'Heroes', icon: '🦸', tip: 'Jessie is the best rally joiner in the game', detail: '+25% DMG dealt to all troops at max expedition skill. Even at low investment, her expedition skill is top tier. MAX HER EXPEDITION SKILL FIRST.' },
  { category: 'Heroes', icon: '🦸', tip: 'Sergey is the best garrison joiner', detail: '-20% damage taken for ENTIRE garrison at max expedition skill. Critical for defense. MAX HIS EXPEDITION SKILL.' },
  { category: 'Heroes', icon: '🦸', tip: 'F2P: Focus resources on 3-4 core heroes maximum', detail: 'Spread resources = weak everywhere. Pick Jeronimo + Wu Ming + 1 Lancer + 1 Marksman. Max them before touching others.' },
  { category: 'SvS Battle', icon: '⚔️', tip: 'SHIELD UP during entire Battle Phase unless actively fighting', detail: 'Enemies can teleport to your state and attack unshielded cities. They get points for killing your troops.' },
  { category: 'SvS Battle', icon: '⚔️', tip: 'Attacking or joining rally DROPS your shield for 30 minutes', detail: "You can't re-shield for 30 min after attacking. Time your attacks carefully or you become a target." },
  { category: 'Upgrade Priorities', icon: '📈', tip: 'Hero Power (Essence Stones) and Research are the REAL long-term investments', detail: 'In mid/late game, these give permanent, multiplicative stat boosts that affect all combat. This is where serious players concentrate.' },
  { category: 'Upgrade Priorities', icon: '📈', tip: 'Troop Power is FAKE power', detail: "Having more troops seems great... until you have enough. Once you hit troop caps for rallies/marches, extra troops just sit there. Quality beats quantity." },
  { category: 'New Player', icon: '🆕', tip: "DON'T spend resources just because the red dot appears", detail: 'The game shows upgrade notifications constantly. Ignore them. Save resources for KEY events, not every event.' },
  { category: 'New Player', icon: '🆕', tip: 'Save ALL speedups for SvS Prep and Hall of Chiefs', detail: 'These events give massive rewards for speedup usage. Using speedups randomly = wasted value.' },
  { category: 'New Player', icon: '🆕', tip: 'Not all events are worth participating in', detail: 'Snowbusters, Fishing = pay-to-progress traps. SvS Prep, Bear Trap, Hall of Chiefs = high value. Be selective.' },
  { category: 'Farm Accounts', icon: '🌾', tip: 'Farm accounts = extra resource income for your main', detail: 'A farm account gathers resources 24/7 that you transfer to your main account. Essential for F2P/Dolphins to keep pace with spenders.' },
  { category: 'Farm Accounts', icon: '🌾', tip: 'Start farm accounts in the SAME STATE as your main', detail: "Resources can only be sent within your state. A farm in State 500 can't help your main in State 200." },
  { category: 'Alliance (R4/R5)', icon: '🏰', tip: 'R5 has full control; R4s assist with most management tasks', detail: 'R5 can build/relocate HQ, transfer leadership, disband alliance. R4 can kick R1-R3, start Tech research, build structures, manage Championship lanes.' },
  { category: 'Alliance (R4/R5)', icon: '🏰', tip: "Mark recommended Alliance Tech with green 'ok' icon for +20% contribution rewards", detail: 'When you endorse a tech, members get bonus contribution rewards. Coordinate which tech to prioritize.' },
];

// Common mistakes data
const commonMistakes = [
  { mistake: 'Spending resources whenever the red dot appears', correction: "Ignore red dots. Save speedups/FC/Mithril for SvS Prep and Hall of Chiefs - that's where the value is.", category: 'New Player' },
  { mistake: 'Not shielding during SvS Battle Phase', correction: 'Enemies can teleport to your state and attack. Shield up or lose troops and give them points.', category: 'SvS Battle' },
  { mistake: 'Using speedups on SvS Day 3 or 4', correction: 'Speedups only give points on Day 1, 2, and 5', category: 'SvS Prep' },
  { mistake: 'Ignoring Daybreak Island battle decorations', correction: 'Mythic decorations give +10% Attack/Defense per decoration - huge stat source', category: 'Daybreak Island' },
  { mistake: 'Skipping Tool Enhancement research at each tier', correction: 'Tool Enhancement I-VII gives cumulative ~35% research speed. Do Tool Enhancement before other research at each tier.', category: 'Research' },
  { mistake: 'Wrong hero in leftmost rally slot', correction: 'Only leftmost hero\'s expedition skill applies. Use Jessie or Jeronimo.', category: 'Combat' },
  { mistake: 'Upgrading one Chief Gear piece to max while others lag behind', correction: 'Keep all 6 pieces at SAME TIER for set bonuses. 6-piece Attack bonus helps ALL troops.', category: 'Chief Gear' },
  { mistake: 'Prioritizing Lancer/Marksman Chief Gear over Infantry', correction: 'Infantry engage first and form frontline. Upgrade order: Infantry (Coat/Pants) > Marksman (Belt/Weapon) > Lancer (Cap/Watch).', category: 'Chief Gear' },
  { mistake: 'Using General Hero Shards during SvS', correction: 'General shards give ZERO points. Only named hero shards count.', category: 'SvS Prep' },
  { mistake: 'Training new troops on SvS Day 4 with speedups', correction: 'PROMOTING troops (0.64-0.71 p/s) beats speedup value (0.50 p/s). Train new = 0.39 p/s = bad.', category: 'SvS Prep' },
  { mistake: 'Building Epic Daybreak decorations instead of Mythic', correction: 'Epic = 2.5% max. Mythic = 10% max. Skip to Mythic for 4x the bonus.', category: 'Daybreak Island' },
  { mistake: 'Spending Flames outside of Flame Lotto', correction: 'Save ALL Flames for Flame Lotto event. Best value per Flame by far.', category: 'Events' },
  { mistake: 'Attacking during SvS without planning shield timing', correction: 'Attacking drops shield for 30 min. You become a target. Time attacks with alliance coordination.', category: 'SvS Battle' },
  { mistake: 'Chasing troop count / troop power as main goal', correction: 'Troop power is fake power. Once you have enough for rallies, invest in Research and Essence Stones instead - permanent quality > temporary quantity.', category: 'Upgrade Priorities' },
  { mistake: 'Leaving Cookhouse on default Healthy Gruel', correction: 'Switch to Fancy Meal immediately. Small meat increase, huge happiness/health boost. Tap Cookhouse > Stove > menu icon > Fancy Meal.', category: 'New Player' },
  { mistake: 'Letting the Furnace run out of coal', correction: 'Coal burns 24/7 even offline. Keep Furnace on MAX power at all times. Survivors freeze without heat.', category: 'New Player' },
  { mistake: 'R4/R5 not checking rally joiner heroes before starting', correction: "Use rally overview screen to verify every joiner's first hero and skill ratings. Boot players who don't meet requirements.", category: 'Alliance' },
  { mistake: 'Poor Alliance Championship lane assignments', correction: 'Analyze enemy setups before placing players. Strategic positioning against weaker foes wins more than raw power.', category: 'Alliance' },
  { mistake: 'Starting a farm account in a different state than your main', correction: 'Resources can only be transferred within the same state. Farms must be in the same state as your main account to be useful.', category: 'Farm Accounts' },
  { mistake: 'Investing in heroes/research/gear on farm accounts', correction: 'Farms are just resource generators. Only level Furnace and resource buildings. All other investment is wasted.', category: 'Farm Accounts' },
];

// Alliance management tips
const allianceTips = [
  { tip: 'R5 has full control; R4s assist with most management tasks', detail: 'R5 can build/relocate HQ, transfer leadership, disband alliance. R4 can kick R1-R3, start Tech research, build structures, manage Championship lanes.', priority: 'critical' as const },
  { tip: "Mark recommended Alliance Tech with green 'ok' icon for +20% contribution rewards", detail: 'When you endorse a tech, members get bonus contribution rewards. Coordinate which tech to prioritize.', priority: 'critical' as const },
  { tip: 'Kick inactive players aggressively in new states', detail: 'Early game has high player churn. Keep roster active to maintain top alliance status. Full roster of actives > partial roster of inactives.', priority: 'high' as const },
  { tip: 'Verify rally joiner heroes BEFORE starting rally', detail: "Use rally overview screen to check every joiner's first hero and skill ratings. Boot joiners who don't meet requirements.", priority: 'high' as const },
  { tip: 'Set rally times in advance and communicate in alliance chat', detail: 'Assign roles, plan reinforcements, coordinate pet buffs. Preparation wins rallies more than raw power.', priority: 'high' as const },
  { tip: 'Alliance Championship: Assign lanes strategically', detail: 'R4/R5 assign players to lanes. Analyze enemy setups, position players to match against weaker opponents. Poor arrangement = facing stronger foes.', priority: 'high' as const },
  { tip: "Territory control requires 75% of farm's 2x2 area", detail: 'Only R4/R5 can place Alliance Banner blueprints. May need multiple banners around a farm to claim it fully.', priority: 'medium' as const },
  { tip: 'Joining a rally drops your shield for 30 minutes', detail: 'Starting or joining a rally = exposed to attacks. Reinforcing does NOT drop shield. Plan accordingly during SvS.', priority: 'medium' as const },
  { tip: 'Whitelist allows movement between specific alliances', detail: 'Players can be on multiple whitelists. Use this for coordinating between allied alliances without rejection delays.', priority: 'medium' as const },
];

// Hero investment data by generation
interface HeroData {
  name: string;
  class: string;
  tier: string;
  tierExpedition?: string;
  mythic?: boolean;
  investment: string;
  why: string;
  skills: string;
  longevity: string;
}

interface GenerationData {
  summary: string;
  heroes: HeroData[];
}

const heroGenerations: Record<string, GenerationData> = {
  '1': {
    summary: 'Foundation heroes - Jeronimo & Jessie stay meta forever',
    heroes: [
      { name: 'Jeronimo', class: 'Infantry', tier: 'S+', mythic: true, investment: 'MAX', why: 'Best rally leader in the game. His expedition skills boost all Infantry damage and stay relevant at every level of play.', skills: 'MAX all 3 expedition skills - Infantry Offense, Infantry Defense, and Infantry Health buffs all stack with your troops.', longevity: 'Forever meta. Still #1 rally leader even against Gen 14 heroes.' },
      { name: 'Jessie', class: 'Lancer', tier: 'A', tierExpedition: 'S+', investment: 'MAX EXPEDITION', why: "Best rally JOINER in the game. Her top-right expedition skill 'Stand of Arms' gives +25% damage dealt to the entire rally.", skills: "MAX 'Stand of Arms' (top-right expedition skill) to level 5 for +25% damage. Other skills are lower priority.", longevity: "Forever meta as a joiner. You'll use her in slot 1 for every attack rally you join." },
      { name: 'Sergey', class: 'Infantry', tier: 'B', tierExpedition: 'S', investment: 'HIGH (Expedition only)', why: "Best GARRISON joiner. His 'Defenders Edge' expedition skill reduces damage taken by the entire garrison by up to 20%.", skills: "MAX 'Defenders Edge' (top-right expedition skill). Skip exploration skills entirely.", longevity: 'Forever meta as garrison joiner. Put in slot 1 when defending.' },
      { name: 'Natalia', class: 'Infantry', tier: 'A', mythic: true, investment: 'MEDIUM', why: 'Solid frontline tank with good sustain. Feral Protection provides damage reduction. Has mythic gear for late-game scaling.', skills: 'Expedition skills if you need another Infantry. Gets replaced by Gen 6+ Infantry but mythic gear keeps her relevant.', longevity: 'Useful until Gen 6 Wu Ming. Mythic gear gives her late-game niche.' },
      { name: 'Molly', class: 'Lancer', tier: 'B', mythic: true, investment: 'LOW-MEDIUM', why: 'B-tier Lancer but has mythic gear. Worth keeping for late-game mythic investment if you lack better Lancers.', skills: 'Only invest if you\'re building her mythic gear. Otherwise skip for Norah/Gordon.', longevity: 'Mythic gear gives late-game potential. Otherwise outclassed by S-tier Lancers.' },
      { name: 'Zinman', class: 'Marksman', tier: 'C', mythic: true, investment: 'LOW', why: 'C-tier Marksman but has mythic gear. Only invest if you\'re a whale building all mythic heroes.', skills: 'Skip unless going for mythic gear completion.', longevity: 'Weak hero but mythic gear exists. Whales only.' },
      { name: 'Bahiti', class: 'Marksman', tier: 'B', tierExpedition: 'A', investment: 'LOW', why: 'Decent early Marksman but outclassed quickly. A-tier expedition gives some value.', skills: 'Only invest if no better Marksman available.', longevity: 'Replace with Gen 5 Gwen or any S-tier Marksman.' },
    ],
  },
  '2': {
    summary: 'Philly is the best healer until Gen 13 - invest heavily in exploration skills',
    heroes: [
      { name: 'Philly', class: 'Lancer', tier: 'A', investment: 'HIGH (Exploration)', why: 'Best healer in the game until Flora (Gen 13). Her exploration skills provide massive healing in PvE content.', skills: 'MAX all EXPLORATION skills. Her expedition skills are mediocre - focus on exploration for healing.', longevity: 'Meta healer until Gen 13 Flora. Even then, still usable as backup.' },
      { name: 'Alonso', class: 'Marksman', tier: 'A', investment: 'MEDIUM', why: 'Solid Marksman DPS. Good bridge hero until Gen 5+ Marksmen.', skills: 'Expedition skills for PvP. Replaced by Gwen (Gen 5) or Bradley (Gen 7).', longevity: 'Usable until Gen 7-8. Then becomes backup.' },
      { name: 'Flint', class: 'Infantry', tier: 'A', investment: 'LOW-MEDIUM', why: 'Backup Infantry tank. Not bad, but not essential.', skills: 'Only invest if you need Infantry depth.', longevity: 'Replaced by Wu Ming (Gen 6). Skip if resources are tight.' },
    ],
  },
  '3': {
    summary: "All A-tier heroes - use as bridges but don't over-invest",
    heroes: [
      { name: 'Logan', class: 'Infantry', tier: 'A', tierExpedition: 'S', investment: 'MEDIUM', why: 'Good Infantry with S-tier expedition rating. Provides solid troop buffs.', skills: 'Expedition skills have value. But Gen 6 Wu Ming is much better.', longevity: 'Bridge hero. Usable until Gen 6.' },
      { name: 'Mia', class: 'Lancer', tier: 'A', investment: 'LOW-MEDIUM', why: 'Decent Lancer but not special.', skills: 'Only invest if you need Lancer depth.', longevity: 'Replaced by Norah (Gen 5) or Gordon (Gen 7).' },
      { name: 'Greg', class: 'Marksman', tier: 'A', investment: 'LOW-MEDIUM', why: 'Serviceable Marksman. Nothing wrong with him.', skills: 'Expedition skills if needed.', longevity: 'Replaced by Gwen (Gen 5) or better.' },
    ],
  },
  '4': {
    summary: 'Skip generation - Gen 5 has much better options',
    heroes: [
      { name: 'Ahmose', class: 'Infantry', tier: 'A', investment: 'SKIP', why: "Passively collect shards but don't invest. Wu Ming (Gen 6) is far superior.", skills: 'Save your resources.', longevity: 'Outclassed by Gen 5-6. Skip.' },
      { name: 'Reina', class: 'Lancer', tier: 'A', investment: 'SKIP', why: 'Norah (Gen 5) comes right after and is S-tier.', skills: 'Save your resources.', longevity: 'Skip for Norah.' },
      { name: 'Lynn', class: 'Marksman', tier: 'A', investment: 'SKIP', why: 'Gwen (Gen 5) is coming and is S-tier.', skills: 'Save your resources.', longevity: 'Skip for Gwen.' },
    ],
  },
  '5': {
    summary: 'First S-tier generation! Norah and Gwen are excellent investments',
    heroes: [
      { name: 'Norah', class: 'Lancer', tier: 'S', tierExpedition: 'S+', investment: 'HIGH', why: 'Balanced offensive AND defensive buffs. -15% damage taken AND +15% damage dealt makes her versatile.', skills: 'MAX expedition skills. Her top-right skill is excellent for joining.', longevity: 'Long-term value. S+ expedition tier means she stays relevant.' },
      { name: 'Gwen', class: 'Marksman', tier: 'S', investment: 'HIGH', why: 'First S-tier Marksman. Solid DPS upgrade over all previous Marksmen.', skills: 'Expedition skills for PvP damage.', longevity: 'Usable until Gen 8+ Marksmen. Good value.' },
      { name: 'Hector', class: 'Infantry', tier: 'A', tierExpedition: 'S', investment: 'MEDIUM', why: 'A-tier overall but S-tier expedition. Good Infantry if you need depth.', skills: 'Expedition skills have value.', longevity: "Backup to Wu Ming (Gen 6). Don't over-invest." },
    ],
  },
  '6': {
    summary: 'Wu Ming is TOP 3 hero in the game - MAX EVERYTHING',
    heroes: [
      { name: 'Wu Ming', class: 'Infantry', tier: 'S+', investment: 'MAX', why: "Top 3 hero in the entire game. -25% ALL damage taken is unmatched sustain. Best defensive Infantry ever.", skills: "MAX ALL skills. Every expedition skill is valuable. He's worth every resource.", longevity: "Forever meta. Even Gen 14 doesn't replace him for pure defense." },
      { name: 'Renee', class: 'Lancer', tier: 'S', investment: 'HIGH', why: 'Infantry ATK boost benefits your Infantry troops. Good synergy with Wu Ming and Jeronimo.', skills: 'Expedition skills for Infantry buff.', longevity: 'Long-term value with Infantry-focused builds.' },
      { name: 'Wayne', class: 'Marksman', tier: 'A', investment: 'LOW', why: 'Only A-tier in a generation with an S+ hero. Skip unless you desperately need Marksman depth.', skills: 'Save resources for better Marksmen.', longevity: 'Outclassed by Gen 7-8 Marksmen.' },
    ],
  },
  '7': {
    summary: 'All three heroes are S-tier - solid generation',
    heroes: [
      { name: 'Gordon', class: 'Lancer', tier: 'S', investment: 'HIGH', why: 'Poison damage is devastating in rallies. Best Lancer for sustained damage over time.', skills: 'MAX expedition skills. Poison stacks make him excellent for long fights.', longevity: 'Rally specialist. Long-term value.' },
      { name: 'Edith', class: 'Infantry', tier: 'S', investment: 'HIGH', why: '3/3 sustain skills make her incredibly tanky. Great complement to Wu Ming.', skills: 'All expedition skills provide sustain buffs.', longevity: 'Solid Infantry depth. Long-term backup to Wu Ming.' },
      { name: 'Bradley', class: 'Marksman', tier: 'S', investment: 'HIGH', why: 'First S-tier Marksman with well-rounded skills. Solid ranged DPS.', skills: 'Expedition skills for PvP damage.', longevity: 'Usable until Gen 10 Blanchette. Good investment.' },
    ],
  },
  '8': {
    summary: 'Hendrik has S+ expedition rating - best single-target DPS',
    heroes: [
      { name: 'Gatot', class: 'Infantry', tier: 'S', investment: 'HIGH', why: 'Pure defense specialist. 3/3 sustain skills stack for maximum tankiness.', skills: 'All skills are defensive. Great for garrison and long fights.', longevity: 'Defensive specialist. Long-term Infantry depth.' },
      { name: 'Hendrik', class: 'Marksman', tier: 'S', tierExpedition: 'S+', investment: 'HIGH', why: 'S+ expedition tier - best single-target DPS Marksman until Blanchette (Gen 10).', skills: 'MAX expedition skills. His single-target damage is unmatched.', longevity: 'Long-term value. S+ expedition means relevance even late game.' },
      { name: 'Sonya', class: 'Lancer', tier: 'S', investment: 'MEDIUM-HIGH', why: 'Offense-focused Lancer. Good damage but less utility than Gordon.', skills: 'Expedition skills for attack buffs.', longevity: "Good Lancer option. Complements Gordon's poison." },
    ],
  },
  '9': {
    summary: 'Magnus is S+ Infantry - another must-have hero',
    heroes: [
      { name: 'Magnus', class: 'Infantry', tier: 'S+', investment: 'MAX', why: 'S+ Infantry with excellent all-around skills. Top-tier frontline hero.', skills: 'MAX all expedition skills. Every skill provides value.', longevity: "Forever meta. S+ tier doesn't get replaced easily." },
      { name: 'Xura', class: 'Marksman', tier: 'S', investment: 'HIGH', why: 'Solid S-tier Marksman. Good damage and utility.', skills: 'Expedition skills for PvP.', longevity: 'Usable until Blanchette (Gen 10). Good bridge.' },
      { name: 'Fred', class: 'Lancer', tier: 'A', investment: 'LOW', why: 'Only A-tier in a generation with an S+ hero. Skip unless you need Lancer depth.', skills: 'Save resources.', longevity: 'Outclassed by S-tier Lancers.' },
    ],
  },
  '10': {
    summary: 'Blanchette is THE best Marksman in the game - MAX EVERYTHING',
    heroes: [
      { name: 'Blanchette', class: 'Marksman', tier: 'S+', investment: 'MAX', why: 'Best Marksman in the entire game. S+ expedition tier. Highest DPS output possible.', skills: "MAX ALL skills. She's the Marksman equivalent of Jeronimo and Wu Ming.", longevity: 'Forever meta. Best Marksman even against Gen 14.' },
      { name: 'Freya', class: 'Lancer', tier: 'S', investment: 'HIGH', why: 'Strong S-tier Lancer. Good offensive capabilities.', skills: 'Expedition skills for damage.', longevity: 'Long-term Lancer value.' },
      { name: 'Gregory', class: 'Infantry', tier: 'A', investment: 'LOW', why: 'A-tier Infantry in a generation with an S+ Marksman. You have Wu Ming and Magnus already.', skills: 'Skip unless you need Infantry depth.', longevity: 'Outclassed by S+ Infantry.' },
    ],
  },
  '11': {
    summary: 'Rufus is solid S-tier Marksman, Lloyd has S expedition',
    heroes: [
      { name: 'Rufus', class: 'Marksman', tier: 'S', investment: 'MEDIUM-HIGH', why: 'Good S-tier Marksman but you likely have Blanchette already.', skills: 'Expedition skills if you need Marksman depth.', longevity: 'Good backup to Blanchette.' },
      { name: 'Lloyd', class: 'Lancer', tier: 'A', tierExpedition: 'S', investment: 'MEDIUM', why: 'A-tier overall but S expedition. Good joiner potential.', skills: 'Expedition skills for joining rallies.', longevity: 'Niche use as joiner. Not essential.' },
      { name: 'Eleonora', class: 'Infantry', tier: 'A', investment: 'LOW', why: 'A-tier Infantry when you have Wu Ming and Magnus.', skills: 'Skip unless you need depth.', longevity: 'Backup only.' },
    ],
  },
  '12': {
    summary: 'Hervor is S+ Infantry - another max investment hero',
    heroes: [
      { name: 'Hervor', class: 'Infantry', tier: 'S+', investment: 'MAX', why: 'S+ Infantry. Excellent skills that rival Wu Ming and Magnus.', skills: 'MAX all expedition skills. S+ heroes are always worth maxing.', longevity: 'Forever meta. Third S+ Infantry in your lineup.' },
      { name: 'Karol', class: 'Lancer', tier: 'S', investment: 'HIGH', why: 'Strong S-tier Lancer. Good all-around skills.', skills: 'Expedition skills for PvP.', longevity: 'Long-term Lancer value.' },
      { name: 'Ligeia', class: 'Marksman', tier: 'S', investment: 'MEDIUM-HIGH', why: 'S-tier Marksman. Good backup to Blanchette.', skills: 'Expedition skills if you need Marksman depth.', longevity: 'Solid Marksman depth.' },
    ],
  },
  '13': {
    summary: 'Vulcanus is S+ Marksman, Flora is the new best healer',
    heroes: [
      { name: 'Vulcanus', class: 'Marksman', tier: 'S+', investment: 'MAX', why: 'S+ Marksman. Rivals Blanchette for damage output.', skills: 'MAX all expedition skills. Two S+ Marksmen means devastating DPS.', longevity: 'Forever meta alongside Blanchette.' },
      { name: 'Flora', class: 'Lancer', tier: 'S', investment: 'HIGH (Exploration)', why: 'NEW BEST HEALER. Replaces Philly for PvE content. Massive healing output.', skills: 'MAX EXPLORATION skills for healing. Her expedition skills are secondary.', longevity: 'New meta healer. Philly becomes backup.' },
      { name: 'Gisela', class: 'Infantry', tier: 'A', investment: 'LOW', why: 'A-tier Infantry when you have three S+ Infantry already.', skills: 'Skip unless you need depth.', longevity: 'Backup only.' },
    ],
  },
  '14': {
    summary: 'Elif is S+ Infantry - latest and one of the best',
    heroes: [
      { name: 'Elif', class: 'Infantry', tier: 'S+', investment: 'MAX', why: 'Latest S+ Infantry. Fourth S+ Infantry option. Excellent skills.', skills: 'MAX all expedition skills. S+ Infantry are always meta.', longevity: 'Current meta. Future-proof investment.' },
      { name: 'Dominic', class: 'Lancer', tier: 'S', investment: 'HIGH', why: 'Strong S-tier Lancer. Good all-around performance.', skills: 'Expedition skills for PvP.', longevity: 'Long-term Lancer value.' },
      { name: 'Cara', class: 'Marksman', tier: 'S', investment: 'MEDIUM-HIGH', why: 'S-tier Marksman. Good but you have Blanchette and Vulcanus.', skills: 'Expedition skills if you need Marksman depth.', longevity: 'Third Marksman option.' },
    ],
  },
};

// Category tips data
const categoryTips: Record<string, { name: string; icon: string; tips: { tip: string; detail: string; priority: 'critical' | 'high' | 'medium' | 'low' }[] }> = {
  new_player: {
    name: 'New Player / Resource Management',
    icon: '🆕',
    tips: [
      { tip: "DON'T spend resources just because the red dot appears", detail: 'The game shows upgrade notifications constantly. Ignore them. Save resources for KEY events, not every event.', priority: 'critical' },
      { tip: 'Save ALL speedups for SvS Prep and Hall of Chiefs', detail: 'These events give massive rewards for speedup usage. Using speedups randomly = wasted value.', priority: 'critical' },
      { tip: 'Not all events are worth participating in', detail: 'Snowbusters, Fishing = pay-to-progress traps. SvS Prep, Bear Trap, Hall of Chiefs = high value. Be selective.', priority: 'critical' },
      { tip: 'Save Fire Crystals for SvS Prep Day 1 (2,000 pts each)', detail: 'Don\'t use FC for building upgrades randomly. Hoard them for SvS Prep where they give huge points.', priority: 'high' },
      { tip: 'Save Mithril for SvS Prep Day 4 (40,000 pts each)', detail: 'Mithril is extremely valuable during SvS. NEVER use it outside the event.', priority: 'high' },
      { tip: 'Early game: focus on Furnace level, not power', detail: 'Furnace unlocks systems and troops. Power is meaningless if you\'re behind on Furnace level.', priority: 'high' },
      { tip: 'Keep Furnace burning at all times - set to MAX power', detail: 'Never let your furnace run out of coal. Keep it on MAX power. Survivors freeze and become unhappy/sick without heat.', priority: 'high' },
      { tip: 'Upgrade Cookhouse to Fancy Meals immediately', detail: 'Tap Cookhouse > Stove > menu icon > select Fancy Meal. Tiny meat cost increase, huge boost to survivor happiness and health.', priority: 'high' },
    ],
  },
  upgrade_priorities: {
    name: 'Upgrade Priorities',
    icon: '📈',
    tips: [
      { tip: 'Hero Power (Essence Stones) and Research are the REAL long-term investments', detail: 'In mid/late game, these give permanent, multiplicative stat boosts that affect all combat.', priority: 'critical' },
      { tip: 'Troop Power is FAKE power', detail: 'Once you hit troop caps for rallies/marches, extra troops just sit there. Quality beats quantity.', priority: 'critical' },
      { tip: 'Damage scales with square root of troops', detail: 'Doubling your troops only gives +41% damage. But +10% Lethality from research? That\'s +10% forever on every fight.', priority: 'high' },
      { tip: 'Essence Stones boost Hero Gear Mastery permanently', detail: 'Each mastery level is a permanent stat increase. This compounds with research, gear, and everything else.', priority: 'high' },
    ],
  },
  svs_prep: {
    name: 'SvS Prep Phase',
    icon: '⚔️',
    tips: [
      { tip: 'SPEEDUPS ONLY GIVE POINTS ON DAY 1, 2, AND 5', detail: 'Day 3 (Beast Slay) and Day 4 (Hero Development) give ZERO points for speedups. Save them!', priority: 'critical' },
      { tip: 'General Hero Shards do NOT give points', detail: 'Only NAMED hero shards (Jeronimo, Natalia, etc.) count. General shards = 0 points.', priority: 'critical' },
      { tip: "Day 4: Promote troops, don't train new ones", detail: 'T9→T10 promotion: 0.71 pts/sec. Training NEW T10: only 0.39 pts/sec. Promoting beats speedups.', priority: 'critical' },
      { tip: 'Mithril = 40,000 points each on Day 4', detail: 'NEVER use Mithril outside SvS Prep. Save every single one for Day 4.', priority: 'high' },
      { tip: 'Lucky Wheel = 8,000 points per spin on Day 2 or 3', detail: 'Save all Lucky Wheel tickets for SvS Prep.', priority: 'high' },
    ],
  },
  svs_battle: {
    name: 'SvS Battle Phase',
    icon: '⚔️',
    tips: [
      { tip: 'SHIELD UP during entire Battle Phase unless actively fighting', detail: 'Enemies can teleport to your state and attack unshielded cities. They get points for killing your troops.', priority: 'critical' },
      { tip: 'Attacking or joining rally DROPS your shield for 30 minutes', detail: "You can't re-shield for 30 min after attacking. Time your attacks carefully or you become a target.", priority: 'critical' },
      { tip: 'Losing SvS = enemy can become Supreme President of BOTH states', detail: 'If enemy captures your Sunfire Castle, their alliance leader rules both states. Your president is removed.', priority: 'high' },
      { tip: 'Field Triage recovers 30-90% of troops lost in SvS', detail: 'Base 30% recovery. Use Rebirth Tomes with allies to increase up to 90%. Coordinate with alliance.', priority: 'high' },
    ],
  },
  daybreak_island: {
    name: 'Daybreak Island',
    icon: '🏝️',
    tips: [
      { tip: 'Mythic decorations give +10% stats, Epic only +2.5%', detail: 'Epic = 5 levels × 0.5% = 2.5% max. Mythic = 10 levels × 1% = 10% max. Skip straight to Mythic.', priority: 'critical' },
      { tip: 'Build BOTH Attack and Defense Mythics for your main troop type', detail: 'Infantry: Floating Market (+10% ATK) + Snow Castle (+10% DEF). Lancer: Amphitheatre + Elegant Villa. Marksman: Observation Deck + Art Gallery.', priority: 'critical' },
      { tip: 'Decorations give bigger bonuses than Tree of Life', detail: 'Two Mythic decorations = +20% for your troop type. Tree of Life L10 = only +5% Attack, +5% Defense universal.', priority: 'high' },
      { tip: 'Tree of Life combat buffs: L4 (DEF), L6 (ATK), L9 (HP), L10 (Lethality)', detail: 'Each is +5%. L1-3, L5, L7-8 are just Healing Speed - rush past them.', priority: 'medium' },
    ],
  },
  research: {
    name: 'Research',
    icon: '🔬',
    tips: [
      { tip: 'Prioritize Tool Enhancement at each tier (I-VII)', detail: 'Each level gives incremental research speed bonuses (0.4%-2.5% per level). Total across I-VII is ~35%.', priority: 'critical' },
      { tip: 'Lethality research is a damage MULTIPLIER', detail: 'Attack and Lethality multiply together. +10% each = +21% damage. Prioritize Lethality over raw Attack.', priority: 'critical' },
      { tip: 'Battle tree > Growth tree > Economy tree (after Tool Enhancement VII)', detail: 'Economy tree is lowest priority. Only do it after Battle and Growth are solid.', priority: 'high' },
      { tip: 'Research your MAIN troop type first', detail: 'If you\'re Infantry-focused, max Infantry Lethality/Attack/Defense before touching Marksman or Lancer.', priority: 'high' },
    ],
  },
  combat: {
    name: 'Combat & Rallies',
    icon: '🎯',
    tips: [
      { tip: "Rally joining: ONLY leftmost hero's expedition skill applies", detail: "Put Jessie (+25% DMG) or Jeronimo in leftmost slot. Other heroes' expedition skills are wasted.", priority: 'critical' },
      { tip: 'Exploration skills for PvE, Expedition skills for PvP', detail: 'Bear Trap, Labyrinth = Exploration. SvS, rallies, Crazy Joe, garrison = Expedition. Don\'t mix them up.', priority: 'high' },
      { tip: 'Sergey in leftmost slot for DEFENSE', detail: "Sergey's -20% DMG taken is best defensive skill. Use him when reinforcing garrisons.", priority: 'high' },
      { tip: 'Class counters: Infantry > Lancer > Marksman > Infantry', detail: "~30% damage bonus against weak class. Match your composition to counter enemy's main type.", priority: 'medium' },
    ],
  },
  chief_gear: {
    name: 'Chief Gear',
    icon: '⚙️',
    tips: [
      { tip: 'Keep all 6 Chief Gear pieces at SAME TIER for set bonuses', detail: "6-piece set bonus gives Attack to ALL troops. Don't max one piece while others lag behind.", priority: 'critical' },
      { tip: 'Chief Gear priority: Infantry > Marksman > Lancer', detail: "When upgrading to next tier, do Infantry first. They're frontline and engage first in battle.", priority: 'critical' },
      { tip: 'Chief Gear > Hero Gear for most players', detail: 'Chief Gear set bonuses affect ALL troops. Hero Gear only affects one hero. Prioritize Chief Gear unless you\'re a whale.', priority: 'high' },
    ],
  },
  heroes: {
    name: 'Heroes',
    icon: '🦸',
    tips: [
      { tip: 'Jessie is the best rally joiner in the game', detail: '+25% DMG dealt to all troops at max expedition skill. MAX HER EXPEDITION SKILL FIRST.', priority: 'critical' },
      { tip: 'Sergey is the best garrison joiner', detail: '-20% damage taken for ENTIRE garrison at max expedition skill. MAX HIS EXPEDITION SKILL.', priority: 'critical' },
      { tip: 'F2P: Focus resources on 3-4 core heroes maximum', detail: 'Spread resources = weak everywhere. Pick Jeronimo + Wu Ming + 1 Lancer + 1 Marksman.', priority: 'critical' },
      { tip: "Don't invest in heroes that will be replaced next generation", detail: 'Check hero tier lists. S+ heroes stay relevant. B/C tier heroes get replaced.', priority: 'high' },
      { tip: 'Philly is essential for PvE content', detail: 'Best healer until Gen 13 Flora. Healer critical for exploration, Bear Trap.', priority: 'high' },
    ],
  },
  pets: {
    name: 'Pets',
    icon: '🐻',
    tips: [
      { tip: 'Activate combat pets BEFORE battles', detail: 'Saber-tooth Tiger (+10% Lethality), Mammoth (+10% Defense), Frost Gorilla (+10% Health). 2-hour buffs.', priority: 'high' },
      { tip: 'Pet level matters - L100 gives ~2x the buff of L50', detail: "Don't just own combat pets, level them. Higher level = bigger percentage buff.", priority: 'medium' },
    ],
  },
  events: {
    name: 'Events',
    icon: '📅',
    tips: [
      { tip: 'NEVER spend Flames outside Flame Lotto', detail: 'Save every single Flame for Flame Lotto event. Best value for flame currency.', priority: 'high' },
      { tip: 'Snowbusters and Fishing are pay-to-progress', detail: "F2P players hit a wall quickly. Do free attempts only, don't buy packs for these.", priority: 'high' },
      { tip: 'Bear Trap is S-tier for F2P', detail: 'Best rewards for effort. Always participate. Use EXPLORATION skills team (not expedition).', priority: 'high' },
    ],
  },
  farm_accounts: {
    name: 'Farm Accounts',
    icon: '🌾',
    tips: [
      { tip: 'Farm accounts = extra resource income for your main', detail: 'A farm account gathers resources 24/7 that you transfer to your main account. Essential for F2P/Dolphins.', priority: 'critical' },
      { tip: 'Start farm accounts in the SAME STATE as your main', detail: "Resources can only be sent within your state. A farm in State 500 can't help your main in State 200.", priority: 'critical' },
      { tip: "Farm accounts don't need heroes, research, or gear", detail: 'Only level Furnace and resource buildings. No combat investment needed.', priority: 'high' },
      { tip: 'Farm accounts should stay under a shield 24/7', detail: 'Farms are weak targets. Keep them shielded always.', priority: 'high' },
      { tip: 'Aim for F18-F20 on farms, then stop', detail: 'Higher furnace = better resource buildings, but diminishing returns. F18-F20 is the sweet spot.', priority: 'high' },
    ],
  },
};

// Spending advice
const spendingAdvice: Record<string, string> = {
  f2p: 'Focus on 1-2 heroes per generation MAX. Prioritize S+ heroes: Jeronimo, Jessie (expedition only), Wu Ming, Magnus, Blanchette. Skip entire generations (Gen 4) to save resources.',
  minnow: 'Invest in all S+ heroes and 1 S-tier per generation. Skip A-tier heroes unless desperate for class depth.',
  dolphin: 'Invest in all S+ and S-tier heroes. A-tier heroes only as bridges while waiting for better options.',
  whale: 'MAX all S+ heroes. HIGH investment in all S-tier. Use A-tier as needed for depth and variety.',
};

// Hidden Gems - non-obvious competitive insights from deep combat analysis
const hiddenGems: { category: string; icon: string; tip: string; detail: string; priority: 'critical' | 'high' | 'medium' }[] = [
  // Combat Math - Critical
  {
    category: 'Combat Math', icon: '🔢',
    tip: 'Attack and Lethality MULTIPLY together in the damage formula',
    detail: 'Kills = sqrt(Troops) x (Attack x Lethality) / (Defense x Health). Since they multiply, investing in whichever stat is LOWER gives more damage per resource. Most accounts have Attack >> Lethality, so Lethality upgrades are almost always more efficient.',
    priority: 'critical',
  },
  {
    category: 'Combat Math', icon: '🔢',
    tip: '"Damage Dealt" buffs are the strongest buff type in the game',
    detail: 'There are 3 damage buff types: "Attack" (boosts base troop stat only), "Normal Attack Damage" (only troop auto-attacks), and "Damage Dealt" (multiplies EVERYTHING — troops, hero skills, pets, teammate buffs). Jessie\'s +25% Damage Dealt is a final multiplier on all damage sources.',
    priority: 'critical',
  },
  // Rally Strategy - Critical
  {
    category: 'Rally Strategy', icon: '🎯',
    tip: 'Mixed joiner compositions mathematically outperform identical joiners',
    detail: 'Hero skills have hidden categories (effect_op codes). Skills in the same category stack additively, but different categories multiply together. 4x Jessie = 2.0x damage. But 2 joiners from one category + 2 from another = 1.5 x 1.5 = 2.25x (12.5% more). Coordinate varied joiner heroes in rallies.',
    priority: 'critical',
  },
  {
    category: 'Rally Strategy', icon: '🎯',
    tip: 'Enemy debuffs benefit ALL rally participants — the biggest force multiplier',
    detail: 'Renee\'s enemy_vuln, Vulcanus\'s enemy_def_debuff, and Gordon\'s enemy_vuln apply to every member\'s troops. In a 20-person rally, a 30% enemy debuff effectively provides 30% x 20 participants = massive total value vs a personal 30% buff that only helps you.',
    priority: 'critical',
  },
  // Hidden Heroes - High
  {
    category: 'Hidden Heroes', icon: '🦸',
    tip: 'Renee (Gen 6) has the strongest debuff in the game',
    detail: 'Her Dreamcatcher skill applies 150% enemy vulnerability (50% uptime = 75% effective). In rallies, this benefits all participants. She should be a top priority for rally leader lineups, not just a "good Lancer."',
    priority: 'high',
  },
  {
    category: 'Hidden Heroes', icon: '🦸',
    tip: 'Rufus (Gen 11) is a stealth S++ hero',
    detail: 'He simultaneously buffs infantry DMG +60%, marksman DMG +100%, AND debuffs enemy lethality -50% and enemy vulnerability +25%. He\'s one of only 2 heroes who can reduce enemy Lethality — a stat most players can\'t counter.',
    priority: 'high',
  },
  {
    category: 'Hidden Heroes', icon: '🦸',
    tip: 'Blanchette is mathematically unique — the only hero with crit damage buff',
    detail: '+50% crit damage + 20% crit rate in the same kit. No other hero has crit_dmg_buff at all. In a marksman rally (Blanchette + Vulcanus + Rufus), you get 200% marksman DMG, 60% ATK, 50% crit DMG, and 90% enemy stat reduction.',
    priority: 'high',
  },
  // Gear & Widgets - High
  {
    category: 'Gear & Widgets', icon: '⚙️',
    tip: 'Exclusive gear bonuses (widgets) do NOT work when joining rallies',
    detail: 'Rally leaders get full widget benefits. Garrison defenders get defensive widgets. But rally JOINERS get zero widget benefit. Expensive exclusive gear upgrades on joiner-only heroes like Jessie or Sergey are completely wasted in rallies.',
    priority: 'high',
  },
  {
    category: 'Gear & Widgets', icon: '⚙️',
    tip: 'Exclusive skills use DUAL math — both additive AND multiplicative',
    detail: 'Regular stats (research, chief gear) stack purely additively. But exclusive skills and buff items apply +X% additive AND xX% multiplicative simultaneously. This makes exclusive skill levels on rally leader heroes disproportionately powerful per percentage point.',
    priority: 'high',
  },
  // Combat Math - Medium
  {
    category: 'Combat Math', icon: '🔢',
    tip: 'Class counters only provide 10% attack bonus, not 30%',
    detail: 'Many guides overstate the rock-paper-scissors bonus. The real counter advantage is only ~10% attack. Stat bonuses and skill quality matter roughly 7x more than getting the counter matchup right. Don\'t restructure your whole composition just for counters.',
    priority: 'medium',
  },
  // Troop Mechanics - Medium
  {
    category: 'Troop Mechanics', icon: '⚔️',
    tip: 'T7+ Lancers can bypass Infantry to hit Marksmen directly',
    detail: 'T7+ Lancers have a hidden "Ambusher" skill: 20% chance to skip the frontline and strike back-row Marksmen. T7+ Marksmen get "Volley": 10% chance to attack twice in one turn. Always include some Lancers for anti-Marksman insurance in mixed compositions.',
    priority: 'medium',
  },
  // Garrison - Medium
  {
    category: 'Garrison', icon: '🏰',
    tip: 'Garrison uses the HIGHEST stat bonuses from all defenders, not the owner\'s',
    detail: 'When reinforcing a garrison, the player with the best stat bonuses among all defenders becomes the stat source for the entire garrison. A whale reinforcing a dolphin\'s city is extremely powerful. A dolphin reinforcing a whale adds troop bodies but not stats.',
    priority: 'medium',
  },
  // Drill Camp - Medium
  {
    category: 'Drill Camp', icon: '🏋️',
    tip: 'Drill Camp syncs all heroes to your 5th-best hero\'s level for free',
    detail: 'No daily cost to use Drill Camp. Only costs 500 gems to swap a hero out immediately instead of waiting the 24h cooldown. This means investing heavily in 5 core heroes implicitly raises your entire roster\'s level.',
    priority: 'medium',
  },
  // SvS - Medium
  {
    category: 'SvS', icon: '⚔️',
    tip: 'SvS casualty recovery heavily favors attacking over defending',
    detail: 'Attackers recover 90% of losses via Field Triage. Defenders lose troops more permanently (35% dead, 10% severely injured). Alliance strategy should favor aggressive rallies over passive garrison stacking when you have the stats to compete.',
    priority: 'medium',
  },
];

function TipCard({ tip, detail, priority, categoryBadge }: { tip: string; detail: string; priority: 'critical' | 'high' | 'medium' | 'low'; categoryBadge?: string }) {
  const colors = priorityColors[priority];
  return (
    <div className={`bg-surface/50 border-l-4 ${colors.border} p-4 rounded-lg mb-3`}>
      <div className="flex justify-between items-start gap-3">
        <div className="flex-1">
          <p className="font-semibold text-frost mb-1">{tip}</p>
          <p className="text-sm text-frost-muted">{detail}</p>
        </div>
        <div className="flex flex-col gap-1 items-end">
          {categoryBadge && (
            <span className="text-xs px-2 py-0.5 rounded bg-surface text-frost-muted whitespace-nowrap">
              {categoryBadge}
            </span>
          )}
          <span className={`text-xs px-2 py-0.5 rounded ${colors.badge} whitespace-nowrap`}>
            {colors.label}
          </span>
        </div>
      </div>
    </div>
  );
}

function HeroCard({ hero }: { hero: HeroData }) {
  const investmentStyle = investmentColors[hero.investment] || investmentColors['MEDIUM'];
  const tierStyle = tierColors[hero.tier] || tierColors['B'];
  const classIcon = classIcons[hero.class] || '?';
  const niches = heroNicheUses[hero.name] || [];

  return (
    <div className={`bg-surface/50 border-l-4 p-4 rounded-lg mb-3 ${
      hero.investment.includes('MAX') ? 'border-l-red-500' :
      hero.investment.includes('HIGH') ? 'border-l-orange-500' :
      hero.investment.includes('MEDIUM') ? 'border-l-blue-500' :
      'border-l-slate-500'
    }`}>
      <div className="flex justify-between items-start gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xl">{classIcon}</span>
          <span className="font-bold text-frost text-lg">{hero.name}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${tierStyle}`}>
            {hero.tier}{hero.tierExpedition && hero.tierExpedition !== hero.tier ? ` (Exp: ${hero.tierExpedition})` : ''}
          </span>
          {hero.mythic && (
            <span className="text-xs px-2 py-0.5 rounded bg-gradient-to-r from-yellow-500 to-orange-500 text-black font-bold">
              MYTHIC GEAR
            </span>
          )}
          {niches.map((niche, i) => (
            <span
              key={i}
              className="text-xs px-2 py-0.5 rounded bg-purple-500/30 text-purple-300 cursor-help"
              title={niche.tooltip}
            >
              {niche.badge}
            </span>
          ))}
        </div>
        <span className={`text-xs px-2 py-1 rounded border ${investmentStyle} whitespace-nowrap font-medium`}>
          {hero.investment}
        </span>
      </div>
      <div className="text-sm text-frost-muted space-y-2">
        <p><strong className="text-frost">Why:</strong> {hero.why}</p>
        <p><strong className="text-frost">Skills:</strong> {hero.skills}</p>
        <p><strong className="text-frost">Longevity:</strong> {hero.longevity}</p>
      </div>
    </div>
  );
}

function CriticalTipsTab() {
  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">Critical Tips</h2>
      <p className="text-frost-muted mb-6">The most impactful knowledge. Get these wrong and you'll fall behind.</p>

      {criticalTips.map((tip, i) => (
        <TipCard
          key={i}
          tip={tip.tip}
          detail={tip.detail}
          priority="critical"
          categoryBadge={`${tip.icon} ${tip.category}`}
        />
      ))}
    </div>
  );
}

function HiddenGemsTab() {
  // Group tips by category
  const grouped: Record<string, typeof hiddenGems> = {};
  for (const gem of hiddenGems) {
    if (!grouped[gem.category]) grouped[gem.category] = [];
    grouped[gem.category].push(gem);
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">Hidden Gems</h2>
      <p className="text-frost-muted mb-6">
        Non-obvious competitive insights from deep combat analysis. The stuff even experienced players miss.
      </p>

      {Object.entries(grouped).map(([category, tips]) => (
        <div key={category} className="mb-6">
          <h3 className="text-lg font-semibold text-frost mb-3 flex items-center gap-2">
            <span>{tips[0].icon}</span> {category}
          </h3>
          {tips.map((gem, i) => (
            <TipCard
              key={i}
              tip={gem.tip}
              detail={gem.detail}
              priority={gem.priority}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

function HeroInvestmentTab() {
  const [expandedGens, setExpandedGens] = useState<Set<string>>(new Set(['1', '5', '6']));

  const toggleGen = (gen: string) => {
    const newExpanded = new Set(expandedGens);
    if (newExpanded.has(gen)) {
      newExpanded.delete(gen);
    } else {
      newExpanded.add(gen);
    }
    setExpandedGens(newExpanded);
  };

  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">Hero Investment by Generation</h2>
      <p className="text-frost-muted mb-4">Which heroes to prioritize when unlocking each generation. Click to expand.</p>

      {/* PvE vs PvP explanation */}
      <details className="mb-6 bg-surface/50 rounded-lg">
        <summary className="p-4 cursor-pointer text-frost font-medium hover:bg-surface/70 rounded-lg">
          What do PvE and PvP mean?
        </summary>
        <div className="p-4 pt-0 text-sm text-frost-muted space-y-3">
          <div>
            <p className="font-medium text-frost">PvE (Player vs Environment)</p>
            <p>Content where you fight against the game, not other players: Bear Trap, Labyrinth, Exploration</p>
            <p className="text-green-400">Uses Exploration Skills</p>
          </div>
          <div>
            <p className="font-medium text-frost">PvP (Player vs Player)</p>
            <p>Content where you fight against other players: Rallies, Garrison Defense, SvS, Arena, Brothers in Arms</p>
            <p className="text-blue-400">Uses Expedition Skills</p>
          </div>
          <div className="bg-ice/10 p-3 rounded-lg border border-ice/20">
            <p className="font-medium text-ice">Why This Matters</p>
            <ul className="mt-1 space-y-1">
              <li>Some heroes are amazing for PvE but weak in PvP (and vice versa)</li>
              <li>Mia's Exploration skills have RNG damage (great for Bear Trap retries)</li>
              <li>Jessie's Expedition skill (+25% damage) makes her the best rally joiner</li>
            </ul>
          </div>
        </div>
      </details>

      {/* Spending profile advice */}
      <div className="card mb-6 border-ice/30">
        <h3 className="font-medium text-frost mb-3">Investment Tips by Spending Profile</h3>
        <div className="grid gap-3">
          {Object.entries(spendingAdvice).map(([profile, advice]) => (
            <div key={profile} className="bg-surface/50 p-3 rounded-lg">
              <span className="font-medium text-frost uppercase text-sm">{profile}:</span>
              <p className="text-sm text-frost-muted mt-1">{advice}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Generation list */}
      <div className="space-y-2">
        {Object.entries(heroGenerations).map(([gen, data]) => {
          const isExpanded = expandedGens.has(gen);
          const maxCount = data.heroes.filter(h => h.investment.includes('MAX')).length;
          const highCount = data.heroes.filter(h => h.investment.includes('HIGH') && !h.investment.includes('MAX')).length;
          const skipCount = data.heroes.filter(h => h.investment.includes('SKIP')).length;

          return (
            <div key={gen} className="bg-surface/30 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleGen(gen)}
                className="w-full p-4 text-left flex items-center justify-between hover:bg-surface/50 transition-colors"
              >
                <div>
                  <span className="font-bold text-frost">Gen {gen}:</span>
                  <span className="text-frost-muted ml-2">{data.summary}</span>
                </div>
                <div className="flex items-center gap-2">
                  {maxCount > 0 && <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400">{maxCount} MAX</span>}
                  {highCount > 0 && <span className="text-xs px-2 py-0.5 rounded bg-orange-500/20 text-orange-400">{highCount} HIGH</span>}
                  {skipCount > 0 && <span className="text-xs px-2 py-0.5 rounded bg-gray-500/20 text-gray-400">{skipCount} SKIP</span>}
                  <span className="text-frost-muted">{isExpanded ? '▼' : '▶'}</span>
                </div>
              </button>
              {isExpanded && (
                <div className="p-4 pt-0">
                  {data.heroes.map((hero, i) => (
                    <HeroCard key={i} hero={hero} />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AllianceTab() {
  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">Alliance Management (R4/R5)</h2>
      <p className="text-frost-muted mb-6">Essential knowledge for alliance officers and leaders.</p>

      {allianceTips.map((tip, i) => (
        <TipCard
          key={i}
          tip={tip.tip}
          detail={tip.detail}
          priority={tip.priority}
        />
      ))}

      {/* Related mistakes */}
      <h3 className="text-lg font-bold text-frost mt-8 mb-4">Common R4/R5 Mistakes</h3>
      {commonMistakes
        .filter(m => m.category === 'Alliance')
        .map((mistake, i) => (
          <TipCard
            key={i}
            tip={`Mistake: ${mistake.mistake}`}
            detail={`Fix: ${mistake.correction}`}
            priority="critical"
          />
        ))}
    </div>
  );
}

function CommonMistakesTab() {
  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">Common Mistakes</h2>
      <p className="text-frost-muted mb-6">Things players do wrong that cost them progress or battles.</p>

      {commonMistakes.map((mistake, i) => (
        <TipCard
          key={i}
          tip={mistake.mistake}
          detail={`Do this: ${mistake.correction}`}
          priority="critical"
          categoryBadge={mistake.category}
        />
      ))}
    </div>
  );
}

function ByCategoryTab() {
  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">All Tips by Category</h2>
      <p className="text-frost-muted mb-6">Browse all tips organized by topic. Click to expand each category.</p>

      <div className="space-y-2">
        {Object.entries(categoryTips).map(([catId, category]) => (
          <details key={catId} className="bg-surface/30 rounded-lg">
            <summary className="p-4 cursor-pointer hover:bg-surface/50 rounded-lg flex items-center justify-between">
              <span className="font-medium text-frost">
                {category.icon} {category.name}
                <span className="text-frost-muted text-sm ml-2">({category.tips.length} tips)</span>
              </span>
            </summary>
            <div className="p-4 pt-0">
              {category.tips
                .sort((a, b) => {
                  const order = { critical: 0, high: 1, medium: 2, low: 3 };
                  return order[a.priority] - order[b.priority];
                })
                .map((tip, i) => (
                  <TipCard
                    key={i}
                    tip={tip.tip}
                    detail={tip.detail}
                    priority={tip.priority}
                  />
                ))}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}

export default function QuickTipsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('critical');

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'critical', label: 'Critical Tips' },
    { key: 'hidden-gems', label: 'Hidden Gems' },
    { key: 'hero-investment', label: 'Hero Investment' },
    { key: 'alliance', label: 'Alliance (R4/R5)' },
    { key: 'mistakes', label: 'Common Mistakes' },
    { key: 'by-category', label: 'By Category' },
  ];

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Quick Tips & Cheat Sheet</h1>
          <p className="text-frost-muted mt-2">
            Key game knowledge in one place. The stuff most players get wrong.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6 border-b border-surface-border pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-ice text-background'
                  : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="mb-8">
          {activeTab === 'critical' && <CriticalTipsTab />}
          {activeTab === 'hidden-gems' && <HiddenGemsTab />}
          {activeTab === 'hero-investment' && <HeroInvestmentTab />}
          {activeTab === 'alliance' && <AllianceTab />}
          {activeTab === 'mistakes' && <CommonMistakesTab />}
          {activeTab === 'by-category' && <ByCategoryTab />}
        </div>

        {/* Footer */}
        <div className="text-center border-t border-surface-border pt-6">
          <p className="text-sm text-frost-muted mb-4">
            {criticalTips.length} critical tips | {hiddenGems.length} hidden gems | {Object.keys(heroGenerations).length} generations | {commonMistakes.length} common mistakes
          </p>
          <button
            onClick={() => window.print()}
            className="btn-secondary"
          >
            Print Cheat Sheet
          </button>
        </div>
      </div>
    </PageLayout>
  );
}
