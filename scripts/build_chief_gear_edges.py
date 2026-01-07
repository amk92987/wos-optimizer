"""
Build Chief Gear edges from raw table data.
Converts raw rows to upgrade edges and generates validation report.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "chief_gear.table.json"
EDGES_FILE = PROJECT_ROOT / "data" / "upgrades" / "chief_gear.steps.json"
REPORT_FILE = PROJECT_ROOT / "data" / "validation" / "chief_gear.report.json"


def load_raw_data():
    """Load raw table data."""
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_max_step(tier: str, steps_config: dict) -> int:
    """Get maximum step for a tier."""
    exceptions = steps_config.get("exceptions", {})
    if tier in exceptions:
        return exceptions[tier]
    return steps_config.get("default", 4)


def build_edges(raw_data: dict) -> tuple[list, dict]:
    """
    Convert raw rows to edges.
    Returns (edges_list, validation_info).
    """
    tier_order = raw_data["tier_order"]
    steps_config = raw_data["steps_per_tier"]
    rows = raw_data["rows"]

    # Build lookup: (tier, step) -> row
    row_lookup = {}
    duplicates = []
    for row in rows:
        key = (row["tier"], row["step"])
        if key in row_lookup:
            duplicates.append(key)
        row_lookup[key] = row

    # Track nodes and edges
    edges = []
    missing_nodes = []
    orphan_edges = []

    # Build tier index for next tier lookup
    tier_index = {t: i for i, t in enumerate(tier_order)}

    for row in rows:
        tier = row["tier"]
        step = row["step"]
        max_step = get_max_step(tier, steps_config)

        # Determine next node
        if step < max_step:
            # Same tier, next step
            next_tier = tier
            next_step = step + 1
        else:
            # Next tier, step 1
            current_idx = tier_index.get(tier)
            if current_idx is not None and current_idx + 1 < len(tier_order):
                next_tier = tier_order[current_idx + 1]
                next_step = 1
            else:
                # Last tier, no next edge
                continue

        # Check if next node exists
        next_key = (next_tier, next_step)
        if next_key not in row_lookup:
            orphan_edges.append({
                "from": {"tier": tier, "step": step},
                "to": {"tier": next_tier, "step": next_step}
            })
            continue

        # Build edge
        edge = {
            "upgrade_id": f"chief_gear:{tier}:step{step}->step{next_step}" if tier == next_tier else f"chief_gear:{tier}:step{step}->{next_tier}:step{next_step}",
            "from": {"tier": tier, "step": step},
            "to": {"tier": next_tier, "step": next_step},
            "cost": {
                "hardened_alloy": row["hardened_alloy"],
                "polishing_solution": row["polishing_solution"],
                "design_plan": row["design_plan"],
                "lunar_amber": row["lunar_amber"]
            },
            "source_ids": ["SRC_WIKI_CHIEF_GEAR"],
            "evidence": {"source_row_key": row["row_key"]},
            "confidence": {"grade": "A", "reason": "direct table row"}
        }
        edges.append(edge)

    # Check for missing nodes (expected but not in rows)
    for tier in tier_order:
        max_step = get_max_step(tier, steps_config)
        for step in range(1, max_step + 1):
            if (tier, step) not in row_lookup:
                missing_nodes.append({"tier": tier, "step": step})

    validation_info = {
        "duplicates": [{"tier": t, "step": s} for t, s in duplicates],
        "missing_nodes": missing_nodes,
        "orphan_edges": orphan_edges
    }

    return edges, validation_info


def validate_edges(edges: list) -> dict:
    """Run edge integrity validation."""
    # Check for duplicate outgoing edges
    from_nodes = {}
    for edge in edges:
        key = (edge["from"]["tier"], edge["from"]["step"])
        if key in from_nodes:
            return {"ok": False, "error": f"Duplicate outgoing edge from {key}"}
        from_nodes[key] = edge

    # Check all costs are non-negative
    for edge in edges:
        for resource, amount in edge["cost"].items():
            if amount < 0:
                return {"ok": False, "error": f"Negative cost {resource}={amount} in {edge['upgrade_id']}"}

    return {"ok": True}


def main():
    print("Loading raw data...")
    raw_data = load_raw_data()

    print("Building edges...")
    edges, validation_info = build_edges(raw_data)

    print("Validating edges...")
    integrity = validate_edges(edges)

    # Build output files
    edges_output = {
        "system": "chief_gear",
        "unit": "step",
        "currencies": ["hardened_alloy", "polishing_solution", "design_plan", "lunar_amber"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "edges": edges
    }

    # Build report
    tiers_found = list(set(e["from"]["tier"] for e in edges))
    tiers_found.sort(key=lambda t: raw_data["tier_order"].index(t) if t in raw_data["tier_order"] else 999)

    report = {
        "system": "chief_gear",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "ok": integrity["ok"] and len(validation_info["duplicates"]) == 0 and len(validation_info["missing_nodes"]) == 0,
        "tiers_found": tiers_found,
        "rows": len(raw_data["rows"]),
        "edges": len(edges),
        "duplicates": validation_info["duplicates"],
        "missing_nodes": validation_info["missing_nodes"],
        "orphan_edges": validation_info["orphan_edges"],
        "integrity": integrity,
        "notes": []
    }

    if validation_info["orphan_edges"]:
        report["notes"].append(f"{len(validation_info['orphan_edges'])} orphan edges (last tier step has no next tier)")

    # Save files
    print(f"Saving edges to {EDGES_FILE}...")
    EDGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EDGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(edges_output, f, indent=2)

    print(f"Saving report to {REPORT_FILE}...")
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("CHIEF GEAR BUILD COMPLETE")
    print("="*60)
    print(f"Rows processed: {report['rows']}")
    print(f"Edges generated: {report['edges']}")
    print(f"Tiers: {len(tiers_found)}")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")

    if report["duplicates"]:
        print(f"WARNING: {len(report['duplicates'])} duplicates found")
    if report["missing_nodes"]:
        print(f"WARNING: {len(report['missing_nodes'])} missing nodes")
    if report["orphan_edges"]:
        print(f"INFO: {len(report['orphan_edges'])} orphan edges (expected for last tier)")

    print("="*60)

    return report["ok"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
