# WoS Feedback Review Skill

## Purpose
Review pending feedback items (bugs and feature requests) that have been triaged for development. Analyze each item and provide actionable recommendations.

## When to Use
Run this skill when you want Claude to review feedback marked as:
- **pending_fix** - Bugs awaiting investigation/fix
- **pending_update** - Feature requests awaiting implementation

## How It Works

1. Query the database for pending feedback items
2. For each item, analyze and provide:
   - **Bugs**: Root cause analysis, affected files, suggested fix
   - **Features**: Feasibility assessment, implementation outline, effort estimate
   - **Data Errors**: Verify against data files, identify discrepancies

## Usage

```bash
cd /c/Users/adam/PycharmProjects/WoS
```

Then run this Python script to get pending feedback:

```python
from database.db import get_db, init_db
from database.models import Feedback, User

init_db()
db = get_db()

# Get pending items
pending = db.query(Feedback).filter(
    Feedback.status.in_(['pending_fix', 'pending_update'])
).order_by(Feedback.created_at.desc()).all()

print(f"\n{'='*60}")
print(f"PENDING FEEDBACK REVIEW ({len(pending)} items)")
print('='*60)

for item in pending:
    user = db.query(User).filter(User.id == item.user_id).first()
    username = user.username if user else "Anonymous"

    print(f"\n[{item.status.upper()}] #{item.id} - {item.category.title()}")
    print(f"From: {username}")
    if item.page:
        print(f"Page: {item.page}")
    print(f"Description: {item.description}")
    print("-" * 40)

db.close()
```

## Review Process

For each pending item:

### Bugs (pending_fix)
1. Identify the affected page/component from the description
2. Search for relevant code files
3. Analyze potential root cause
4. Propose a fix with specific code changes
5. Note any related issues

### Features (pending_update)
1. Understand the requested functionality
2. Check if similar functionality exists
3. Assess complexity (low/medium/high)
4. Outline implementation steps
5. Identify affected files
6. Note any concerns or dependencies

### Data Errors (pending_fix or pending_update)
1. Identify the data file in question
2. Verify the reported error
3. Check data sources (wiki, whiteoutdata, etc.)
4. Propose correction

## After Review

Once you've analyzed the feedback:
1. Discuss findings with the user
2. Get approval to implement fixes/features
3. Implement the changes
4. After user confirms the fix/feature is working, mark the item as completed using:

```python
from database.db import get_db, init_db
from database.models import Feedback

init_db()
db = get_db()

# Mark specific item as completed
item = db.query(Feedback).filter(Feedback.id == ITEM_ID).first()
if item:
    item.status = 'completed'
    db.commit()
    print(f"Marked feedback #{item.id} as completed")

db.close()
```

**Important**: Only mark as completed AFTER the user confirms the implementation is working correctly. The admin UI does not have a Complete button - this is intentional so that completion is tracked through this skill.

## Example Output

```
## Feedback #12 - Bug: Hero gear not saving

**Analysis**: The user reports that hero gear changes aren't persisting.

**Affected Files**:
- pages/1_Hero_Tracker.py (gear save logic)
- database/models.py (UserHero model)

**Root Cause**: The auto-save logic checks for changes but the gear slot attribute names may be mismatched (gear_slot1 vs gear_slot_1).

**Suggested Fix**:
1. Verify attribute names in Hero Tracker match UserHero model
2. Add explicit save confirmation for gear changes

---

## Feedback #15 - Feature: Export hero roster

**Request**: User wants to export their hero roster as CSV/image.

**Feasibility**: High - similar export exists for feedback

**Implementation**:
1. Add export button to Hero Tracker page
2. Create DataFrame from UserHero data
3. Generate CSV download
4. (Optional) Generate image using matplotlib/pillow

**Affected Files**:
- pages/1_Hero_Tracker.py
```

## Workflow Example

1. Admin marks bug #12 as "To Fix" → moves to Pending Fix tab
2. User runs `/wos-feedback`
3. Claude analyzes and proposes fix
4. User approves: "yes, implement the fix"
5. Claude implements the code changes
6. User tests and confirms: "looks good, it's working now"
7. Claude marks #12 as completed:
   ```python
   item = db.query(Feedback).filter(Feedback.id == 12).first()
   item.status = 'completed'
   db.commit()
   ```
8. Item moves to Completed tab
