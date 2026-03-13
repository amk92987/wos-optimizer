---
name: wos-openai-review
description: Invoke the OpenAI code review system for a second opinion on code changes. Supports diff-based and file-based reviews across 8 review types. Use for significant changes or cross-cutting modifications.
allowed-tools: Bash, Read, Glob, Grep
---

# WoS OpenAI Code Review - Second Opinion Agent

## Purpose
Invokes the OpenAI review system (`scripts/review/`) to get an independent code review from GPT-4o-mini. Claude Code remains the primary builder; OpenAI acts as a review agent providing a second perspective on code quality, architecture, security, and potential regressions.

## When to Use
- Making significant changes that touch multiple files or subsystems
- Modifying critical paths (auth, data access, payment-related)
- Uncertain about architectural approach
- Before deploying large changes to live
- After refactoring shared components or utilities
- When changing DynamoDB key structures or data models

## Prerequisites

The review system requires an OpenAI API key:

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-..."

# Windows (cmd)
set OPENAI_API_KEY=sk-...

# Unix
export OPENAI_API_KEY=sk-...
```

The key is read from the environment at runtime. It is never logged or stored.

## Review System Architecture

### Key Files
| File | Purpose |
|------|---------|
| `scripts/review/__init__.py` | Package entry point, imports |
| `scripts/review/openai_client.py` | OpenAI API client with retry logic |
| `scripts/review/orchestrator.py` | Review orchestration and coordination |
| `scripts/review/prompts.py` | Prompt templates and ReviewType enum |
| `scripts/review/parser.py` | Response parsing and ReviewResult model |
| `scripts/review/cli.py` | CLI interface for running reviews |

### Review Types

The system supports 8 review types that can be combined:

| Type | Focus | Best For |
|------|-------|----------|
| `code_quality` | Clean code, naming, DRY, complexity | General code changes |
| `ui_ux` | Theme compliance, accessibility, UX | Frontend component changes |
| `architecture` | Design patterns, separation of concerns | Structural changes |
| `integration_impact` | Cross-system effects, API contracts | Changes touching multiple modules |
| `regressions_risks` | Breaking changes, edge cases | Refactoring, data model changes |
| `security_sanity` | Auth, injection, secrets exposure | Auth, API, data access changes |
| `performance_sanity` | N+1 queries, memory, cold starts | Database queries, Lambda handlers |
| `implementation_options` | Alternative approaches, trade-offs | Design decisions |

## How to Invoke Reviews

### Method 1: Python CLI

```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer

# Diff-based review (review uncommitted changes)
.venv/Scripts/python.exe -m scripts.review.cli --diff --types code_quality,regressions_risks

# Review specific files
.venv/Scripts/python.exe -m scripts.review.cli --files backend/handlers/heroes.py frontend/components/HeroCard.tsx --types architecture,integration_impact

# All review types on a diff
.venv/Scripts/python.exe -m scripts.review.cli --diff --types all
```

### Method 2: Python API

```python
from scripts.review import ReviewOrchestrator, ReviewType

orchestrator = ReviewOrchestrator()

# Review a git diff
result = orchestrator.review_diff(
    diff_text="<git diff output>",
    review_types=[ReviewType.CODE_QUALITY, ReviewType.SECURITY_SANITY],
    context="Adding new admin endpoint for bulk user operations"
)

print(result.summary)
for concern in result.top_concerns:
    print(f"  [{concern.severity}] {concern.description}")
```

### Method 3: Manual (for Custom Prompts)

```python
from scripts.review import OpenAIReviewClient

client = OpenAIReviewClient(model="gpt-4o-mini")
result = client.chat(
    system_message="You are a code reviewer for a Next.js + Python Lambda project.",
    user_message="Review this code change: ...",
    response_format={"type": "json_object"}
)
```

## Generating the Diff

### Uncommitted Changes
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer
git diff
```

### Staged Changes
```bash
git diff --cached
```

