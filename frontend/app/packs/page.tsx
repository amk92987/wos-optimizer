'use client';

import { useState, useMemo } from 'react';
import PageLayout from '@/components/PageLayout';

// Hide number input spinners
const hideSpinnerStyle = `
  .no-spinner::-webkit-outer-spin-button,
  .no-spinner::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  .no-spinner[type=number] {
    -moz-appearance: textfield;
  }
`;

// Tier colors
const TIER_COLORS: Record<string, string> = {
  S: '#FFD700',
  A: '#9B59B6',
  B: '#3498DB',
  C: '#95A5A6',
  D: '#E74C3C',
};

// Price options
const PRICE_OPTIONS = [0.99, 1.99, 2.99, 4.99, 9.99, 14.99, 19.99, 29.99, 49.99, 99.99];

interface PackItem {
  id: string;
  name: string;
  image?: string;
  emoji?: string;
  fsValue: number;
  tier: string;
  desc: string;
  category: 'unique' | 'currency' | 'speedups' | 'resources';
  type?: string;
  duration?: string;
  denom?: string;
}

// All pack items organized by category
const PACK_ITEMS: Record<string, { label: string; items: PackItem[]; isSpeedupGrid?: boolean; isResourceGrid?: boolean }> = {
  hero: {
    label: 'Hero Items',
    items: [
      { id: 'mythic_shard', name: 'Mythic Shards', image: 'mythic_hero_shard.png', fsValue: 33, tier: 'A', desc: 'Gold/orange shards for Mythic heroes', category: 'unique' },
      { id: 'specific_mythic_shard', name: 'Specific Hero Shards', image: 'mythic_hero_shard.png', fsValue: 40, tier: 'A', desc: 'Shards for specific heroes (Molly, etc.)', category: 'unique' },
      { id: 'epic_shard', name: 'Epic Shards', image: 'epic_hero_shard.png', fsValue: 17, tier: 'B', desc: 'Purple shards for Epic heroes', category: 'unique' },
      { id: 'rare_shard', name: 'Rare Shards', image: 'rare_hero_shard.png', fsValue: 8, tier: 'C', desc: 'Blue shards for Rare heroes', category: 'unique' },
      { id: 'hero_xp_1k', name: 'Hero XP (1k)', image: 'hero_xp.png', fsValue: 1, tier: 'C', desc: '1000 experience points', category: 'unique' },
      { id: 'hero_xp_5k', name: 'Hero XP (5k)', image: 'hero_xp.png', fsValue: 5, tier: 'C', desc: '5000 experience points', category: 'unique' },
      { id: 'mythic_exploration_manual', name: 'Mythic Explore Manual', image: 'mythic_exploration_manual.png', fsValue: 3.7, tier: 'B', desc: 'Exploration skills for Mythic heroes', category: 'unique' },
      { id: 'mythic_expedition_manual', name: 'Mythic Expedition Manual', image: 'mythic_expedition_manual.png', fsValue: 3.7, tier: 'B', desc: 'Expedition skills for Mythic heroes', category: 'unique' },
      { id: 'epic_exploration_manual', name: 'Epic Explore Manual', image: 'epic_exploration_manual.png', fsValue: 17, tier: 'B', desc: 'Exploration skills for Epic heroes', category: 'unique' },
      { id: 'epic_expedition_manual', name: 'Epic Expedition Manual', image: 'epic_expedition_manual.png', fsValue: 17, tier: 'B', desc: 'Expedition skills for Epic heroes', category: 'unique' },
      { id: 'rare_exploration_manual', name: 'Rare Explore Manual', image: 'rare_exploration_manual.png', fsValue: 5, tier: 'C', desc: 'Exploration skills for Rare heroes', category: 'unique' },
      { id: 'rare_expedition_manual', name: 'Rare Expedition Manual', image: 'rare_expedition_manual.png', fsValue: 5, tier: 'C', desc: 'Expedition skills for Rare heroes', category: 'unique' },
    ],
  },
  heroGear: {
    label: 'Hero Gear',
    items: [
      { id: 'essence_stone', name: 'Essence Stones', image: 'essence_stone.png', fsValue: 22, tier: 'A', desc: 'For Mythic gear mastery. $0.22 each', category: 'unique' },
      { id: 'mithril', name: 'Mithril', image: 'mithril.png', fsValue: 141, tier: 'S', desc: 'Rare material for gear empowerment. $1.41 each', category: 'unique' },
      { id: 'xp_component', name: 'Hero Gear XP (per 100)', image: 'xp_component.png', fsValue: 13, tier: 'B', desc: 'Enhancement XP components', category: 'unique' },
      { id: 'lucky_hero_gear_chest', name: 'Lucky Gear Chest', image: 'mythic_hero_gear_chest.png', fsValue: 22, tier: 'A', desc: 'Random hero gear pieces', category: 'unique' },
      { id: 'epic_hero_gear_chest', name: 'Epic Gear Chest', image: 'epic_hero_gear_chest.png', fsValue: 12, tier: 'B', desc: 'Contains random epic hero gear pieces', category: 'unique' },
      { id: 'hero_gear_chest', name: 'Hero Gear Chest', image: 'hero_gear_chest.png', fsValue: 8, tier: 'C', desc: 'Contains random hero gear pieces', category: 'unique' },
    ],
  },
  customGear: {
    label: 'Custom Gear',
    items: [
      { id: 'custom_hero_gear_s1', name: 'Custom Gear S1', image: 'mythic_hero_gear_chest.png', fsValue: 22, tier: 'B', desc: 'Choose hero gear (Gen 1)', category: 'unique' },
      { id: 'custom_hero_gear_s2', name: 'Custom Gear S2', image: 'mythic_hero_gear_chest.png', fsValue: 24, tier: 'B', desc: 'Choose hero gear (Gen 2)', category: 'unique' },
      { id: 'custom_hero_gear_s3', name: 'Custom Gear S3', image: 'mythic_hero_gear_chest.png', fsValue: 26, tier: 'B', desc: 'Choose hero gear (Gen 3)', category: 'unique' },
      { id: 'custom_hero_gear_s4', name: 'Custom Gear S4', image: 'mythic_hero_gear_chest.png', fsValue: 28, tier: 'B', desc: 'Choose hero gear (Gen 4)', category: 'unique' },
      { id: 'custom_hero_gear_s5', name: 'Custom Gear S5', image: 'mythic_hero_gear_chest.png', fsValue: 30, tier: 'B', desc: 'Choose hero gear (Gen 5)', category: 'unique' },
      { id: 'custom_hero_gear_s6', name: 'Custom Gear S6', image: 'mythic_hero_gear_chest.png', fsValue: 32, tier: 'A', desc: 'Choose hero gear (Gen 6)', category: 'unique' },
      { id: 'custom_hero_gear_s7', name: 'Custom Gear S7', image: 'mythic_hero_gear_chest.png', fsValue: 34, tier: 'A', desc: 'Choose hero gear (Gen 7)', category: 'unique' },
      { id: 'custom_hero_gear_s8', name: 'Custom Gear S8', image: 'mythic_hero_gear_chest.png', fsValue: 36, tier: 'A', desc: 'Choose hero gear (Gen 8)', category: 'unique' },
      { id: 'custom_hero_gear_s9', name: 'Custom Gear S9', image: 'mythic_hero_gear_chest.png', fsValue: 38, tier: 'A', desc: 'Choose hero gear (Gen 9)', category: 'unique' },
      { id: 'custom_hero_gear_s10', name: 'Custom Gear S10', image: 'mythic_hero_gear_chest.png', fsValue: 40, tier: 'A', desc: 'Choose hero gear (Gen 10)', category: 'unique' },
      { id: 'custom_hero_gear_s11', name: 'Custom Gear S11', image: 'mythic_hero_gear_chest.png', fsValue: 42, tier: 'A', desc: 'Choose hero gear (Gen 11)', category: 'unique' },
      { id: 'custom_hero_gear_s12', name: 'Custom Gear S12', image: 'mythic_hero_gear_chest.png', fsValue: 44, tier: 'A', desc: 'Choose hero gear (Gen 12)', category: 'unique' },
      { id: 'custom_hero_gear_s13', name: 'Custom Gear S13', image: 'mythic_hero_gear_chest.png', fsValue: 46, tier: 'S', desc: 'Choose hero gear (Gen 13)', category: 'unique' },
      { id: 'custom_hero_gear_s14', name: 'Custom Gear S14', image: 'mythic_hero_gear_chest.png', fsValue: 48, tier: 'S', desc: 'Choose hero gear (Gen 14)', category: 'unique' },
    ],
  },
  chiefGear: {
    label: 'Chief Gear',
    items: [
      { id: 'hardened_alloy', name: 'Hardened Alloy', image: 'hardened_alloy.png', fsValue: 0.067, tier: 'C', desc: 'Primary material for chief gear', category: 'unique' },
      { id: 'polishing_solution', name: 'Polishing Solution', image: 'polishing_solution.png', fsValue: 6.7, tier: 'B', desc: '1 Polish = 100 Alloy in value', category: 'unique' },
      { id: 'design_plans', name: 'Design Plans', image: 'design_plans.png', fsValue: 10, tier: 'B', desc: 'Blueprints for Blue+ quality chief gear', category: 'unique' },
      { id: 'charm_design', name: 'Charm Designs', image: 'charm_design.png', fsValue: 22, tier: 'A', desc: 'Primary material for Chief Charm upgrades', category: 'unique' },
      { id: 'charm_guide', name: 'Charm Guides', image: 'charm_guide.png', fsValue: 6.5, tier: 'B', desc: 'Secondary material for Chief Charm upgrades', category: 'unique' },
      { id: 'chief_gear_chest', name: 'Chief Gear Chest', image: 'chief_gear_chest.png', fsValue: 8, tier: 'C', desc: 'Contains chief gear materials', category: 'unique' },
    ],
  },
  currency: {
    label: 'Gems & VIP',
    items: [
      { id: 'gems', name: 'Gems', image: 'gems.png', fsValue: 0.033, tier: 'A', desc: 'Premium currency (30 gems = 1 FS)', category: 'currency' },
      { id: 'stamina', name: 'Stamina', image: 'stamina.png', fsValue: 1, tier: 'A', desc: 'Energy for beasts and exploration', category: 'currency' },
      { id: 'fire_crystal', name: 'Fire Crystals', image: 'fire_crystal.png', fsValue: 1.7, tier: 'B', desc: 'Currency for Furnace upgrades', category: 'currency' },
      { id: 'vip_xp_10', name: 'VIP XP 10', image: 'vip_points.png', fsValue: 0.7, tier: 'C', desc: '10 VIP experience points', category: 'currency' },
      { id: 'vip_xp_100', name: 'VIP XP 100', image: 'vip_points.png', fsValue: 7, tier: 'B', desc: '100 VIP experience points', category: 'currency' },
      { id: 'vip_xp_1000', name: 'VIP XP 1000', image: 'vip_points.png', fsValue: 70, tier: 'A', desc: '1000 VIP experience points', category: 'currency' },
      { id: 'vip_xp_10000', name: 'VIP XP 10000', image: 'vip_points.png', fsValue: 700, tier: 'S', desc: '10000 VIP experience points', category: 'currency' },
      { id: 'vip_time', name: 'VIP Time (24h)', image: 'vip_time.png', fsValue: 8, tier: 'B', desc: 'Grants temporary VIP benefits', category: 'currency' },
      { id: 'gold_key', name: 'Gold Keys', image: 'gold_key.png', fsValue: 50, tier: 'A', desc: 'Opens gold chests', category: 'currency' },
      { id: 'platinum_key', name: 'Platinum Keys', image: 'platinum_key.png', fsValue: 17, tier: 'B', desc: 'Opens platinum chests', category: 'currency' },
      { id: 'mystery_badge', name: 'Mystery Badges', image: 'mystery_badge.png', fsValue: 0.1, tier: 'B', desc: 'Event currency for mystery shop', category: 'currency' },
    ],
  },
  warItems: {
    label: 'War & Utility',
    items: [
      { id: 'advanced_teleport', name: 'Advanced Teleport', image: 'advanced_teleporter.png', fsValue: 67, tier: 'A', desc: 'Teleport to any location', category: 'unique' },
      { id: 'random_teleport', name: 'Random Teleport', image: 'random_teleporter.png', fsValue: 33, tier: 'B', desc: 'Teleport to random location', category: 'unique' },
      { id: 'alliance_teleport', name: 'Alliance Teleport', image: 'alliance_teleporter.png', fsValue: 67, tier: 'A', desc: 'Teleport near alliance territory', category: 'unique' },
      { id: 'transfer_pass', name: 'Transfer Pass', image: 'transfer_pass.png', fsValue: 100, tier: 'S', desc: 'Transfer to another state', category: 'unique' },
      { id: 'march_accelerator_1', name: 'March Accelerator I', image: 'march_accelerator.png', fsValue: 10, tier: 'B', desc: 'Speeds up march by 50%', category: 'unique' },
      { id: 'march_accelerator_2', name: 'March Accelerator II', image: 'march_accelerator_2.png', fsValue: 20, tier: 'B', desc: 'Speeds up march by 100%', category: 'unique' },
      { id: 'peace_shield_8h', name: 'Peace Shield (8hr)', image: 'shield.png', fsValue: 20, tier: 'B', desc: 'Protect city for 8 hours', category: 'unique' },
      { id: 'peace_shield_24h', name: 'Peace Shield (24hr)', image: 'shield.png', fsValue: 50, tier: 'A', desc: 'Protect city for 24 hours', category: 'unique' },
      { id: 'counter_recon_2h', name: 'Counter Recon (2hr)', image: 'counter_recon.png', fsValue: 9, tier: 'C', desc: 'Hide troop info for 2 hours', category: 'unique' },
      { id: 'counter_recon_8h', name: 'Counter Recon (8hr)', image: 'counter_recon.png', fsValue: 35, tier: 'B', desc: 'Hide troop info for 8 hours', category: 'unique' },
      { id: 'expedition_recall', name: 'Expedition Recall', emoji: '↩️', fsValue: 17, tier: 'B', desc: 'Recall troops instantly', category: 'unique' },
      { id: 'accessory_contract', name: 'Accessory Contract', emoji: '📜', fsValue: 50, tier: 'A', desc: 'General accessory construction', category: 'unique' },
    ],
  },
  pets: {
    label: 'Pets',
    items: [
      { id: 'pet_food', name: 'Pet Food', image: 'pet_food.png', fsValue: 0.024, tier: 'C', desc: 'For leveling up pets', category: 'unique' },
      { id: 'taming_manual', name: 'Taming Manuals', image: 'taming_manual.png', fsValue: 4, tier: 'B', desc: 'Core material for pet advancement', category: 'unique' },
      { id: 'energizing_potion', name: 'Energizing Potion', image: 'energizing_potion.png', fsValue: 14, tier: 'A', desc: 'Pet advancement (Lv.30+)', category: 'unique' },
      { id: 'strengthening_serum', name: 'Strengthening Serum', image: 'strengthening_serum.png', fsValue: 28, tier: 'A', desc: 'Pet advancement (Lv.50+)', category: 'unique' },
      { id: 'common_wild_mark', name: 'Common Wild Mark', image: 'common_wild_mark.png', fsValue: 17, tier: 'B', desc: 'Basic pet refinement', category: 'unique' },
      { id: 'advanced_wild_mark', name: 'Advanced Wild Mark', image: 'advanced_wild_mark.png', fsValue: 71, tier: 'S', desc: 'Advanced pet refinement. $0.71 each', category: 'unique' },
      { id: 'pet_materials_chest', name: 'Pet Materials Chest', image: 'pet_materials_chest.png', fsValue: 10, tier: 'B', desc: 'Random pet advancement materials', category: 'unique' },
    ],
  },
  boosts: {
    label: 'Boosts',
    items: [
      { id: 'troop_attack_boost_2h', name: 'Troop Attack (2hr)', image: 'troops_attack_up.png', fsValue: 42, tier: 'B', desc: 'Increases troop attack for 2 hours', category: 'unique' },
      { id: 'troop_attack_boost_12h', name: 'Troop Attack (12hr)', image: 'troops_attack_up.png', fsValue: 167, tier: 'A', desc: 'Increases troop attack for 12 hours', category: 'unique' },
      { id: 'troop_defense_boost_2h', name: 'Troop Defense (2hr)', image: 'troops_defense_up.png', fsValue: 42, tier: 'B', desc: 'Increases troop defense for 2 hours', category: 'unique' },
      { id: 'troop_defense_boost_12h', name: 'Troop Defense (12hr)', image: 'troops_defense_up.png', fsValue: 167, tier: 'A', desc: 'Increases troop defense for 12 hours', category: 'unique' },
      { id: 'enemy_attack_down_2h', name: 'Enemy Attack Down (2hr)', image: 'enemy_attack_down.png', fsValue: 42, tier: 'B', desc: 'Reduces enemy attack for 2 hours', category: 'unique' },
      { id: 'enemy_attack_down_12h', name: 'Enemy Attack Down (12hr)', image: 'enemy_attack_down.png', fsValue: 167, tier: 'A', desc: 'Reduces enemy attack for 12 hours', category: 'unique' },
      { id: 'enemy_defense_down_2h', name: 'Enemy Defense Down (2hr)', image: 'enemy_defense_down.png', fsValue: 42, tier: 'B', desc: 'Reduces enemy defense for 2 hours', category: 'unique' },
      { id: 'enemy_defense_down_12h', name: 'Enemy Defense Down (12hr)', image: 'enemy_defense_down.png', fsValue: 167, tier: 'A', desc: 'Reduces enemy defense for 12 hours', category: 'unique' },
      { id: 'gathering_speed_boost_8h', name: 'Gathering Speed (8hr)', image: 'gathering_speed_boost.png', fsValue: 4, tier: 'C', desc: 'Increases gathering speed for 8 hours', category: 'unique' },
      { id: 'gathering_speed_boost_24h', name: 'Gathering Speed (24hr)', image: 'gathering_speed_boost.png', fsValue: 10, tier: 'C', desc: 'Increases gathering speed for 24 hours', category: 'unique' },
      { id: 'training_capacity_boost_2h', name: 'Training Capacity (2hr)', image: 'training_capacity_boost.png', fsValue: 50, tier: 'B', desc: 'Increases troop training capacity', category: 'unique' },
      { id: 'deployment_capacity_boost_2h', name: 'Deployment Cap (2hr)', image: 'deployment_capacity_boost.png', fsValue: 50, tier: 'B', desc: 'Increases march deployment capacity', category: 'unique' },
      { id: 'deployment_capacity_boost_12h', name: 'Deployment Cap (12hr)', image: 'deployment_capacity_boost.png', fsValue: 167, tier: 'A', desc: 'Increases march deployment for 12 hours', category: 'unique' },
      { id: 'rally_boost_2h', name: 'Rally Capacity (2hr)', image: 'rally_boost.png', fsValue: 50, tier: 'B', desc: 'Increases rally troop capacity', category: 'unique' },
      { id: 'rally_boost_12h', name: 'Rally Capacity (12hr)', image: 'rally_boost.png', fsValue: 167, tier: 'A', desc: 'Increases rally capacity for 12 hours', category: 'unique' },
    ],
  },
  speedups: {
    label: 'Speedups',
    isSpeedupGrid: true,
    items: [
      // General speedups
      { id: 'speed_gen_1m', name: 'General 1m', image: 'speedup_general.png', fsValue: 0.24, tier: 'C', desc: 'General speedup - 1 min', category: 'speedups', type: 'general', duration: '1m' },
      { id: 'speed_gen_5m', name: 'General 5m', image: 'speedup_general.png', fsValue: 1.2, tier: 'C', desc: 'General speedup - 5 min', category: 'speedups', type: 'general', duration: '5m' },
      { id: 'speed_gen_10m', name: 'General 10m', image: 'speedup_general.png', fsValue: 2.4, tier: 'C', desc: 'General speedup - 10 min', category: 'speedups', type: 'general', duration: '10m' },
      { id: 'speed_gen_30m', name: 'General 30m', image: 'speedup_general.png', fsValue: 7, tier: 'B', desc: 'General speedup - 30 min', category: 'speedups', type: 'general', duration: '30m' },
      { id: 'speed_gen_1h', name: 'General 1h', image: 'speedup_general.png', fsValue: 14, tier: 'B', desc: 'General speedup - 1 hour', category: 'speedups', type: 'general', duration: '1h' },
      { id: 'speed_gen_3h', name: 'General 3h', image: 'speedup_general.png', fsValue: 42, tier: 'A', desc: 'General speedup - 3 hours', category: 'speedups', type: 'general', duration: '3h' },
      { id: 'speed_gen_8h', name: 'General 8h', image: 'speedup_general.png', fsValue: 112, tier: 'A', desc: 'General speedup - 8 hours', category: 'speedups', type: 'general', duration: '8h' },
      { id: 'speed_gen_24h', name: 'General 24h', image: 'speedup_general.png', fsValue: 336, tier: 'S', desc: 'General speedup - 24 hours', category: 'speedups', type: 'general', duration: '24h' },
      // Construction speedups
      { id: 'speed_build_1m', name: 'Construction 1m', image: 'speedup_construction.png', fsValue: 0.24, tier: 'C', desc: 'Construction speedup - 1 min', category: 'speedups', type: 'construction', duration: '1m' },
      { id: 'speed_build_5m', name: 'Construction 5m', image: 'speedup_construction.png', fsValue: 1.2, tier: 'C', desc: 'Construction speedup - 5 min', category: 'speedups', type: 'construction', duration: '5m' },
      { id: 'speed_build_10m', name: 'Construction 10m', image: 'speedup_construction.png', fsValue: 2.4, tier: 'C', desc: 'Construction speedup - 10 min', category: 'speedups', type: 'construction', duration: '10m' },
      { id: 'speed_build_30m', name: 'Construction 30m', image: 'speedup_construction.png', fsValue: 7, tier: 'B', desc: 'Construction speedup - 30 min', category: 'speedups', type: 'construction', duration: '30m' },
      { id: 'speed_build_1h', name: 'Construction 1h', image: 'speedup_construction.png', fsValue: 14, tier: 'B', desc: 'Construction speedup - 1 hour', category: 'speedups', type: 'construction', duration: '1h' },
      { id: 'speed_build_3h', name: 'Construction 3h', image: 'speedup_construction.png', fsValue: 42, tier: 'A', desc: 'Construction speedup - 3 hours', category: 'speedups', type: 'construction', duration: '3h' },
      { id: 'speed_build_8h', name: 'Construction 8h', image: 'speedup_construction.png', fsValue: 112, tier: 'A', desc: 'Construction speedup - 8 hours', category: 'speedups', type: 'construction', duration: '8h' },
      { id: 'speed_build_24h', name: 'Construction 24h', image: 'speedup_construction.png', fsValue: 336, tier: 'S', desc: 'Construction speedup - 24 hours', category: 'speedups', type: 'construction', duration: '24h' },
      // Research speedups
      { id: 'speed_research_1m', name: 'Research 1m', image: 'speedup_research.png', fsValue: 0.24, tier: 'C', desc: 'Research speedup - 1 min', category: 'speedups', type: 'research', duration: '1m' },
      { id: 'speed_research_5m', name: 'Research 5m', image: 'speedup_research.png', fsValue: 1.2, tier: 'C', desc: 'Research speedup - 5 min', category: 'speedups', type: 'research', duration: '5m' },
      { id: 'speed_research_10m', name: 'Research 10m', image: 'speedup_research.png', fsValue: 2.4, tier: 'C', desc: 'Research speedup - 10 min', category: 'speedups', type: 'research', duration: '10m' },
      { id: 'speed_research_30m', name: 'Research 30m', image: 'speedup_research.png', fsValue: 7, tier: 'B', desc: 'Research speedup - 30 min', category: 'speedups', type: 'research', duration: '30m' },
      { id: 'speed_research_1h', name: 'Research 1h', image: 'speedup_research.png', fsValue: 14, tier: 'B', desc: 'Research speedup - 1 hour', category: 'speedups', type: 'research', duration: '1h' },
      { id: 'speed_research_3h', name: 'Research 3h', image: 'speedup_research.png', fsValue: 42, tier: 'A', desc: 'Research speedup - 3 hours', category: 'speedups', type: 'research', duration: '3h' },
      { id: 'speed_research_8h', name: 'Research 8h', image: 'speedup_research.png', fsValue: 112, tier: 'A', desc: 'Research speedup - 8 hours', category: 'speedups', type: 'research', duration: '8h' },
      { id: 'speed_research_24h', name: 'Research 24h', image: 'speedup_research.png', fsValue: 336, tier: 'S', desc: 'Research speedup - 24 hours', category: 'speedups', type: 'research', duration: '24h' },
      // Training speedups
      { id: 'speed_train_1m', name: 'Training 1m', image: 'speedup_training.png', fsValue: 0.24, tier: 'C', desc: 'Training speedup - 1 min', category: 'speedups', type: 'training', duration: '1m' },
      { id: 'speed_train_5m', name: 'Training 5m', image: 'speedup_training.png', fsValue: 1.2, tier: 'C', desc: 'Training speedup - 5 min', category: 'speedups', type: 'training', duration: '5m' },
      { id: 'speed_train_10m', name: 'Training 10m', image: 'speedup_training.png', fsValue: 2.4, tier: 'C', desc: 'Training speedup - 10 min', category: 'speedups', type: 'training', duration: '10m' },
      { id: 'speed_train_30m', name: 'Training 30m', image: 'speedup_training.png', fsValue: 7, tier: 'B', desc: 'Training speedup - 30 min', category: 'speedups', type: 'training', duration: '30m' },
      { id: 'speed_train_1h', name: 'Training 1h', image: 'speedup_training.png', fsValue: 14, tier: 'B', desc: 'Training speedup - 1 hour', category: 'speedups', type: 'training', duration: '1h' },
      { id: 'speed_train_3h', name: 'Training 3h', image: 'speedup_training.png', fsValue: 42, tier: 'A', desc: 'Training speedup - 3 hours', category: 'speedups', type: 'training', duration: '3h' },
      { id: 'speed_train_8h', name: 'Training 8h', image: 'speedup_training.png', fsValue: 112, tier: 'A', desc: 'Training speedup - 8 hours', category: 'speedups', type: 'training', duration: '8h' },
      { id: 'speed_train_24h', name: 'Training 24h', image: 'speedup_training.png', fsValue: 336, tier: 'S', desc: 'Training speedup - 24 hours', category: 'speedups', type: 'training', duration: '24h' },
      // Healing speedups - VALUE = 0
      { id: 'speed_heal_1m', name: 'Healing 1m', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '1m' },
      { id: 'speed_heal_5m', name: 'Healing 5m', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '5m' },
      { id: 'speed_heal_10m', name: 'Healing 10m', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '10m' },
      { id: 'speed_heal_30m', name: 'Healing 30m', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '30m' },
      { id: 'speed_heal_1h', name: 'Healing 1h', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '1h' },
      { id: 'speed_heal_3h', name: 'Healing 3h', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '3h' },
      { id: 'speed_heal_8h', name: 'Healing 8h', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '8h' },
      { id: 'speed_heal_24h', name: 'Healing 24h', image: 'speedup_healing.png', fsValue: 0, tier: 'D', desc: 'Healing speedup - $0 (batch heal is free!)', category: 'speedups', type: 'healing', duration: '24h' },
    ],
  },
  lateGame: {
    label: 'FC5+ Items',
    items: [
      { id: 'expert_sigil', name: 'Expert Sigils', image: 'common_expert_sigil.png', fsValue: 20, tier: 'A', desc: 'Material for hero expertise trees', category: 'unique' },
      { id: 'lunar_amber', name: 'Lunar Amber', image: 'lunar_amber.png', fsValue: 35, tier: 'A', desc: 'Material for Red+ quality chief gear', category: 'unique' },
      { id: 'charm_secrets', name: 'Charm Secrets', image: 'charm_secrets.png', fsValue: 50, tier: 'S', desc: 'Rare material for L12+ charm upgrades', category: 'unique' },
      { id: 'refined_fire_crystal', name: 'Refined FC', image: 'refined_fire_crystal.png', fsValue: 30, tier: 'A', desc: 'Purified FC for FC6+ upgrades', category: 'unique' },
      { id: 'mythic_decoration', name: 'Mythic Decoration', image: 'mythic_decoration_component.png', fsValue: 56, tier: 'A', desc: 'Material for hero decoration upgrades', category: 'unique' },
    ],
  },
  resources: {
    label: 'Resources',
    isResourceGrid: true,
    items: [
      // Meat
      { id: 'meat_100', name: 'Meat 100', image: 'meat.png', fsValue: 0.00054, tier: 'D', desc: '100 Meat', category: 'resources', type: 'meat', denom: '100' },
      { id: 'meat_1k', name: 'Meat 1k', image: 'meat.png', fsValue: 0.0054, tier: 'D', desc: '1,000 Meat', category: 'resources', type: 'meat', denom: '1k' },
      { id: 'meat_10k', name: 'Meat 10k', image: 'meat.png', fsValue: 0.054, tier: 'D', desc: '10,000 Meat', category: 'resources', type: 'meat', denom: '10k' },
      { id: 'meat_100k', name: 'Meat 100k', image: 'meat.png', fsValue: 0.54, tier: 'D', desc: '100,000 Meat', category: 'resources', type: 'meat', denom: '100k' },
      { id: 'meat_1m', name: 'Meat 1M', image: 'meat.png', fsValue: 5.4, tier: 'D', desc: '1,000,000 Meat', category: 'resources', type: 'meat', denom: '1m' },
      // Wood
      { id: 'wood_100', name: 'Wood 100', image: 'wood.png', fsValue: 0.00054, tier: 'D', desc: '100 Wood', category: 'resources', type: 'wood', denom: '100' },
      { id: 'wood_1k', name: 'Wood 1k', image: 'wood.png', fsValue: 0.0054, tier: 'D', desc: '1,000 Wood', category: 'resources', type: 'wood', denom: '1k' },
      { id: 'wood_10k', name: 'Wood 10k', image: 'wood.png', fsValue: 0.054, tier: 'D', desc: '10,000 Wood', category: 'resources', type: 'wood', denom: '10k' },
      { id: 'wood_100k', name: 'Wood 100k', image: 'wood.png', fsValue: 0.54, tier: 'D', desc: '100,000 Wood', category: 'resources', type: 'wood', denom: '100k' },
      { id: 'wood_1m', name: 'Wood 1M', image: 'wood.png', fsValue: 5.4, tier: 'D', desc: '1,000,000 Wood', category: 'resources', type: 'wood', denom: '1m' },
      // Coal
      { id: 'coal_100', name: 'Coal 100', image: 'coal.png', fsValue: 0.0027, tier: 'D', desc: '100 Coal', category: 'resources', type: 'coal', denom: '100' },
      { id: 'coal_1k', name: 'Coal 1k', image: 'coal.png', fsValue: 0.027, tier: 'D', desc: '1,000 Coal', category: 'resources', type: 'coal', denom: '1k' },
      { id: 'coal_10k', name: 'Coal 10k', image: 'coal.png', fsValue: 0.27, tier: 'D', desc: '10,000 Coal', category: 'resources', type: 'coal', denom: '10k' },
      { id: 'coal_100k', name: 'Coal 100k', image: 'coal.png', fsValue: 2.7, tier: 'D', desc: '100,000 Coal', category: 'resources', type: 'coal', denom: '100k' },
      { id: 'coal_1m', name: 'Coal 1M', image: 'coal.png', fsValue: 27, tier: 'D', desc: '1,000,000 Coal', category: 'resources', type: 'coal', denom: '1m' },
      // Iron
      { id: 'iron_100', name: 'Iron 100', image: 'iron.png', fsValue: 0.0108, tier: 'D', desc: '100 Iron', category: 'resources', type: 'iron', denom: '100' },
      { id: 'iron_1k', name: 'Iron 1k', image: 'iron.png', fsValue: 0.108, tier: 'D', desc: '1,000 Iron', category: 'resources', type: 'iron', denom: '1k' },
      { id: 'iron_10k', name: 'Iron 10k', image: 'iron.png', fsValue: 1.08, tier: 'D', desc: '10,000 Iron', category: 'resources', type: 'iron', denom: '10k' },
      { id: 'iron_100k', name: 'Iron 100k', image: 'iron.png', fsValue: 10.8, tier: 'D', desc: '100,000 Iron', category: 'resources', type: 'iron', denom: '100k' },
      { id: 'iron_1m', name: 'Iron 1M', image: 'iron.png', fsValue: 108, tier: 'D', desc: '1,000,000 Iron', category: 'resources', type: 'iron', denom: '1m' },
      // Steel
      { id: 'steel_100', name: 'Steel 100', image: 'steel.png', fsValue: 0.56, tier: 'C', desc: '100 Steel', category: 'resources', type: 'steel', denom: '100' },
      { id: 'steel_1k', name: 'Steel 1k', image: 'steel.png', fsValue: 5.6, tier: 'C', desc: '1,000 Steel', category: 'resources', type: 'steel', denom: '1k' },
      { id: 'steel_10k', name: 'Steel 10k', image: 'steel.png', fsValue: 56, tier: 'C', desc: '10,000 Steel', category: 'resources', type: 'steel', denom: '10k' },
      { id: 'steel_100k', name: 'Steel 100k', image: 'steel.png', fsValue: 560, tier: 'B', desc: '100,000 Steel', category: 'resources', type: 'steel', denom: '100k' },
      { id: 'steel_1m', name: 'Steel 1M', image: 'steel.png', fsValue: 5600, tier: 'A', desc: '1,000,000 Steel', category: 'resources', type: 'steel', denom: '1m' },
    ],
  },
};

