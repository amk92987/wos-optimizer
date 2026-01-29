/**
 * Hero role data - what each hero is good for beyond combat
 * Each hero can have multiple roles
 */

export interface HeroRole {
  role: string;
  detail: string;
  color: string;
}

export const HERO_ROLES: Record<string, HeroRole[]> = {
  // === GENERATION 1 ===
  // Gatherers
  "Smith": [{ role: "Gatherer", detail: "Iron", color: "#95A5A6" }],
  "Eugene": [{ role: "Gatherer", detail: "Wood", color: "#8B4513" }],
  "Charlie": [{ role: "Gatherer", detail: "Coal", color: "#34495E" }],
  "Cloris": [{ role: "Gatherer", detail: "Meat", color: "#E74C3C" }],

  // Stamina/Intel
  "Gina": [
    { role: "Stamina Saver", detail: "-20% stamina (hunts/intel)", color: "#F39C12" },
    { role: "Hunt Speed", detail: "+100% wilderness march speed. Pair with Lumak for fastest hunts", color: "#2ECC71" },
  ],

  // Research & Building
  "Jasser": [
    { role: "Attack Joiner", detail: "+25% DMG dealt", color: "#E74C3C" },
    { role: "Research", detail: "+15% research speed", color: "#9B59B6" },
  ],
  "Zinman": [{ role: "Construction", detail: "+15% build speed, -15% cost", color: "#E67E22" }],

  // Hunting
  "Lumak Bokan": [
    { role: "Hunt Speed", detail: "+100% hunting march speed. Pair with Gina for fastest hunts", color: "#2ECC71" },
  ],

  // Rally/Combat - Gen 1
  "Jessie": [{ role: "BEST Attack Joiner", detail: "+25% DMG dealt (all)", color: "#E74C3C" }],
  "Seo-yoon": [
    { role: "Attack Joiner", detail: "+25% ATK (all)", color: "#E74C3C" },
    { role: "Healing", detail: "+50% infirmary speed", color: "#2ECC71" },
  ],
  "Sergey": [{ role: "BEST Garrison Joiner", detail: "-20% DMG taken (all)", color: "#3498DB" }],
  "Jeronimo": [{ role: "BEST Rally Leader", detail: "+25% DMG, +25% ATK to all", color: "#F1C40F" }],
  "Natalia": [
    { role: "Rally Leader", detail: "+25% DMG, +25% ATK to all", color: "#F1C40F" },
    { role: "Sustain Tank", detail: "Feral Protection: 40% chance to reduce damage taken by 10-50%. Great for extended fights and garrison defense", color: "#3498DB" },
  ],
  "Bahiti": [
    { role: "Early Joiner", detail: "-20% DMG taken, +50% DMG dealt", color: "#E74C3C" },
    { role: "F2P Bear Trap", detail: "Fluorescence: 50% chance of +10-50% damage for all troops. Similar RNG mechanics to Mia but Gen 1", color: "#F39C12" },
  ],
  "Patrick": [
    { role: "Early Joiner", detail: "+25% HP, +25% ATK (all)", color: "#E74C3C" },
    { role: "Early Utility", detail: "Super Nutrients: +25% HP for all troops. Caloric Booster: +25% Attack. Solid early-game buffs", color: "#2ECC71" },
  ],

  // === GENERATION 2 ===
  "Flint": [
    { role: "Rally Leader", detail: "+25% ATK, +25% Lethality, +100% Inf DMG", color: "#F1C40F" },
    { role: "Infantry DPS", detail: "Pyromaniac: +100% Infantry Damage. Immolation: +25% Lethality for all troops. High damage output", color: "#E74C3C" },
  ],
  "Philly": [{ role: "BEST Healer", detail: "Essential for exploration/PvE until Gen 13 Flora", color: "#2ECC71" }],
  "Alonso": [
    { role: "Rally Support", detail: "+50% Lethality, -50% enemy DMG", color: "#9B59B6" },
    { role: "Poison DPS", detail: "Poison Harpoon: 50% chance to deal 10-50% additional damage. Iron Strength: 20% chance to reduce enemy damage", color: "#E74C3C" },
  ],

  // === GENERATION 3 ===
  "Logan": [
    { role: "BEST Defender", detail: "Essential for garrison defense", color: "#3498DB" },
    { role: "Garrison Sustain", detail: "Lion Intimidation: -20% enemy ATK. Leader Inspiration: +20% DEF for all troops", color: "#3498DB" },
  ],
  "Mia": [
    { role: "Bear Expert", detail: "Best hero for Bear Trap event. All 3 skills work regardless of Lancer count", color: "#F39C12" },
    { role: "Rally Support", detail: "+50% DMG taken debuff, +50% DMG dealt", color: "#9B59B6" },
    { role: "Bear Trap Star", detail: "Bad Luck Streak (+50% enemy dmg taken) + Lucky Charm (+50% extra dmg) = massive burst with RNG", color: "#F39C12" },
  ],
  "Greg": [
    { role: "Rally Support", detail: "+40% DMG dealt, +25% HP (all)", color: "#9B59B6" },
    { role: "Arena Strong", detail: "Law and Order gives guaranteed +25% HP to all troops. Deterrence of Law reduces enemy damage. Great for sustained PvP fights", color: "#E91E63" },
  ],

  // === GENERATION 4 ===
  "Ahmose": [{ role: "Defensive Infantry", detail: "Shield + 30% DMG reflect", color: "#3498DB" }],
  "Reina": [{ role: "Rally Support", detail: "+30% normal ATK DMG, +20% dodge", color: "#9B59B6" }],
  "Lynn": [{ role: "Rally Support", detail: "+50% DMG dealt, -20% enemy DMG", color: "#9B59B6" }],

  // === GENERATION 5 ===
  "Hector": [
    { role: "Rally Leader", detail: "-50% DMG taken, +200% Inf/Marks DMG", color: "#F1C40F" },
    { role: "Bear Trap Tank", detail: "Rampant: +100-200% Infantry damage AND +20-100% Marksman damage. Great for Mia Bear Trap comps", color: "#F39C12" },
  ],
  "Norah": [{ role: "Best Rally Joiner", detail: "Sneak Strike: 20% chance for 20-100% extra damage to ALL enemies. Top-tier rally support", color: "#F1C40F" }],
  "Gwen": [{ role: "Rally Support", detail: "+25% DMG taken debuff on enemies", color: "#9B59B6" }],

  // === GENERATION 6 ===
  "Wu Ming": [
    { role: "TOP 3 Hero", detail: "-25% ALL damage taken is unmatched sustain. Best defensive Infantry ever", color: "#F1C40F" },
    { role: "Rally Support", detail: "+25% ATK, +20% Crit", color: "#9B59B6" },
  ],
  "Renee": [{ role: "Rally Support", detail: "+150% DMG to marked targets", color: "#9B59B6" }],
  "Wayne": [
    { role: "Rally Support", detail: "+100% extra attack, +25% Crit", color: "#9B59B6" },
    { role: "Mia Synergy", detail: "Thunder Strike: Extra attack every 4 turns + Fleet: 5-25% crit rate. Pairs with Mia for explosive Bear Trap damage", color: "#F39C12" },
  ],

  // === GENERATION 7 ===
  "Edith": [{ role: "Excellent Joiner", detail: "+25% HP, Marks DEF, Lancer DMG", color: "#E74C3C" }],
  "Gordon": [
    { role: "Rally Support", detail: "+100% Lancer DMG", color: "#9B59B6" },
    { role: "Poison Specialist", detail: "Poison damage is devastating in rallies. Best Lancer for sustained damage over time", color: "#2ECC71" },
  ],
  "Bradley": [
    { role: "TOP PvE Marksman", detail: "+25% ATK, +30% DMG (all)", color: "#2ECC71" },
    { role: "Attack Booster", detail: "Veteran's Might: +25% Attack for all troops. Tactical Assistance: +30% offense boost every 4 turns", color: "#E74C3C" },
  ],

  // === GENERATION 8 ===
  "Gatot": [{ role: "Rally Support", detail: "+100% Inf DMG, +70% Inf DEF", color: "#9B59B6" }],
  "Sonya": [{ role: "Rally Support", detail: "+20% DMG, +75% Lancer DMG", color: "#9B59B6" }],
  "Hendrik": [{ role: "Rally Support", detail: "+100% Marks DMG, +50% Crit", color: "#9B59B6" }],

  // === GENERATION 9 ===
  "Magnus": [{ role: "Rally Leader", detail: "+100% Inf DMG, high survivability", color: "#F1C40F" }],
  "Fred": [{ role: "Rally Support", detail: "-50% enemy Lethality, +50% Lethality", color: "#9B59B6" }],
  "Xura": [{ role: "TOP Rally Leader", detail: "-50% DMG taken, +100% Marks DMG", color: "#F1C40F" }],

  // === GENERATION 10 ===
  "Gregory": [{ role: "Rally Support", detail: "+25% ATK, +50% Inf DMG", color: "#9B59B6" }],
  "Freya": [{ role: "Rally Support", detail: "+15% Inf/Marks DEF & DMG, +25% DMG", color: "#9B59B6" }],
  "Blanchette": [
    { role: "BEST Marksman", detail: "S+ expedition tier. Highest DPS output possible", color: "#F1C40F" },
    { role: "Crit DPS", detail: "Crimson Sniper: +20% Crit Rate and +50% Crit Damage for all troops. Blood Hunter: +25% vs wounded. Top Marksman damage", color: "#E74C3C" },
  ],

  // === GENERATION 11 ===
  "Eleonora": [{ role: "Rally Support", detail: "+100% Inf DMG, -25% enemy ATK", color: "#9B59B6" }],
  "Lloyd": [
    { role: "Lethality Specialist", detail: "+50% Lethality, -20% enemy Leth", color: "#9B59B6" },
    { role: "Lethality King", detail: "Ingenious Mastery: +50% Lethality for all troops. Bird Invasion: -20% enemy Lethality. Top late-game Lancer", color: "#F1C40F" },
  ],
  "Rufus": [{ role: "Rally Support", detail: "+60% Inf DMG, -50% enemy Lethality", color: "#9B59B6" }],

  // === GENERATION 12 ===
  "Hervor": [
    { role: "Rally Leader", detail: "+25% DMG, +100% Inf DMG, -30% Inf DMG taken", color: "#F1C40F" },
    { role: "Top Infantry", detail: "Call For Blood: +25% damage for all. Undying: -30% Infantry damage taken. Battlethirsty: +100% Infantry damage. S+ tier Infantry", color: "#E74C3C" },
  ],
  "Karol": [{ role: "Rally Support", detail: "-20% DMG taken, +25% ATK (all)", color: "#9B59B6" }],
  "Ligeia": [{ role: "Rally Support", detail: "+100% Marks DMG, +50% armor pierce", color: "#9B59B6" }],

  // === GENERATION 13+ ===
  "Gisela": [{ role: "Rally Support", detail: "+100% Inf DMG", color: "#9B59B6" }],
  "Flora": [
    { role: "NEW Best Healer", detail: "Replaces Philly for PvE content. Massive healing output", color: "#2ECC71" },
    { role: "Rally Support", detail: "+100% Lancer DMG, +15% Inf/Marks buffs", color: "#9B59B6" },
  ],
  "Vulcanus": [
    { role: "S+ Marksman", detail: "Rivals Blanchette for damage output. Two S+ Marksmen = devastating DPS", color: "#F1C40F" },
    { role: "Rally Support", detail: "High damage output", color: "#9B59B6" },
  ],

  // === GENERATION 14 ===
  "Dominic": [{ role: "Rally Support", detail: "+100% Lancer DMG, +15% Inf/Marks buffs", color: "#9B59B6" }],
  "Cara": [{ role: "Rally Support", detail: "+30% normal ATK DMG, +100% Marks DMG", color: "#9B59B6" }],
  "Elif": [
    { role: "S+ Infantry", detail: "Latest S+ Infantry. Fourth S+ Infantry option. Excellent skills", color: "#F1C40F" },
    { role: "Rally Support", detail: "Strong infantry support", color: "#9B59B6" },
  ],
};

/**
 * Get hero roles by name
 */
export function getHeroRoles(heroName: string): HeroRole[] | null {
  return HERO_ROLES[heroName] || null;
}