### Changes Since Last Commit
```bash
git diff HEAD~1
```

### Changes on Current Branch vs Master
```bash
git diff master...HEAD
```

### Specific Files
```bash
git diff -- backend/handlers/heroes.py frontend/components/HeroCard.tsx
```

## Review Workflow

### Quick Review (single concern area)
1. Generate diff of changes
2. Run review with 1-2 relevant types
3. Read summary and top concerns
4. Address critical/high severity items

### Comprehensive Review (pre-deployment)
1. Generate full diff against master
2. Run with all review types: `--types all`
3. Prioritize by severity (critical > high > medium > low)
4. Address critical items before deploying
5. Document accepted risks for deferred items

### Follow-Up Review (after applying fixes)
1. Make changes based on initial review
2. Generate new diff
3. Run focused review on the specific concern area
4. Verify concerns are addressed

## Interpreting Results

### Response Structure
```json
{
  "summary": "Overall assessment of the changes",
  "top_concerns": [
    {
      "severity": "high",
      "category": "security",
      "description": "JWT validation not checked in new endpoint",
      "file": "backend/handlers/new.py",
      "line": 42,
      "suggestion": "Add get_effective_user_id() call"
    }
  ],
  "recommended_changes": [
    "Add error handling for DynamoDB ConditionalCheckFailedException",
    "Use prepare_item() before writing to DynamoDB"
  ],
  "follow_up_questions": [
    "Is this endpoint intended to be publicly accessible?"
  ],
  "confidence": "high"
}
```

### Severity Levels
- **Critical**: Must fix before deploying (security holes, data loss risks)
- **High**: Should fix before deploying (bugs, broken patterns)
- **Medium**: Fix soon (code quality, maintainability)
- **Low**: Nice to have (style, minor optimization)

## Review Type Selection Guide

| Change Type | Recommended Review Types |
|-------------|--------------------------|
| New Lambda handler | `code_quality`, `security_sanity`, `architecture` |
| New frontend page | `ui_ux`, `code_quality`, `architecture` |
| DynamoDB schema change | `regressions_risks`, `integration_impact`, `performance_sanity` |
| Auth/security change | `security_sanity`, `regressions_risks` |
| Refactoring | `regressions_risks`, `architecture`, `code_quality` |
| Performance fix | `performance_sanity`, `regressions_risks` |
| Cross-system feature | `integration_impact`, `architecture`, `regressions_risks` |
| Design decision | `implementation_options`, `architecture` |

## Project-Specific Context for Reviews

When providing context to the reviewer, include:
- The project uses DynamoDB single-table design (PK/SK patterns)
- Lambda functions share a common layer (`backend/common/`)
- Frontend is a static Next.js export (no SSR)
- Auth is via Cognito JWT tokens
- Two copies of heroes.json must stay in sync
- DynamoDB items are dicts (use `.get()` not `getattr()`)
- All JSON reads need `encoding='utf-8'`
- The Arctic Night theme uses CSS variables from globals.css

## Safety Notes

1. **API costs**: Each review call costs OpenAI API tokens. Use targeted review types to minimize cost.
2. **No secrets in diffs**: Sanitize any API keys or credentials from diff text before sending.
3. **OpenAI data policy**: Code sent to OpenAI API may be subject to their data usage policy. Do not send production credentials or PII.
4. **Review is advisory**: OpenAI may produce false positives or miss issues. Use as a supplement to human review, not a replacement.

## Workflow

1. **Determine review scope** - What changed? What's the risk level?
2. **Select review types** - Choose 1-4 relevant types from the 8 available
3. **Generate diff** - Get the code changes as text
4. **Add context** - Brief description of what the changes do and why
5. **Run review** - Invoke via CLI or Python API
6. **Analyze results** - Prioritize by severity
7. **Apply fixes** - Address critical/high items
8. **Optional follow-up** - Re-review after fixes if needed
