#!/usr/bin/env python3
"""
Compute gem-equivalent costs for upgrade edges.

Usage:
    python scripts/compute_gem_costs.py [--profile f2p_mid] [--system buildings]

This script:
1. Loads gem shadow prices from data/conversions/gem_shadow_prices.json
2. Loads scarcity profiles from data/conversions/scarcity_profiles.json
3. Computes gem costs for all edges in a system
4. Outputs both baseline and scarcity-adjusted costs
"""

import json
import argparse
from pathlib import Path
from typing import Optional

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PRICES_FILE = DATA_DIR / "conversions" / "gem_shadow_prices.json"
PROFILES_FILE = DATA_DIR / "conversions" / "scarcity_profiles.json"
UPGRADES_DIR = DATA_DIR / "upgrades"


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_gem_price(prices: dict, resource_id: str) -> Optional[float]:
    """Get gem price for a resource, or None if not yet sourced."""
    for category in prices.get("prices", {}).values():
        if isinstance(category, list):
            for item in category:
                if item.get("resource_id") == resource_id:
                    return item.get("gems_per_unit")
    return None


def get_scarcity_multiplier(profiles: dict, profile_name: str, resource_id: str) -> float:
    """Get scarcity multiplier for a resource in a profile."""
    profile = profiles.get("preset_profiles", {}).get(profile_name, {})
    multipliers = profile.get("multipliers", {})

    # Handle resource ID variations
    if resource_id in multipliers:
        return multipliers[resource_id]

    # Map specific speedups to general
    if resource_id.startswith("speedup_"):
        return multipliers.get("speedup_general", 1.0)

    return 1.0  # Default no adjustment


def compute_edge_gem_cost(edge: dict, prices: dict, profile: Optional[dict] = None) -> dict:
    """
    Compute gem cost for a single edge.

    Returns:
        {
            "upgrade_id": str,
            "baseline_gem_cost": float or None,
            "adjusted_gem_cost": float or None,
            "missing_prices": list[str],
            "cost_breakdown": dict
        }
    """
    upgrade_id = edge.get("upgrade_id", "unknown")
    cost = edge.get("cost", {})
    time_seconds = edge.get("time_seconds", 0)

    baseline_cost = 0.0
    adjusted_cost = 0.0
    missing_prices = []
    breakdown = {}

    # Process resource costs
    for resource_id, amount in cost.items():
        if amount == 0:
            continue

        gem_price = get_gem_price(prices, resource_id)

        if gem_price is None:
            missing_prices.append(resource_id)
            breakdown[resource_id] = {"amount": amount, "gem_price": None, "gem_cost": None}
        else:
            resource_gem_cost = amount * gem_price
            baseline_cost += resource_gem_cost

            # Apply scarcity multiplier if profile provided
            if profile:
                multiplier = get_scarcity_multiplier({"preset_profiles": {"current": profile}}, "current", resource_id)
            else:
                multiplier = 1.0

            adjusted_cost += resource_gem_cost * multiplier
            breakdown[resource_id] = {
                "amount": amount,
                "gem_price": gem_price,
                "gem_cost": resource_gem_cost,
                "multiplier": multiplier,
                "adjusted_cost": resource_gem_cost * multiplier
            }

    # Process time cost (speedups)
    if time_seconds > 0:
        gems_per_second = prices.get("derived_rates", {}).get("gems_per_second_speedup")
        if gems_per_second:
            time_gem_cost = time_seconds * gems_per_second
            baseline_cost += time_gem_cost

            if profile:
                multiplier = get_scarcity_multiplier({"preset_profiles": {"current": profile}}, "current", "speedup_general")
            else:
                multiplier = 1.0

            adjusted_cost += time_gem_cost * multiplier
            breakdown["time_speedup"] = {
                "seconds": time_seconds,
                "gems_per_second": gems_per_second,
                "gem_cost": time_gem_cost,
                "multiplier": multiplier,
                "adjusted_cost": time_gem_cost * multiplier
            }
        else:
            missing_prices.append("speedup_rate")

    return {
        "upgrade_id": upgrade_id,
        "baseline_gem_cost": baseline_cost if not missing_prices else None,
        "adjusted_gem_cost": adjusted_cost if not missing_prices else None,
        "missing_prices": missing_prices,
        "cost_breakdown": breakdown
    }


