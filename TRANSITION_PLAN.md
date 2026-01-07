# Transition Plan: Streamlit → Reflex

## Why Move?
Streamlit limitations hit:
- No icon-only sidebar collapse (requested feature, not implemented)
- Browser link preview can't be hidden
- Limited CSS control over components
- Page reruns on every interaction
- Third-party components are clunky

## Recommended: Reflex
- Python-based, compiles to React
- Full UI control
- Proper state management (no full page reruns)
- Real components (sidebar collapse is trivial)
- Same Python skills transfer

## Migration Strategy

### Phase 1: Setup & Core Structure
- [ ] Install Reflex: `pip install reflex`
- [ ] Initialize project: `reflex init`
- [ ] Set up project structure mirroring current pages
- [ ] Migrate database layer (SQLAlchemy works with Reflex)
- [ ] Create base layout with sidebar

### Phase 2: Migrate Pages (in order of complexity)
1. [ ] **Home** - Simple, good starting point
2. [ ] **Settings** - Form inputs, profile management
3. [ ] **Profiles** - File I/O, JSON handling
4. [ ] **Heroes** - Complex cards, filtering, inline editing
5. [ ] **Lineups** - Display logic, hero slots
6. [ ] **Recommendations** - Engine integration
7. [ ] **Backpack** - Image upload, OCR (if used)
8. [ ] **AI Advisor** - OpenAI integration

### Phase 3: UI Improvements (now possible)
- [ ] Collapsible sidebar with icon-only mode
- [ ] Proper star rating component
- [ ] Smooth transitions/animations
- [ ] No page refresh on interactions
- [ ] Custom tooltips (or none)

### Phase 4: Cleanup
- [ ] Remove Streamlit dependencies
- [ ] Update requirements.txt
- [ ] Update deployment configs
- [ ] Archive old Streamlit code

## What Can Stay the Same
- `database/` - SQLAlchemy models and DB logic
- `engine/` - Recommendation engine
- `data/` - JSON files, hero data
- `.claude/` - Skills and documentation
- Core Python logic throughout

## What Needs Rewriting
- All `pages/*.py` files (UI layer)
- `app.py` (entry point)
- `styles/custom.css` → Reflex styling (Tailwind or custom)

## Estimated Effort
- Phase 1: 2-3 hours
- Phase 2: 4-6 hours (most work here)
- Phase 3: 1-2 hours
- Phase 4: 30 min

## Resources
- Reflex docs: https://reflex.dev/docs
- Reflex components: https://reflex.dev/docs/library
- Examples: https://reflex.dev/docs/gallery

## Decision
Keep Streamlit working for now, transition when ready for a focused effort.