const SPEEDUP_TYPES = ['general', 'construction', 'research', 'training', 'healing'];
const SPEEDUP_DURATIONS = ['1m', '5m', '10m', '30m', '1h', '3h', '8h', '24h'];
const RESOURCE_TYPES = ['meat', 'wood', 'coal', 'iron', 'steel'];
const RESOURCE_DENOMS = ['100', '1k', '10k', '100k', '1m'];

const DURATION_COLORS: Record<string, string> = {
  '1m': '#888888', '5m': '#27AE60', '10m': '#27AE60', '30m': '#3498DB',
  '1h': '#3498DB', '3h': '#9B59B6', '8h': '#E67E22', '24h': '#FFD700',
};

const DENOM_COLORS: Record<string, string> = {
  '100': '#888888', '1k': '#27AE60', '10k': '#3498DB', '100k': '#9B59B6', '1m': '#FFD700',
};

interface AnalysisResult {
  totalValue: number;
  totalValueDollars: number;
  currencyValue: number;
  uniqueValue: number;
  speedupValue: number;
  resourceValue: number;
  fillerValue: number;
  fillerPct: number;
  efficiency: number;
  breakdown: { name: string; image?: string; emoji?: string; quantity: number; tier: string; value: number; isFiller: boolean; category: string }[];
  price: number;
}

