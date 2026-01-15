# WoS Lineup Test Skill

## Purpose
Comprehensive testing of the lineup recommendation engine by comparing our rule-based engine against OpenAI and Claude AI recommendations. Stores all data for future training.

## Quick Start

### Step 1: Run a Test Batch First (Recommended!)
```bash
cd /c/Users/adam/PycharmProjects/WoS
.venv/Scripts/python.exe scripts/test_lineups.py --test-batch
```

This runs 3 profiles × 3 scenarios = 9 API calls (~$0.50) to validate the process.

### Step 2: Review Results
```bash
# List results from test run (replace 1 with actual run ID)
.venv/Scripts/python.exe scripts/test_lineups.py --list-results 1

# View detailed result
.venv/Scripts/python.exe scripts/test_lineups.py --view-result 1
```

### Step 3: Run Full Suite (After Validation)
```bash
.venv/Scripts/python.exe scripts/test_lineups.py --run-all --name "Full Run v1"
```

## Command Reference

| Command | Description | Est. Cost |
|---------|-------------|-----------|
| `--test-batch` | 3 profiles × 3 scenarios | ~$0.50 |
| `--run-all` | 39 profiles × 10 scenarios | ~$17 |
| `--profile-group generation` | 14 profiles × 10 scenarios | ~$6 |
| `--dry-run` | No API calls, just preview | $0 |

## Test Profile Groups

| Group | Profiles | Purpose |
|-------|----------|---------|
| `generation` | 14 | Baseline across Gen 2-14 |
| `level_impact` | 6 | Same roster, different levels |
| `gear_impact` | 6 | Same roster, different gear |
| `chief_gear_impact` | 4 | Isolate chief gear effect |
| `charm_impact` | 4 | Isolate charm effect |
| `edge_case` | 5 | Unusual scenarios |

## Scenarios Tested

1. **bear_trap** - Marksman-focused (bear is slow)
2. **crazy_joe** - Infantry-focused (Joe attacks backline)
3. **garrison_defense** - Defending your city
4. **garrison_joiner** - Reinforcing ally (slot 1 matters!)
5. **rally_lead** - Leading a rally attack
6. **rally_joiner** - Joining a rally (slot 1 matters!)
7. **svs_march** - Field battles
8. **alliance_championship** - 3v3 brackets
9. **polar_terror** - Boss fight
10. **capital_clash** - Large scale war

## What Gets Stored

Every test result includes:
- **prompt_sent** - Exact prompt sent to AI (for training)
- **profile_snapshot** - Complete roster data (JSON)
- **openai_lineup** - OpenAI's hero picks + reasoning
- **openai_raw_response** - Full API response
- **claude_lineup** - Claude's hero picks + reasoning
- **claude_raw_response** - Full API response
- **match_score** - How much they agreed

## Reviewing Results

### View Summary Report
```bash
.venv/Scripts/python.exe scripts/test_lineups.py --analyze-run 1
```

Shows:
- Overall match rates
- Match rates by scenario
- Cost summary
- Items needing review

### View Individual Results
```bash
# List all results (sorted by match score, lowest first)
.venv/Scripts/python.exe scripts/test_lineups.py --list-results 1

# View full detail for a specific result
.venv/Scripts/python.exe scripts/test_lineups.py --view-result 42
```

## After Testing: Get Improvement Suggestions

Once you have test results with discrepancies, you can:

1. **Identify patterns** in the disagreements
2. **Feed discrepancies to AI** with our engine code
3. **Get specific code suggestions** for improving the engine

Example prompt for improvement suggestions:
```
I ran lineup tests comparing our engine vs AI. Here are the main discrepancies:

1. Rally Joiner: AI picks Jessie slot 1 (80% of time), our engine picks Jeronimo
2. Garrison Defense: AI prioritizes Sergey, we don't
3. Bear Trap: AI suggests 0/10/90 ratio, we suggest 10/20/70

Our current lineup_builder.py logic is:
[paste relevant code]

What specific changes would you recommend?
```

## Database Tables

- `lineup_test_runs` - Test run metadata and summary stats
- `lineup_test_results` - Individual profile+scenario results
- `lineup_engine_improvements` - Tracked suggestions for engine updates

## Cost Tracking

All costs are logged:
- Token counts (input/output) per API call
- Estimated USD cost per run
- Cumulative totals in test run summary

## Training Data Export

Results are stored in a format suitable for:
- Fine-tuning future models
- Building training datasets
- Analyzing AI reasoning patterns

Query example:
```sql
SELECT prompt_sent, openai_reasoning, claude_reasoning
FROM lineup_test_results
WHERE openai_vs_claude_score > 0.8  -- High agreement = good training data
```
