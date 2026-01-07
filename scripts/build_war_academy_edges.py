"""
Build War Academy edges from raw table data.
Converts raw rows to upgrade edges with prerequisites and generates validation report.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "war_academy.table.json"
EDGES_FILE = PROJECT_ROOT / "data" / "upgrades" / "war_academy.steps.json"
REPORT_FILE = PROJECT_ROOT / "data" / "validation" / "war_academy.report.json"


def load_raw_data():
    """Load raw table data."""
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_edges(raw_data: dict) -> tuple[list, dict]:
    """
    Convert raw rows to edges.
    Returns (edges_list, validation_info).
    """
    tier_order = raw_data["tier_order"]
    rows = raw_data["rows"]

    # Build lookup: level -> row
    row_lookup = {}
    duplicates = []
    for row in rows:
        key = row["level"]
        if key in row_lookup:
            duplicates.append(key)
        row_lookup[key] = row

    # Track edges and issues
    edges = []
    missing_nodes = []
    orphan_edges = []

    # Build level index for next level lookup
    level_index = {level: i for i, level in enumerate(tier_order)}

    for row in rows:
        level = row["level"]
        current_idx = level_index.get(level)

        # Determine next level
        if current_idx is not None and current_idx + 1 < len(tier_order):
            next_level = tier_order[current_idx + 1]
        else:
            # Last level, no next edge
            continue

        # Check if next level exists
        if next_level not in row_lookup:
            orphan_edges.append({
                "from": level,
                "to": next_level
            })
            continue

        next_row = row_lookup[next_level]

        # Build edge - cost comes from the FROM node (what you pay to upgrade TO next)
        edge = {
            "upgrade_id": f"war_academy:{level}->{next_level}",
            "from": {"level": level},
            "to": {"level": next_level},
            "cost": {
                "fire_crystal_shards": row["fire_crystal_shards"],
                "refined_fire_crystals": row["refined_fire_crystals"],
                "meat": row["meat"],
                "wood": row["wood"],
                "coal": row["coal"],
                "iron": row["iron"]
            },
            "prereq": {
                "furnace_fc_level": row["prereq_furnace"]
            },
            "time_seconds": row["time_seconds"],
            "power_gain": next_row["power"] - row["power"],
            "source_ids": ["SRC_WIKI_WAR_ACADEMY"],
            "evidence": {"source_row_key": row["row_key"]},
            "confidence": {"grade": "A", "reason": "direct table row"}
        }
        edges.append(edge)

    # Check for missing nodes
    for level in tier_order:
        if level not in row_lookup:
            missing_nodes.append(level)

    validation_info = {
        "duplicates": duplicates,
        "missing_nodes": missing_nodes,
        "orphan_edges": orphan_edges
    }

    return edges, validation_info


def validate_edges(edges: list) -> dict:
    """Run edge integrity validation."""
    # Check for duplicate outgoing edges
    from_nodes = {}
    for edge in edges:
        key = edge["from"]["level"]
        if key in from_nodes:
            return {"ok": False, "error": f"Duplicate outgoing edge from {key}"}
        from_nodes[key] = edge

    # Check all costs are non-negative
    for edge in edges:
        for resource, amount in edge["cost"].items():
            if amount < 0:
                return {"ok": False, "error": f"Negative cost {resource}={amount} in {edge['upgrade_id']}"}

    # Check prerequisites are valid FC levels
    valid_fc_levels = {f"FC{i}" for i in range(1, 11)}
    for edge in edges:
        prereq = edge["prereq"]["furnace_fc_level"]
        if prereq not in valid_fc_levels:
            return {"ok": False, "error": f"Invalid prerequisite {prereq} in {edge['upgrade_id']}"}

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
        "system": "war_academy",
        "unit": "level",
        "currencies": ["fire_crystal_shards", "refined_fire_crystals", "meat", "wood", "coal", "iron"],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "notes": [
            "Each research applies to all 3 troop types (Infantry, Marksman, Lancer)",
            "Prerequisites refer to Furnace Core building level",
            "Refined Fire Crystals appear starting at FC5-1"
        ],
        "edges": edges
    }

    # Build report
    levels_found = list(set(e["from"]["level"] for e in edges))
    levels_found.sort(key=lambda l: raw_data["tier_order"].index(l) if l in raw_data["tier_order"] else 999)

    report = {
        "system": "war_academy",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ok": integrity["ok"] and len(validation_info["duplicates"]) == 0 and len(validation_info["missing_nodes"]) == 0,
        "levels_found": levels_found,
        "rows": len(raw_data["rows"]),
        "edges": len(edges),
        "duplicates": validation_info["duplicates"],
        "missing_nodes": validation_info["missing_nodes"],
        "orphan_edges": validation_info["orphan_edges"],
        "integrity": integrity,
        "notes": []
    }

    if validation_info["orphan_edges"]:
        report["notes"].append(f"{len(validation_info['orphan_edges'])} orphan edges (last level has no next level)")

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
    print("WAR ACADEMY BUILD COMPLETE")
    print("="*60)
    print(f"Rows processed: {report['rows']}")
    print(f"Edges generated: {report['edges']}")
    print(f"Levels: {len(levels_found)}")
    print(f"Status: {'OK' if report['ok'] else 'FAILED'}")

    if report["duplicates"]:
        print(f"WARNING: {len(report['duplicates'])} duplicates found")
    if report["missing_nodes"]:
        print(f"WARNING: {len(report['missing_nodes'])} missing nodes")
    if report["orphan_edges"]:
        print(f"INFO: {len(report['orphan_edges'])} orphan edges (expected for last level)")

    print("="*60)

    return report["ok"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
