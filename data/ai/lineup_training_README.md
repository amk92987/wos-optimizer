# Lineup Training Data

This directory contains curated training data exported from lineup comparison runs between Claude and OpenAI. The data is intended for future fine-tuning of local AI models (Ollama/Llama).

## Export Script

Generate training data using:
```bash
python scripts/export_lineup_training_data.py --run-id <ID>
python scripts/export_lineup_training_data.py --run-id 8 --output data/ai/lineup_training_run8
```

## Quality Flags

Each training example is annotated with a quality flag to help filter data:

| Flag | Meaning | Use for Training? |
|------|---------|-------------------|
| `gold_standard` | Both AIs agreed - high confidence correct answer | Yes - best examples |
| `valid_alternative` | Both valid strategies (e.g., Jeronimo vs Wu Ming for Crazy Joe) | Yes - include both as valid |
| `claude_correct` | OpenAI made roster constraint error - use Claude answer | Yes - use Claude's answer |
| `parser_false_positive` | Same answer, parsing issue (e.g., "Mia (Marksman, Gen 3)") | Skip - not a real disagreement |
| `needs_review` | Unclear which is correct | Skip - requires human review |

## Known Valid Strategic Debates

These hero choices are both acceptable depending on play style:

- **Crazy Joe**: Jeronimo (burst damage) vs Wu Ming (sustained defense)
- **SvS March**: Jeronimo (offense) vs Wu Ming (survivability)
- **Bear Trap**: Hendrik vs Xura (both S-tier Marksman)

When training, include BOTH alternatives as correct answers for these scenarios.

## Data Format

### JSONL Format (for Ollama fine-tuning)
```jsonl
{"prompt": "...", "response": "...", "quality": "gold_standard"}
{"prompt": "...", "response": "...", "quality": "valid_alternative"}
```

### JSON Format (for review)
```json
[
  {
    "prompt": "User roster and question",
    "response": "Claude's lineup recommendation",
    "quality": "gold_standard",
    "quality_reason": "Both AIs agreed - high confidence correct answer",
    "profile": "Gen10_Dolphin",
    "scenario": "bear_trap",
    "metadata": {
      "run_id": 8,
      "slot1_match": true,
      "heroes_match": 3
    }
  }
]
```

## What NOT to Train On

1. **Parser errors** (`parser_false_positive`) - These are false disagreements caused by parsing issues like extra parenthetical info in hero names

2. **Roster violations** - Recommendations that suggest heroes the user doesn't own (indicated when Claude is correct but OpenAI isn't)

3. **Unreviewed examples** (`needs_review`) - These need human verification before use

## Recommended Training Approach

1. Start with `gold_standard` examples only (highest confidence)
2. Add `claude_correct` examples (expands coverage)
3. Include `valid_alternative` examples with BOTH answers marked as acceptable
4. Skip all other quality flags

## Related Files

- `scripts/export_lineup_training_data.py` - Export script
- `scripts/run_lineup_comparison.py` - Comparison runner
- `scripts/test_lineups.py` - Test profile definitions
- `engine/analyzers/lineup_builder.py` - Lineup engine with templates
- `database/models.py` - `LineupTestResult` model with quality annotations

## Comparison Run History

Check the database table `lineup_test_runs` for past comparison runs:
```sql
SELECT id, timestamp, profiles_tested, scenarios, notes FROM lineup_test_runs ORDER BY id DESC;
```
