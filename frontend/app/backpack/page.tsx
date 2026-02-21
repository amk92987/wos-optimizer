'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

// Item data organized by category
const ITEM_DATA: Record<string, ItemInfo[]> = {
  "Resources": [
    { id: "gems", name: "Gems", image: "gems.png", description: "Premium currency for purchases and speedups", sources: "Daily rewards, Events, Packs, Achievements", uses: "Lucky Wheel, Instant finish, VIP shop, Refreshes" },
    { id: "meat", name: "Meat", image: "meat.png", description: "Basic resource for troop training", sources: "Hunting zones, Resource tiles, Chests", uses: "Training troops, Troop upkeep" },
    { id: "wood", name: "Wood", image: "wood.png", description: "Basic resource for construction", sources: "Lumber mills, Resource tiles, Chests", uses: "Building upgrades, Research" },
    { id: "coal", name: "Coal", image: "coal.png", description: "Resource for advanced construction", sources: "Coal mines, Resource tiles, Chests", uses: "Building upgrades, Research" },
    { id: "iron", name: "Iron", image: "iron.png", description: "Rare resource for high-level upgrades", sources: "Iron mines, Resource tiles, Events", uses: "Advanced buildings, Elite troops" },
    { id: "steel", name: "Steel", image: "steel.png", description: "Refined iron for advanced uses", sources: "Steel production, Events, Chests", uses: "High-tier construction, Research" },
    { id: "fire_crystal", name: "Fire Crystal", image: "fire_crystal.png", description: "Currency for Furnace upgrades (FC1-FC5)", sources: "FC mines, Events, Packs, Bear Trap, Daily missions", uses: "Furnace building upgrades" },
    { id: "fire_crystal_shard", name: "Fire Crystal Shard", image: "fire_crystal_shard.png", description: "Component for crafting Fire Crystals", sources: "Daily missions, Intel missions, Events", uses: "Convert to Fire Crystals in Crystal Lab" },
    { id: "refined_fire_crystal", name: "Refined Fire Crystal", image: "refined_fire_crystal.png", description: "Purified FC for higher Furnace levels (FC6+)", sources: "Crystal Lab Super Refinement, Events, Packs", uses: "High-level Furnace upgrades (FC6-FC10)" },
    { id: "stamina", name: "Chief Stamina", image: "stamina.png", description: "Energy for beasts and exploration", sources: "Natural regen (1/6min), VIP shop, Events", uses: "Beast attacks, Exploration battles" },
  ],
  "Hero Items": [
    { id: "legendary_hero_shard", name: "Legendary Shard", image: "mythic_hero_shard.png", description: "Universal shard for any legendary hero", sources: "Lucky Wheel, Events, Packs, Hero Hall", uses: "Unlock/upgrade any legendary hero" },
    { id: "epic_hero_shard", name: "Epic Shard", image: "epic_hero_shard.png", description: "Universal shard for epic heroes", sources: "Hero Hall, Events, Exploration", uses: "Unlock/upgrade any epic hero" },
    { id: "rare_hero_shard", name: "Rare Shard", image: "rare_hero_shard.png", description: "Universal shard for rare heroes", sources: "Exploration, Daily rewards, Events", uses: "Unlock/upgrade any rare hero" },
    { id: "hero_xp", name: "Hero XP", image: "hero_xp.png", description: "Experience points to level up heroes", sources: "Exploration, Combat Manuals, Events", uses: "Leveling up heroes" },
    { id: "mythic_exploration_manual", name: "Mythic Exploration Manual", image: "mythic_exploration_manual.png", description: "Upgrades exploration skills for Mythic heroes", sources: "Lighthouse Intel, Exploration bosses, VIP Shop", uses: "Mythic hero exploration skills" },
    { id: "epic_exploration_manual", name: "Epic Exploration Manual", image: "epic_exploration_manual.png", description: "Upgrades exploration skills for Epic heroes", sources: "Lighthouse Intel, Exploration stages, VIP Shop", uses: "Epic hero exploration skills" },
    { id: "rare_exploration_manual", name: "Rare Exploration Manual", image: "rare_exploration_manual.png", description: "Upgrades exploration skills for Rare heroes", sources: "Exploration stages, Daily play, Events", uses: "Rare hero exploration skills" },
    { id: "mythic_expedition_manual", name: "Mythic Expedition Manual", image: "mythic_expedition_manual.png", description: "Upgrades expedition skills for Mythic heroes", sources: "Lighthouse Intel, VIP Shop, Events (rare)", uses: "Mythic hero expedition skills" },
    { id: "epic_expedition_manual", name: "Epic Expedition Manual", image: "epic_expedition_manual.png", description: "Upgrades expedition skills for Epic heroes", sources: "Lighthouse Intel, Exploration, VIP Shop", uses: "Epic hero expedition skills" },
    { id: "rare_expedition_manual", name: "Rare Expedition Manual", image: "rare_expedition_manual.png", description: "Upgrades expedition skills for Rare heroes", sources: "Exploration stages, Events", uses: "Rare hero expedition skills" },
    { id: "essence_stone", name: "Essence Stone", image: "essence_stone.png", description: "Critical for Mythic gear mastery. Very valuable", sources: "Mystery Shop, Arena Shop, Hero gear recycling", uses: "Mythic Hero Gear Mastery (FC20+)" },
    { id: "mithril", name: "Mithril", image: "mithril.png", description: "Rare material for Legendary gear empowerment", sources: "Arena Shop (3/season), Frostdragon event, Packs", uses: "Empower Legendary Hero Gear at 20/40/60/80/100" },
    { id: "xp_component", name: "Enhancement XP Component", image: "xp_component.png", description: "Primary material for enhancing hero gear stats", sources: "Events, Tundra Trading, Daily/Intel missions", uses: "Leveling up Hero Gear (FC15+)" },
    { id: "hero_gear_chest", name: "Hero Gear Chest", image: "hero_gear_chest.png", description: "Contains random hero gear pieces", sources: "Events, Lucky chests, Frosty Fortune", uses: "Building hero gear collection" },
  ],
  "Chief Gear": [
    { id: "hardened_alloy", name: "Hardened Alloy", image: "hardened_alloy.png", description: "Primary material for chief gear upgrades", sources: "Polar Terror rallies (Lv.3+), Beast hunts (22+), Crazy Joe", uses: "Chief gear crafting/upgrades" },
    { id: "polishing_solution", name: "Polishing Solution", image: "polishing_solution.png", description: "Secondary material for chief gear refinement", sources: "Crazy Joe, Frostfire Mine, Championship Shop", uses: "Chief gear refinement" },
    { id: "design_plans", name: "Design Plans", image: "design_plans.png", description: "Blueprints for Blue+ quality chief gear", sources: "Alliance Championship, Foundry, Power Region", uses: "Upgrading chief gear (Blue+)" },
    { id: "lunar_amber", name: "Lunar Amber", image: "lunar_amber.png", description: "Material for Red+ quality chief gear", sources: "Material Exchanges, Premium packs, Events", uses: "High-tier chief gear (Red+)" },
    { id: "charm_secrets", name: "Charm Secrets", image: "charm_secrets.png", description: "Rare material for L12+ charm upgrades (Gen 7 state required)", sources: "Events, Material Exchange, Premium packs", uses: "Chief Charm upgrades L12-L16" },
    { id: "charm_design", name: "Charm Design", image: "charm_design.png", description: "Primary material for Chief Charm upgrades", sources: "Events, Giant Elk pet, Packs, Tundra Trading", uses: "Chief Charm upgrades (all levels)" },
    { id: "charm_guide", name: "Charm Guide", image: "charm_guide.png", description: "Secondary material for Chief Charm upgrades", sources: "Alliance Shop, Events, Foundry, Giant Elk pet", uses: "Chief Charm upgrades (all levels)" },
  ],
  "Pets": [
    { id: "pet_food", name: "Pet Food", image: "pet_food.png", description: "Nutrient substance for leveling up pets", sources: "Pet adventures (10 stamina), Beast Cage activities", uses: "Feeding pets to gain XP" },
    { id: "taming_manual", name: "Taming Manual", image: "taming_manual.png", description: "Core material for pet potential advancement", sources: "Pet adventures, Lighthouse Intel missions", uses: "Pet advancement (all levels)" },
    { id: "energizing_potion", name: "Energizing Potion", image: "energizing_potion.png", description: "Extra advancement material for pets (Lv.30+)", sources: "Pet adventures, Events", uses: "Pet advancement from level 30+" },
    { id: "strengthening_serum", name: "Strengthening Serum", image: "strengthening_serum.png", description: "Advanced advancement material (Lv.50+)", sources: "Pet adventures, High-level beast hunts", uses: "Pet advancement from level 50+" },
    { id: "common_wild_mark", name: "Common Wild Mark", image: "common_wild_mark.png", description: "Material for basic pet refinement", sources: "Pet adventures, Various events", uses: "Pet refinement processes" },
    { id: "advanced_wild_mark", name: "Advanced Wild Mark", image: "advanced_wild_mark.png", description: "Material for advanced pet refinement", sources: "Pet adventures, Higher-tier beast hunts", uses: "Advanced pet refinement" },
    { id: "pet_materials_chest", name: "Pet Materials Chest", image: "pet_materials_chest.png", description: "Contains pet advancement materials", sources: "Events, Shops, Quest rewards", uses: "Pet advancement" },
  ],
  "Speedups": [
    { id: "speedup_general", name: "General Speedup", image: "speedup_general.png", description: "Reduces any timer. Most versatile", sources: "Events, Chests, Packs, Alliance help", uses: "Any: construction, research, training, healing", durations: "1min, 5min, 1hr, 3hr, 8hr, 24hr" },
    { id: "speedup_construction", name: "Construction Speedup", image: "speedup_construction.png", description: "Reduces building timers only", sources: "Events, Chests, Construction milestones", uses: "Building construction and upgrades", durations: "1min, 5min, 1hr, 3hr, 8hr" },
    { id: "speedup_research", name: "Research Speedup", image: "speedup_research.png", description: "Reduces research timers only", sources: "Events, Chests, Research milestones", uses: "Research projects only", durations: "1min, 5min, 1hr, 3hr, 8hr" },
    { id: "speedup_training", name: "Training Speedup", image: "speedup_training.png", description: "Reduces troop training timers only", sources: "Events, Chests, Training milestones", uses: "Troop training only", durations: "1min, 5min, 1hr, 3hr, 8hr" },
    { id: "speedup_healing", name: "Healing Speedup", image: "speedup_healing.png", description: "Reduces hospital healing timers only", sources: "Events, Chests, Combat rewards", uses: "Healing wounded troops only", durations: "1min, 5min, 1hr, 3hr, 8hr" },
  ],
  "Boosts": [
    { id: "shield", name: "Peace Shield", image: "shield.png", description: "Protects city from attacks", sources: "Events, Packs, Gem shop, Rewards", uses: "Protecting city when offline", durations: "2hr, 8hr, 24hr, 3 day, 7 day" },
    { id: "counter_recon", name: "Counter Recon", image: "counter_recon.png", description: "Hides troop/resource info from scouts", sources: "Events, Packs, Gem shop", uses: "Hide army before SvS/battles", durations: "2hr, 24hr" },
    { id: "vip_time", name: "VIP Time", image: "vip_time.png", description: "Grants temporary VIP benefits", sources: "Events, Packs, Daily rewards", uses: "Activating VIP buffs/discounts", durations: "24hr, 7 day, 30 day" },
    { id: "troops_attack_up", name: "Troop Attack UP", image: "troops_attack_up.png", description: "Temporarily increases troop attack", sources: "City Bonus (2k/20k gems), Events, Packs", uses: "Activate before rallies/SvS", durations: "2hr (+10%), 12hr (+20%)" },
    { id: "troops_defense_up", name: "Troop Defense UP", image: "troops_defense_up.png", description: "Temporarily increases troop defense", sources: "City Bonus (2k/20k gems), Events, Packs", uses: "Activate when expecting attacks", durations: "2hr (+10%), 12hr (+20%)" },
    { id: "march_accelerator", name: "March Speed Boost", image: "march_accelerator.png", description: "Increases march speed", sources: "Events, Packs, Rewards", uses: "Faster rallies, Quick reinforcements" },
    { id: "gathering_speed_boost", name: "Gathering Boost", image: "gathering_speed_boost.png", description: "Increases gathering speed on tiles", sources: "City Bonus, Events, Packs", uses: "Faster resource collection", durations: "8hr, 24hr (+100%)" },
    { id: "rally_boost", name: "Rally Attack Boost", image: "rally_boost.png", description: "Increases damage during rallies", sources: "Events, Packs, Alliance rewards", uses: "Before leading/joining rallies" },
    { id: "expedition_boost", name: "Expedition Boost", image: "expedition_boost.png", description: "Boosts expedition battle performance", sources: "Events, Packs", uses: "Expedition battles" },
  ],
  "Currencies": [
    { id: "platinum_key", name: "Platinum Key", image: "platinum_key.png", description: "Opens platinum chests for rare rewards", sources: "Events, Packs, Milestones", uses: "Opening platinum reward chests" },
    { id: "gold_key", name: "Gold Key", image: "gold_key.png", description: "Opens gold chests for good rewards", sources: "Events, Packs, Daily alliance ranking", uses: "Opening gold reward chests" },
    { id: "lucky_wheel_ticket", name: "Wheel Ticket", image: "lucky_wheel_ticket.png", description: "Free spin on the Lucky Wheel", sources: "Events, Daily login, Packs", uses: "Lucky Wheel for shards/items" },
    { id: "alliance_token", name: "Alliance Token", image: "alliance_token.png", description: "Alliance currency (resets daily/weekly)", sources: "Tech donations, Crazy Joe, Alliance activities", uses: "Alliance Shop (teleports, speedups, VIP)" },
    { id: "arena_token", name: "Arena Token", image: "arena_token.png", description: "Currency from Arena battles", sources: "Arena battles, Arena rankings", uses: "Arena Shop (gear, stamina, essence stones)" },
    { id: "mystery_badge", name: "Mystery Badge", image: "mystery_badge.png", description: "Daily currency for Mystery Shop (cap 80/day)", sources: "Daily missions (80 free), Mystery Badge Packs", uses: "Mystery Shop (Custom Mythic gear)" },
    { id: "frost_star", name: "Frost Star", image: "frost_star.png", description: "Premium currency for special items", sources: "Events, Battle Pass, Special rewards", uses: "Frost Star shop exclusives" },
    { id: "glowstones", name: "Glowstones", image: "glowstone.png", description: "Labyrinth currency for premium items", sources: "Labyrinth Raiding, Glowstone Mine (F25+)", uses: "Labyrinth Shop (Mythic Shards, Hero Gear, Mithril)" },
    { id: "fortune_token", name: "Fortune Token", image: "fortune_token.png", description: "Mia's Fortune Hut - reveal orbs", sources: "Daily missions (22), Free bonus (1/day), Packs", uses: "Reveal orbs for Wish Reward, stack multipliers" },
    { id: "marks_of_valor", name: "Marks of Valor", image: "mark_of_valor.png", description: "Hall of Heroes - redeem for Mythic Hero Shards", sources: "Purchase with gems, Hall of Heroes packs", uses: "Mythic Hero Shards (varies by your server generation)" },
  ],
  "Misc": [
    { id: "random_teleporter", name: "Random Teleport", image: "random_teleporter.png", description: "Moves city to random location", sources: "Events, Gem shop (cheap), Rewards", uses: "Escaping attacks, Relocating" },
    { id: "advanced_teleporter", name: "Advanced Teleport", image: "advanced_teleporter.png", description: "Moves city to chosen location", sources: "Events, Packs, Gem shop, Arena Shop", uses: "Strategic positioning" },
    { id: "alliance_teleporter", name: "Alliance Teleport", image: "alliance_teleporter.png", description: "Moves city near alliance territory", sources: "Events, Alliance shop, Packs", uses: "Joining alliance hive" },
    { id: "transfer_pass", name: "Transfer Pass", image: "transfer_pass.png", description: "Relocate entire city to different state", sources: "Alliance Shop (priority), Events", uses: "Server/state migration" },
    { id: "resource_chest", name: "Resource Chest", image: "resource_chest.png", description: "Contains choice of basic resources", sources: "Events, Daily missions, Tundra Trading", uses: "Choose meat, wood, coal, or iron" },
    { id: "chief_gear_chest", name: "Chief Gear Chest", image: "chief_gear_chest.png", description: "Contains chief gear materials", sources: "Events, Foundry rewards", uses: "Chief gear crafting materials" },
    { id: "fire_crystal_chest", name: "Fire Crystal Chest", image: "fire_crystal_chest.png", description: "Contains Fire Crystals or Shards", sources: "Crystal Reactivation, Daily missions (last 2)", uses: "Post-FC30 upgrades" },
    { id: "common_expert_sigil", name: "Expert Sigil", image: "common_expert_sigil.png", description: "Material for hero expertise trees", sources: "Events, Expert missions, Shops", uses: "Hero expertise abilities" },
  ],
};