def main():
    parser = argparse.ArgumentParser(description="Compute gem costs for upgrade edges")
    parser.add_argument("--profile", default="f2p_mid", help="Scarcity profile to use")
    parser.add_argument("--system", help="Upgrade system to process (e.g., buildings, chief_gear)")
    parser.add_argument("--check-prices", action="store_true", help="Check which prices are missing")
    args = parser.parse_args()

    # Load data
    if not PRICES_FILE.exists():
        print(f"ERROR: Prices file not found: {PRICES_FILE}")
        return 1

    prices = load_json(PRICES_FILE)

    if args.check_prices:
        print("=" * 60)
        print("GEM SHADOW PRICES STATUS")
        print("=" * 60)

        for category_name, category_items in prices.get("prices", {}).items():
            print(f"\n{category_name}:")
            if isinstance(category_items, list):
                for item in category_items:
                    resource_id = item.get("resource_id")
                    gem_price = item.get("gems_per_unit")
                    confidence = item.get("confidence", {}).get("grade", "?")
                    status = f"{gem_price:.4f}" if gem_price else "NOT SET"
                    print(f"  {resource_id}: {status} (confidence: {confidence})")

        print("\n" + "=" * 60)
        print("To populate prices, provide in-game screenshots or")
        print("find verified calculator data with gem costs.")
        print("=" * 60)
        return 0

    # Load profiles
    profiles = load_json(PROFILES_FILE) if PROFILES_FILE.exists() else {}
    profile = profiles.get("preset_profiles", {}).get(args.profile, {}).get("multipliers")

    if not profile:
        print(f"WARNING: Profile '{args.profile}' not found, using no scarcity adjustment")
        profile = None

    # Find upgrade files
    edge_files = list(UPGRADES_DIR.glob("*.edges.json")) + list(UPGRADES_DIR.glob("*.steps.json"))

    if args.system:
        edge_files = [f for f in edge_files if args.system in f.stem]

    if not edge_files:
        print("No upgrade edge files found")
        return 1

    print("=" * 60)
    print(f"COMPUTING GEM COSTS (profile: {args.profile})")
    print("=" * 60)

    total_edges = 0
    total_with_costs = 0
    all_missing = set()

    for edge_file in sorted(edge_files):
        data = load_json(edge_file)
        edges = data.get("edges", [])

        print(f"\n{edge_file.name}: {len(edges)} edges")

        file_missing = set()
        file_with_costs = 0

        for edge in edges[:3]:  # Show first 3 as examples
            result = compute_edge_gem_cost(edge, prices, profile)

            if result["baseline_gem_cost"] is not None:
                file_with_costs += 1
                print(f"  {result['upgrade_id']}")
                print(f"    Baseline: {result['baseline_gem_cost']:,.0f} gems")
                if result["adjusted_gem_cost"]:
                    print(f"    Adjusted: {result['adjusted_gem_cost']:,.0f} gems")
            else:
                file_missing.update(result["missing_prices"])

        if len(edges) > 3:
            print(f"  ... and {len(edges) - 3} more edges")

        if file_missing:
            print(f"  Missing prices for: {', '.join(sorted(file_missing))}")

        all_missing.update(file_missing)
        total_edges += len(edges)
        total_with_costs += file_with_costs

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total edges: {total_edges}")
    print(f"Edges with computable costs: {total_with_costs}")

    if all_missing:
        print(f"\nMissing prices for: {', '.join(sorted(all_missing))}")
        print("\nTo enable cost computation, populate gem_shadow_prices.json with:")
        print("  - In-game shop screenshots (best)")
        print("  - Verified calculator data")
    else:
        print("\nAll prices available! Ready to compute costs.")

    return 0


if __name__ == "__main__":
    exit(main())