function calculateAnalysis(quantities: Record<string, number>, price: number, farmerMode: boolean): AnalysisResult {
  let totalValue = 0, currencyValue = 0, uniqueValue = 0, speedupValue = 0, resourceValue = 0, fillerValue = 0;
  const breakdown: AnalysisResult['breakdown'] = [];

  for (const catData of Object.values(PACK_ITEMS)) {
    for (const item of catData.items) {
      const qty = quantities[item.id] || 0;
      if (qty > 0) {
        let value = qty * item.fsValue;
        if (farmerMode && item.category === 'resources') value = 0;

        totalValue += value;
        const isFiller = item.tier === 'D' || item.category === 'resources';

        if (item.category === 'resources') { resourceValue += value; fillerValue += value; }
        else if (item.category === 'currency') currencyValue += value;
        else if (item.category === 'speedups') { speedupValue += value; if (item.tier === 'D') fillerValue += value; }
        else uniqueValue += value;

        breakdown.push({ name: item.name, image: item.image, emoji: item.emoji, quantity: qty, tier: item.tier, value, isFiller, category: item.category });
      }
    }
  }

  breakdown.sort((a, b) => b.value - a.value);
  const priceFs = price * 100;

  return {
    totalValue, totalValueDollars: totalValue / 100, currencyValue, uniqueValue, speedupValue, resourceValue, fillerValue,
    fillerPct: totalValue > 0 ? (fillerValue / totalValue) * 100 : 0,
    efficiency: priceFs > 0 ? (totalValue / priceFs) * 100 : 0,
    breakdown, price,
  };
}

