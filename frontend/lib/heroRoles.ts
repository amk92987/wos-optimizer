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
  "Gina": [{ role: "Stamina Saver", detail: "-20% stamina (hunts/intel)", color: "#F39C12" }],

  // Research & Building
  "Jasser": [
    { role: "Attack Joiner", detail: "+25% DMG dealt", color: "#E74C3C" },
    { role: "Research", detail: "+15% research speed", color: "#9B59B6" },
  ],
  "Zinman": [{ role: "Construction", detail: "+15% build speed, -15% cost", color: "#E67E22" }],

  // Rally/Combat - Gen 1
  "Jessie": [{ role: "BEST Attack Joiner", detail: "+25% DMG dealt (all)", color: "#E74C3C" }],
  "Seo-yoon": [
    { role: "Attack Joiner", detail: "+25% ATK (all)", color: "#E74C3C" },
    { role: "Healing", detail: "+50% infirmary speed", color: "#2ECC71" },
  ],
  "Sergey": [{ role: "BEST Garrison Joiner", detail: "-20% DMG taken (all)", color: "#3498DB" }],
  "Jeronimo": [{ role: "BEST Rally Leader", detail: "+25% DMG, +25% ATK to all", color: "#F1C40F" }],
  "Natalia": [{ role: "Rally Leader", detail: "+25% DMG, +25% ATK to all", color: "#F1C40F" }],
  "Bahiti": [{ role: "Early Joiner", detail: "-20% DMG taken, +50% DMG dealt", color: "#E74C3C" }],
  "Patrick": [{ role: "Early Joiner", detail: "+25% HP, +25% ATK (all)", color: "#E74C3C" }],

  // === GENERATION 2 ===
  "Flint": [{ role: "Rally Leader", detail: "+25% ATK, +25% Lethality, +100% Inf DMG", color: "#F1C40F" }],
  "Philly": [{ role: "BEST Healer", detail: "Essential for exploration/PvE", color: "#2ECC71" }],
  "Alonso": [{ role: "Rally Support", detail: "+50% Lethality, -50% enemy DMG", color: "#9B59B6" }],

  // === GENERATION 3 ===
  "Logan": [{ role: "BEST Defender", detail: "Essential for garrison defense", color: "#3498DB" }],
  "Mia": [{ role: "Rally Support", detail: "+50% DMG taken debuff, +50% DMG dealt", color: "#9B59B6" }],
  "Greg": [{ role: "Rally Support", detail: "+40% DMG dealt, +25% HP (all)", color: "#9B59B6" }],

  // === GENERATION 4 ===
  "Ahmose": [{ role: "Defensive Infantry", detail: "Shield + 30% DMG reflect", color: "#3498DB" }],
  "Reina": [{ role: "Rally Support", detail: "+30% normal ATK DMG, +20% dodge", color: "#9B59B6" }],
  "Lynn": [{ role: "Rally Support", detail: "+50% DMG dealt, -20% enemy DMG", color: "#9B59B6" }],

  // === GENERATION 5 ===
  "Hector": [{ role: "Rally Leader", detail: "-50% DMG taken, +200% Inf/Marks DMG", color: "#F1C40F" }],
  "Norah": [{ role: "TOP Rally Joiner", detail: "+100% extra DMG (Sneak Strike)", color: "#E74C3C" }],
  "Gwen": [{ role: "Rally Support", detail: "+25% DMG taken debuff on enemies", color: "#9B59B6" }],

  // === GENERATION 6 ===
  "Wu Ming": [{ role: "Rally Support", detail: "+25% ATK, +20% Crit", color: "#9B59B6" }],
  "Renee": [{ role: "Rally Support", detail: "+150% DMG to marked targets", color: "#9B59B6" }],
  "Wayne": [{ role: "Rally Support", detail: "+100% extra attack, +25% Crit", color: "#9B59B6" }],

  // === GENERATION 7 ===
  "Edith": [{ role: "Excellent Joiner", detail: "+25% HP, Marks DEF, Lancer DMG", color: "#E74C3C" }],
  "Gordon": [{ role: "Rally Support", detail: "+100% Lancer DMG", color: "#9B59B6" }],
  "Bradley": [{ role: "TOP PvE Marksman", detail: "+25% ATK, +30% DMG (all)", color: "#2ECC71" }],

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
  "Blanchette": [{ role: "Rally Support", detail: "+25% ATK, +60% Inf DMG", color: "#9B59B6" }],

  // === GENERATION 11 ===
  "Eleonora": [{ role: "Rally Support", detail: "+100% Inf DMG, -25% enemy ATK", color: "#9B59B6" }],
  "Lloyd": [{ role: "Lethality Specialist", detail: "+50% Lethality, -20% enemy Leth", color: "#9B59B6" }],
  "Rufus": [{ role: "Rally Support", detail: "+60% Inf DMG, -50% enemy Lethality", color: "#9B59B6" }],

  // === GENERATION 12 ===
  "Hervor": [{ role: "Rally Leader", detail: "+25% DMG, +100% Inf DMG, -30% Inf DMG taken", color: "#F1C40F" }],
  "Karol": [{ role: "Rally Support", detail: "-20% DMG taken, +25% ATK (all)", color: "#9B59B6" }],
  "Ligeia": [{ role: "Rally Support", detail: "+100% Marks DMG, +50% armor pierce", color: "#9B59B6" }],

  // === GENERATION 13+ ===
  "Gisela": [{ role: "Rally Support", detail: "+100% Inf DMG", color: "#9B59B6" }],
  "Flora": [{ role: "Rally Support", detail: "+100% Lancer DMG, +15% Inf/Marks buffs", color: "#9B59B6" }],
  "Vulcanus": [{ role: "Rally Support", detail: "High damage output", color: "#9B59B6" }],

  // === GENERATION 14 ===
  "Dominic": [{ role: "Rally Support", detail: "+100% Lancer DMG, +15% Inf/Marks buffs", color: "#9B59B6" }],
  "Cara": [{ role: "Rally Support", detail: "+30% normal ATK DMG, +100% Marks DMG", color: "#9B59B6" }],
  "Elif": [{ role: "Rally Support", detail: "Strong marksman support", color: "#9B59B6" }],
};

/**
 * Get hero roles by name
 */
export function getHeroRoles(heroName: string): HeroRole[] | null {
  return HERO_ROLES[heroName] || null;
}