interface ItemInfo {
  id: string;
  name: string;
  image: string;
  description: string;
  sources: string;
  uses: string;
  durations?: string;
}

const categories = Object.keys(ITEM_DATA);

export default function ItemGuidePage() {
  const [activeTab, setActiveTab] = useState(categories[0]);
  const [searchQuery, setSearchQuery] = useState('');

  // Filter items based on search
  const getFilteredItems = (categoryItems: ItemInfo[]) => {
    if (!searchQuery) return categoryItems;
    const query = searchQuery.toLowerCase();
    return categoryItems.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.sources.toLowerCase().includes(query) ||
        item.uses.toLowerCase().includes(query)
    );
  };

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Item Guide</h1>
          <p className="text-frost-muted mt-2">
            Reference for game items - what they are, where to get them, and what they're used for.
          </p>
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input w-full md:w-96"
          />
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-1.5 mb-6 border-b border-surface-border pb-4 lg:flex-nowrap lg:gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap lg:flex-1 lg:text-center ${
                activeTab === cat
                  ? 'bg-ice text-background'
                  : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Items Table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-border bg-surface/50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-frost-muted uppercase tracking-wider w-12"></th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-frost-muted uppercase tracking-wider">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-frost-muted uppercase tracking-wider">Description</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-frost-muted uppercase tracking-wider">Sources</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-frost-muted uppercase tracking-wider">Uses</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {getFilteredItems(ITEM_DATA[activeTab]).map((item) => (
                  <tr key={item.id} className="hover:bg-surface/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="w-8 h-8 rounded bg-surface-hover flex items-center justify-center overflow-hidden">
                        <img
                          src={`/images/items/${item.image}`}
                          alt={item.name}
                          width={32}
                          height={32}
                          className="object-contain"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                            (e.target as HTMLImageElement).parentElement!.innerHTML = `<span class="text-xs font-bold text-ice">${item.name.charAt(0)}</span>`;
                          }}
                        />
                      </div>
                    </td>
                    <td className="px-4 py-3 font-medium text-frost whitespace-nowrap">
                      {item.name}
                    </td>
                    <td className="px-4 py-3 text-sm text-frost-muted">
                      {item.description}
                      {item.durations && (
                        <span className="block text-xs text-warning mt-1">{item.durations}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-frost-muted">{item.sources}</td>
                    <td className="px-4 py-3 text-xs text-ice">{item.uses}</td>
                  </tr>
                ))}
                {getFilteredItems(ITEM_DATA[activeTab]).length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-frost-muted">
                      No items match your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tips */}
        <div className="card mt-6 border-ice/30 bg-ice/5">
          <h2 className="section-header">Item Priority Tips</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-success">S</span>
              <span><strong className="text-frost">Mithril, Essence Stones</strong> - Highest value, never waste</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">A</span>
              <span><strong className="text-frost">Mythic Shards, Charm Designs</strong> - High priority, save for events</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-warning">B</span>
              <span><strong className="text-frost">Speedups, Keys</strong> - Use strategically during SvS</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-frost-muted">C</span>
              <span><strong className="text-frost">Resources</strong> - Farmable, don't spend gems on these</span>
            </li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