export default function PackAnalyzerPage() {
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [price, setPrice] = useState(4.99);
  const [farmerMode, setFarmerMode] = useState(false);
  const [activeTab, setActiveTab] = useState('hero');

  const analysis = useMemo(() => calculateAnalysis(quantities, price, farmerMode), [quantities, price, farmerMode]);

  const updateQuantity = (itemId: string, value: number) => {
    setQuantities(prev => ({ ...prev, [itemId]: Math.max(0, value) }));
  };

  const clearAll = () => setQuantities({});

  const getEfficiencyColor = (eff: number) => eff >= 100 ? 'text-success' : eff >= 70 ? 'text-warning' : 'text-error';
  const getEfficiencyLabel = (eff: number) => eff >= 100 ? 'Good Value' : eff >= 70 ? 'Fair Value' : 'Poor Value';

  const categories = Object.keys(PACK_ITEMS);

  // Build lookup for speedups
  const speedupLookup = useMemo(() => {
    const lookup: Record<string, Record<string, PackItem>> = {};
    PACK_ITEMS.speedups.items.forEach(item => {
      if (!lookup[item.type!]) lookup[item.type!] = {};
      lookup[item.type!][item.duration!] = item;
    });
    return lookup;
  }, []);

  // Build lookup for resources
  const resourceLookup = useMemo(() => {
    const lookup: Record<string, Record<string, PackItem>> = {};
    PACK_ITEMS.resources.items.forEach(item => {
      if (!lookup[item.type!]) lookup[item.type!] = {};
      lookup[item.type!][item.denom!] = item;
    });
    return lookup;
  }, []);

  const renderItemImage = (item: { image?: string; emoji?: string; name: string }, size: number = 40) => {
    if (item.image) {
      return <img src={`/images/items/${item.image}`} alt={item.name} width={size} height={size} className="object-contain" />;
    }
    return <span className="text-3xl">{item.emoji || '📦'}</span>;
  };

  const renderItemGrid = (items: PackItem[]) => (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
      {items.map(item => (
        <div key={item.id} className="text-center">
          <div className="mb-2 h-12 flex items-center justify-center" title={item.desc}>
            {renderItemImage(item)}
          </div>
          <p className="text-[10px] text-frost-muted mb-1 truncate px-1" title={item.name}>{item.name}</p>
          <input
            type="number" min={0} value={quantities[item.id] || ''} placeholder="0"
            onChange={e => updateQuantity(item.id, parseInt(e.target.value) || 0)}
            className="input text-center text-xs w-16 mx-auto py-1 no-spinner"
          />
        </div>
      ))}
    </div>
  );

  const renderSpeedupGrid = () => (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr>
            <th className="text-left p-2 text-frost-muted font-medium">Duration</th>
            {SPEEDUP_TYPES.map(type => {
              const imgMap: Record<string, string> = { general: 'speedup_general.png', construction: 'speedup_construction.png', research: 'speedup_research.png', training: 'speedup_training.png', healing: 'speedup_healing.png' };
              return (
                <th key={type} className="p-2 text-center">
                  <div className="flex flex-col items-center gap-1">
                    <img src={`/images/items/${imgMap[type]}`} alt={type} width={24} height={24} className="object-contain" />
                    <span className="text-[10px] text-frost-muted capitalize">{type}</span>
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {SPEEDUP_DURATIONS.map(dur => (
            <tr key={dur}>
              <td className="p-2 font-medium" style={{ color: DURATION_COLORS[dur] }}>{dur}</td>
              {SPEEDUP_TYPES.map(type => {
                const item = speedupLookup[type]?.[dur];
                return (
                  <td key={`${type}-${dur}`} className="p-1 text-center">
                    {item && (
                      <input
                        type="number" min={0} value={quantities[item.id] || ''} placeholder="0"
                        onChange={e => updateQuantity(item.id, parseInt(e.target.value) || 0)}
                        className="input text-center text-xs w-14 py-1 no-spinner"
                        title={item.desc}
                      />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderResourceGrid = () => (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr>
            <th className="text-left p-2 text-frost-muted font-medium">Amount</th>
            {RESOURCE_TYPES.map(type => (
              <th key={type} className="p-2 text-center">
                <div className="flex flex-col items-center gap-1">
                  <img src={`/images/items/${type}.png`} alt={type} width={24} height={24} className="object-contain" />
                  <span className="text-[10px] text-frost-muted capitalize">{type}</span>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {RESOURCE_DENOMS.map(denom => (
            <tr key={denom}>
              <td className="p-2 font-medium" style={{ color: DENOM_COLORS[denom] }}>{denom}</td>
              {RESOURCE_TYPES.map(type => {
                const item = resourceLookup[type]?.[denom];
                return (
                  <td key={`${type}-${denom}`} className="p-1 text-center">
                    {item && (
                      <input
                        type="number" min={0} value={quantities[item.id] || ''} placeholder="0"
                        onChange={e => updateQuantity(item.id, parseInt(e.target.value) || 0)}
                        className="input text-center text-xs w-14 py-1 no-spinner"
                        title={item.desc}
                      />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <PageLayout>
      <style dangerouslySetInnerHTML={{ __html: hideSpinnerStyle }} />
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Pack Value Analyzer</h1>
          <p className="text-frost-muted mt-2">Cut through inflated % values. See what you're <em>actually</em> paying for.</p>
        </div>

        {/* Farmer Mode */}
        <div className="card mb-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" checked={farmerMode} onChange={e => setFarmerMode(e.target.checked)}
              className="w-5 h-5 rounded border-surface-border bg-surface text-ice focus:ring-ice" />
            <div>
              <span className="font-medium text-frost">I'm a resource farmer</span>
              <span className="text-sm text-frost-muted ml-2">(set resources to $0)</span>
            </div>
          </label>
          {farmerMode && <p className="text-sm text-ice mt-2">Farmer Mode ON: Resources valued at $0.</p>}
        </div>

        {/* The Fluff Problem */}
        <div className="card mb-4 border-warning/30 bg-warning/5">
          <p className="text-sm text-frost">
            <strong>The Fluff Problem:</strong> Packs bundle items together, making them feel more valuable than they are.
          </p>
          <p className="text-sm text-frost-muted mt-2">
            Example: A $4.99 pack with 10 Essence Stones = <strong className="text-error">$0.22 actual value</strong> (4.4% of price).
            You're paying a <strong className="text-error">23x markup</strong> for what you want!
          </p>
        </div>

        {/* Price & Analysis */}
        <div className="card mb-4">
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <div>
              <label className="text-sm text-frost-muted block mb-1">Pack Price</label>
              <select value={price} onChange={e => setPrice(parseFloat(e.target.value))} className="input w-28">
                {PRICE_OPTIONS.map(p => <option key={p} value={p}>${p.toFixed(2)}</option>)}
              </select>
            </div>
            <button onClick={clearAll} className="btn-secondary text-sm">Clear All</button>
          </div>

          {analysis.totalValue > 0 ? (
            <>
              {/* Value Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="text-center p-3 rounded-lg bg-success/10">
                  <div className="text-xl font-bold text-success">${analysis.totalValueDollars.toFixed(2)}</div>
                  <div className="text-xs text-frost-muted">Actual Value</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-surface">
                  <div className="text-xl font-bold text-frost">${analysis.price.toFixed(2)}</div>
                  <div className="text-xs text-frost-muted">Pack Price</div>
                </div>
                <div className={`text-center p-3 rounded-lg ${analysis.efficiency >= 100 ? 'bg-success/10' : analysis.efficiency >= 70 ? 'bg-warning/10' : 'bg-error/10'}`}>
                  <div className={`text-xl font-bold ${getEfficiencyColor(analysis.efficiency)}`}>{analysis.efficiency.toFixed(0)}%</div>
                  <div className="text-xs text-frost-muted">{getEfficiencyLabel(analysis.efficiency)}</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-error/10">
                  <div className="text-xl font-bold text-error">{analysis.fillerPct.toFixed(0)}%</div>
                  <div className="text-xs text-frost-muted">Filler{analysis.fillerPct > 50 ? ' (Heavy!)' : ''}</div>
                </div>
              </div>

              {/* Category Bar */}
              <div className="mb-4">
                <p className="text-xs text-frost-muted mb-1">Value by Category:</p>
                <div className="flex h-5 rounded overflow-hidden">
                  {analysis.currencyValue > 0 && <div style={{ width: `${(analysis.currencyValue / analysis.totalValue) * 100}%`, backgroundColor: '#FFD700' }} />}
                  {analysis.uniqueValue > 0 && <div style={{ width: `${(analysis.uniqueValue / analysis.totalValue) * 100}%`, backgroundColor: '#9B59B6' }} />}
                  {analysis.speedupValue > 0 && <div style={{ width: `${(analysis.speedupValue / analysis.totalValue) * 100}%`, backgroundColor: '#3498DB' }} />}
                  {analysis.resourceValue > 0 && <div style={{ width: `${(analysis.resourceValue / analysis.totalValue) * 100}%`, backgroundColor: '#E74C3C' }} />}
                </div>
                <div className="flex justify-center gap-3 text-[10px] text-frost-muted mt-1">
                  <span><span style={{ color: '#FFD700' }}>●</span> Currency</span>
                  <span><span style={{ color: '#9B59B6' }}>●</span> Unique</span>
                  <span><span style={{ color: '#3498DB' }}>●</span> Speedups</span>
                  <span><span style={{ color: '#E74C3C' }}>●</span> Resources</span>
                </div>
              </div>

              {/* Item Breakdown */}
              <div>
                <p className="text-sm font-medium text-frost mb-2">Item Breakdown (Top 10)</p>
                <div className="space-y-1">
                  {analysis.breakdown.slice(0, 10).map((item, i) => {
                    const pct = (item.value / analysis.totalValue) * 100;
                    const tierColor = TIER_COLORS[item.tier] || '#666';
                    return (
                      <div key={i} className="flex items-center justify-between p-2 rounded bg-surface/50" style={{ borderLeft: `3px solid ${tierColor}` }}>
                        <div className="flex items-center gap-2">
                          <span className="text-sm flex-shrink-0">{item.image ? <img src={`/images/items/${item.image}`} alt={item.name} width={20} height={20} className="object-contain inline-block" /> : (item.emoji || '📦')}</span>
                          <span className="text-sm text-frost">{item.name}</span>
                        </div>
                        <div className="text-sm">
                          <span className="font-bold text-frost">×{item.quantity.toLocaleString()}</span>
                          <span className="text-frost-muted mx-1">→</span>
                          <span style={{ color: tierColor }}>${(item.value / 100).toFixed(2)}</span>
                          <span className="text-frost-muted ml-1">({pct.toFixed(1)}%)</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-6 text-frost-muted">
              <div className="text-4xl mb-3">📦</div>
              <p>Enter item quantities below to see analysis</p>
            </div>
          )}
        </div>

        {/* Item Entry */}
        <div className="card">
          <h2 className="text-lg font-semibold text-frost mb-4">Enter Pack Contents</h2>

          {/* Tabs */}
          <div className="flex flex-wrap gap-1.5 mb-6 border-b border-surface-border pb-4 lg:flex-nowrap lg:gap-2">
            {categories.map(cat => (
              <button key={cat} onClick={() => setActiveTab(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap lg:flex-1 lg:text-center ${activeTab === cat ? 'bg-ice text-background' : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'}`}>
                {PACK_ITEMS[cat].label}
              </button>
            ))}
          </div>

          {/* Content */}
          {PACK_ITEMS[activeTab].isSpeedupGrid ? renderSpeedupGrid() :
           PACK_ITEMS[activeTab].isResourceGrid ? renderResourceGrid() :
           renderItemGrid(PACK_ITEMS[activeTab].items)}
        </div>

        {/* Tips */}
        <div className="card mt-4">
          <details className="group">
            <summary className="flex items-center justify-between cursor-pointer text-frost font-medium">
              <span>Understanding Pack Value</span>
              <span className="text-ice group-open:rotate-180 transition-transform">▼</span>
            </summary>
            <div className="mt-3 pt-3 border-t border-surface-border space-y-2 text-sm text-frost-muted">
              <div>
                <strong className="text-frost">Item Tiers:</strong>
                <ul className="mt-1 space-y-0.5">
                  <li><span style={{ color: TIER_COLORS.S }}>S Tier</span>: Mithril, Advanced Wild Marks, 24h Speedups</li>
                  <li><span style={{ color: TIER_COLORS.A }}>A Tier</span>: Essence Stones, Gold Keys, Gems</li>
                  <li><span style={{ color: TIER_COLORS.B }}>B Tier</span>: Hourly speedups, Manuals</li>
                  <li><span style={{ color: TIER_COLORS.C }}>C Tier</span>: Small speedups, Steel, Hero XP</li>
                  <li><span style={{ color: TIER_COLORS.D }}>D Tier</span>: Resources, Healing speedups - FILLER</li>
                </ul>
              </div>
              <div>
                <strong className="text-frost">Efficiency:</strong> 100%+ = Good deal, 70-99% = Fair, Below 70% = Poor
              </div>
            </div>
          </details>
        </div>
      </div>
    </PageLayout>
  );
}
