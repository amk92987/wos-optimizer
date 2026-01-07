"""
Build Troops edges from raw sample data.
Generates training and promotion edges with costs, validates linearity.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRAIN_SAMPLES_FILE = PROJECT_ROOT / "data" / "raw" / "troops.train.samples.json"
PROMOTE_SAMPLES_FILE = PROJECT_ROOT / "data" / "raw" / "troops.promote.samples.json"
TRAIN_EDGES_FILE = PROJECT_ROOT / "data" / "upgrades" / "troops.train.edges.json"
PROMOTE_EDGES_FILE = PROJECT_ROOT / "data" / "upgrades" / "troops.promote.edges.json"
REPORT_FILE = PROJECT_ROOT / "data" / "validation" / "troops.report.json"

# Configuration
TROOP_TYPES = ["infantry", "lancer", "marksman"]
TRAIN_TIERS = [6, 7, 8, 9, 10, 11]
PROMOTE_TIERS = [(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)]
QUANTITIES = [100, 500, 1000, 5000, 10000]


def load_raw_data():
    """Load raw sample files."""
    with open(TRAIN_SAMPLES_FILE, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    with open(PROMOTE_SAMPLES_FILE, 'r', encoding='utf-8') as f:
        promote_data = json.load(f)
    return train_data, promote_data


def get_per_troop_cost(per_troop_costs: dict, troop_type: str, tier: int) -> dict:
    """Get per-troop cost for a specific troop type and tier."""
    for row in per_troop_costs[troop_type]:
        if row["tier"] == tier:
            return row
    return None


def get_per_troop_promote_cost(per_troop_costs: dict, troop_type: str, tier_from: int, tier_to: int) -> dict:
    """Get per-troop promotion cost for a specific troop type and tier transition."""
    for row in per_troop_costs[troop_type]:
        if row["tier_from"] == tier_from and row["tier_to"] == tier_to:
            return row
    return None


def build_train_edges(train_data: dict) -> tuple[list, list]:
    """Build training edges for all combinations."""
    edges = []
    missing = []
    per_troop_costs = train_data["per_troop_costs"]

    for troop_type in TROOP_TYPES:
        for tier in TRAIN_TIERS:
            per_troop = get_per_troop_cost(per_troop_costs, troop_type, tier)
            if not per_troop:
                missing.append({"type": troop_type, "tier": tier})
                continue

            for qty in QUANTITIES:
                edge = {
                    "upgrade_id": f"troops_train:{troop_type}:T{tier}:qty{qty}",
                    "from": {
                        "action": "train",
                        "troop_type": troop_type,
                        "tier": tier,
                        "qty": qty
                    },
                    "to": {
                        "result": "trained",
                        "troop_type": troop_type,
                        "tier": tier,
                        "qty": qty
                    },
                    "cost": {
                        "meat": per_troop["meat"] * qty,
                        "wood": per_troop["wood"] * qty,
                        "coal": per_troop["coal"] * qty,
                        "iron": per_troop["iron"] * qty,
                        "fire_crystal": 0,
                        "speedups_seconds": 0
                    },
                    "time_seconds": per_troop["time_seconds"] * qty,
                    "benefit": {
                        "power_gained": per_troop["power"] * qty
                    },
                    "event_points": {
                        "hall_of_chiefs": per_troop["hoc_points"] * qty,
                        "king_of_icefield": per_troop["koi_points"] * qty,
                        "state_of_power": per_troop["svs_points"] * qty
                    },
                    "source_ids": ["SRC_TROOP_CALCULATOR"],
                    "evidence": {"sample_key": f"{troop_type}_T{tier}_qty{qty}_train"},
                    "confidence": {"grade": "B", "reason": "calculator output capture"}
                }
                edges.append(edge)

    return edges, missing


def build_promote_edges(promote_data: dict) -> tuple[list, list]:
    """Build promotion edges for all combinations."""
    edges = []
    missing = []
    per_troop_costs = promote_data["per_troop_promotion_costs"]

    for troop_type in TROOP_TYPES:
        for tier_from, tier_to in PROMOTE_TIERS:
            per_troop = get_per_troop_promote_cost(per_troop_costs, troop_type, tier_from, tier_to)
            if not per_troop:
                missing.append({"type": troop_type, "tier_from": tier_from, "tier_to": tier_to})
                continue

            for qty in QUANTITIES:
                edge = {
                    "upgrade_id": f"troops_promote:{troop_type}:T{tier_from}->T{tier_to}:qty{qty}",
                    "from": {
                        "action": "promote",
                        "troop_type": troop_type,
                        "tier_from": tier_from,
                        "tier_to": tier_to,
                        "qty": qty
                    },
                    "to": {
                        "result": "promoted",
                        "troop_type": troop_type,
                        "tier_from": tier_from,
                        "tier_to": tier_to,
                        "qty": qty
                    },
                    "cost": {
                        "meat": per_troop["meat"] * qty,
                        "wood": per_troop["wood"] * qty,
                        "coal": per_troop["coal"] * qty,
                        "iron": per_troop["iron"] * qty,
                        "fire_crystal": 0,
                        "speedups_seconds": 0
                    },
                    "time_seconds": per_troop["time_seconds"] * qty,
                    "benefit": {
                        "power_gained": per_troop["power_gained"] * qty
                    },
                    "event_points": {
                        "hall_of_chiefs": per_troop["hoc_points"] * qty,
                        "king_of_icefield": per_troop["koi_points"] * qty,
                        "state_of_power": per_troop["svs_points"] * qty
                    },
                    "source_ids": ["SRC_TROOP_CALCULATOR"],
                    "evidence": {"sample_key": f"{troop_type}_T{tier_from}_to_T{tier_to}_qty{qty}_promote"},
                    "confidence": {"grade": "B", "reason": "calculator output capture"}
                }
                edges.append(edge)

    return edges, missing


def check_linearity(edges: list, action_type: str) -> tuple[bool, list]:
    """
    Check that costs scale linearly between qty=1000 and qty=10000.
    Tolerance: 1%
    """
    issues = []

    # Group edges by (troop_type, tier) or (troop_type, tier_from, tier_to)
    edge_groups = {}
    for edge in edges:
        if action_type == "train":
            key = (edge["from"]["troop_type"], edge["from"]["tier"])
        else:
            key = (edge["from"]["troop_type"], edge["from"]["tier_from"], edge["from"]["tier_to"])

        qty = edge["from"]["qty"]
        if key not in edge_groups:
            edge_groups[key] = {}
        edge_groups[key][qty] = edge

    # Check linearity for each group
    for key, qty_edges in edge_groups.items():
        if 1000 not in qty_edges or 10000 not in qty_edges:
            continue

        edge_1000 = qty_edges[1000]
        edge_10000 = qty_edges[10000]

        for resource in ["meat", "wood", "coal", "iron"]:
            cost_1000 = edge_1000["cost"][resource]
            cost_10000 = edge_10000["cost"][resource]
            expected = cost_1000 * 10

            if cost_1000 == 0:
                continue

            deviation = abs(cost_10000 - expected) / expected
            if deviation > 0.01:  # 1% tolerance
                issues.append({
                    "key": str(key),
                    "resource": resource,
                    "cost_1000": cost_1000,
                    "cost_10000": cost_10000,
                    "expected": expected,
                    "deviation_pct": round(deviation * 100, 2)
                })

    return len(issues) == 0, issues


def validate_edges(train_edges: list, promote_edges: list) -> dict:
    """Run all validations."""
    issues = []

    # Check for duplicates
    train_ids = set()
    for edge in train_edges:
        if edge["upgrade_id"] in train_ids:
            issues.append(f"Duplicate train edge: {edge['upgrade_id']}")
        train_ids.add(edge["upgrade_id"])

    promote_ids = set()
    for edge in promote_edges:
        if edge["upgrade_id"] in promote_ids:
            issues.append(f"Duplicate promote edge: {edge['upgrade_id']}")
        promote_ids.add(edge["upgrade_id"])

    # Check all costs are non-negative
    for edge in train_edges + promote_edges:
        for resource, amount in edge["cost"].items():
            if amount < 0:
                issues.append(f"Negative cost {resource}={amount} in {edge['upgrade_id']}")

    # Check promotion sanity
    for edge in promote_edges:
        tier_from = edge["from"]["tier_from"]
        tier_to = edge["from"]["tier_to"]
        if tier_to != tier_from + 1:
            issues.append(f"Invalid promotion {tier_from}->{tier_to} in {edge['upgrade_id']}")
        if edge["from"]["qty"] <= 0:
            issues.append(f"Invalid qty in {edge['upgrade_id']}")

    # Linearity checks
    train_linear_ok, train_linear_issues = check_linearity(train_edges, "train")
    promote_linear_ok, promote_linear_issues = check_linearity(promote_edges, "promote")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "linearity_ok": train_linear_ok and promote_linear_ok,
        "train_linearity_issues": train_linear_issues,
        "promote_linearity_issues": promote_linear_issues
    }


def main():
    print("Loading raw data...")
    train_data, promote_data = load_raw_data()

    print("Building training edges...")
    train_edges, train_missing = build_train_edges(train_data)

    print("Building promotion edges...")
    promote_edges, promote_missing = build_promote_edges(promote_data)

    print("Validating edges...")
    validation = validate_edges(train_edges, promote_edges)

    # Build output files
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    train_output = {
        "system": "troops_train",
        "unit": "batch",
        "currencies": ["meat", "wood", "coal", "iron", "fire_crystal", "speedups_seconds"],
        "generated_at": timestamp,
        "notes": [
            "Training costs scale linearly with quantity",
            "Time is base time before speed buffs",
            "Event points from HOC (Hall of Chiefs), KoI (King of Icefield), SvS (State of Power)"
        ],
        "edges": train_edges
    }

    promote_output = {
        "system": "troops_promote",
        "unit": "batch",
        "currencies": ["meat", "wood", "coal", "iron", "fire_crystal", "speedups_seconds"],
        "generated_at": timestamp,
        "notes": [
            "Promotion costs = training_cost(tier_to) - training_cost(tier_from)",
            "Time is base time before speed buffs",
            "Promotion is more resource-efficient than training from scratch"
        ],
        "edges": promote_edges
    }

    # Build report
    report = {
        "system": "troops",
        "generated_at": timestamp,
        "ok": validation["ok"] and len(train_missing) == 0 and len(promote_missing) == 0,
        "train_edges": len(train_edges),
        "promote_edges": len(promote_edges),
        "troop_types": TROOP_TYPES,
        "train_tiers": TRAIN_TIERS,
        "promote_tiers": [f"T{f}->T{t}" for f, t in PROMOTE_TIERS],
        "quantities": QUANTITIES,
        "train_missing": train_missing,
        "promote_missing": promote_missing,
        "linearity_ok": validation["linearity_ok"],
        "train_linearity_issues": validation["train_linearity_issues"],
        "promote_linearity_issues": validation["promote_linearity_issues"],
        "integrity_issues": validation["issues"],
        "notes": []
    }

    if not validation["linearity_ok"]:
        report["notes"].append("Linearity check failed - costs may have rounding or breakpoints")

    # Save files
    print(f"Saving training edges to {TRAIN_EDGES_FILE}...")
    TRAIN_EDGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRAIN_EDGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(train_output, f, indent=2)

    print(f"Saving promotion edges to {PROMOTE_EDGES_FILE}...")
    with open(PROMOTE_EDGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(promote_output, f, indent=2)

    print(f"Saving report to {REPORT_FILE}...")
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("TROOPS BUILD COMPLETE")
    print("="*60)
    print(f"Training edges: {report['train_edges']}")
    print(f"Promotion edges: {report['promote_edges']}")
    print(f"Troop types: {len(TROOP_TYPES)}")
    print(f"Quantities per type/tier: {len(QUANTITIES)}")
    print(f"Linearity: {'OK' if report['linearity_ok'] else 'ISSUES'}")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")

    if train_missing:
        print(f"WARNING: {len(train_missing)} missing training tiers")
    if promote_missing:
        print(f"WARNING: {len(promote_missing)} missing promotion tiers")

    print("="*60)

    return report["ok"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
