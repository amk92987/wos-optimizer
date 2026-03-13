---
name: wos-design-review
description: Review UI/UX changes for visual consistency, accessibility, theme compliance, and component pattern adherence. Use when UI components or pages are created or modified.
allowed-tools: Read, Glob, Grep, Bash(npm:*), WebFetch
---

# WoS Design Review - UI/UX Consistency & Accessibility

## Purpose
Reviews frontend UI changes for consistency with the Arctic Night frost/winter theme, adherence to established component patterns, accessibility compliance, and mobile responsiveness. Catches visual regressions, theme violations, and UX anti-patterns before they reach users.

## When to Use
- After creating or modifying React components
- When building new pages in `frontend/app/`
- When changing CSS variables or Tailwind classes
- After modifying the component library (`frontend/components/`)
- When changing layout, navigation, or tab patterns
- Before deploying UI changes to dev or live

## Arctic Night Theme Reference

The theme is defined in `frontend/app/globals.css`. All UI must use these CSS variables:

### Color Palette
| Variable | Value | Usage |
|----------|-------|-------|
| `--glacier-50` to `--glacier-900` | Blue scale (#E8F4F8 to #060D15) | Primary palette |
| `--ice` / `--ice-light` | #4A90D9 / #7DD3FC | Interactive elements, links |
| `--frost` / `--frost-muted` | #E8F4F8 / #B8D4E8 | Text highlights, headings |
| `--fire` / `--fire-light` | #FF6B35 / #FF8C42 | Warnings, emphasis, CTAs |
| `--gold` | #FFD700 | Stars, premium indicators |
| `--background` | #0A1628 | Page background |
| `--background-light` | #122340 | Elevated sections |
| `--surface` / `--surface-hover` | #1A3A5C / #2E5A8C | Cards, panels |
| `--card-bg` | rgba(35, 61, 93, 0.4) | Card backgrounds |
| `--text-primary` | #E8F4F8 | Main text |
| `--text-secondary` | #8F9DB4 | Secondary text |
| `--text-muted` | #5A6A7A | Disabled, hints |
| `--border` / `--border-subtle` | rgba(74, 144, 217, 0.3/0.15) | Borders |
| `--success` / `--warning` / `--error` / `--info` | Green/Amber/Red/Blue | Status indicators |

### Theme Rules
1. NEVER use hardcoded colors -- always use CSS variables or Tailwind classes mapped to them
2. Dark backgrounds with light text (dark theme only)
3. Ice-blue for interactive elements; fire-orange for warnings/emphasis
4. Gold for star ratings and premium content
5. Semi-transparent card backgrounds for depth

## Component Library

### Shared UI Components (`frontend/components/ui/`)

| Component | File | Usage |
|-----------|------|-------|
| Badge | `Badge.tsx` | Status labels, tier indicators |
| DataTable | `DataTable.tsx` | Tabular data display |
| MetricCard | `MetricCard.tsx` | Dashboard stat cards |
| Modal | `Modal.tsx` | Dialog overlays |
| ProgressBar | `ProgressBar.tsx` | Level/completion indicators |
| Skeleton | `Skeleton.tsx` | Loading placeholders |
| Tabs | `Tabs.tsx` | Tab-based navigation |
| Toast | `Toast.tsx` | Notification toasts |
| Toggle | `Toggle.tsx` | Boolean switches |
| Tooltip | `Tooltip.tsx` | Hover information |

### Hero Components (`frontend/components/hero/`)

| Component | File | Usage |
|-----------|------|-------|
| GearSlotEditor | `GearSlotEditor.tsx` | Inline gear quality/level/mastery editing |
| MythicGearEditor | `MythicGearEditor.tsx` | Exclusive gear toggle + editors |
| NumberStepper | `NumberStepper.tsx` | `[-] value [+]` reusable control |
| SaveIndicator | `SaveIndicator.tsx` | Auto-save status (saving/saved/error) |
| SkillPips | `SkillPips.tsx` | Clickable skill level circles |
| StarRating | `StarRating.tsx` | Clickable stars + ascension pips |

### Layout Components (`frontend/components/`)

| Component | File | Usage |
|-----------|------|-------|
| AppShell | `AppShell.tsx` | Main layout wrapper with sidebar |
| Sidebar | `Sidebar.tsx` | Navigation sidebar |
| PageLayout | `PageLayout.tsx` | Standard page wrapper |
| Expander | `Expander.tsx` | Collapsible sections |
| HeroCard | `HeroCard.tsx` | Hero display with auto-save |
| HeroDetailModal | `HeroDetailModal.tsx` | Full hero detail view |
| HeroRoleBadges | `HeroRoleBadges.tsx` | Role indicator badges |

## Key Patterns to Enforce

### 1. Always-Interactive Hero Cards
- No edit/save/cancel buttons -- all fields auto-save via `useAutoSave` hook
- Debounced 300ms saves with optimistic UI updates
- SaveIndicator shows saving/saved/error status
- HeroCard props: `hero`, `token`, `onSaved?`, `onRemove?` (no `onUpdate`)

### 2. Tab Navigation
- Use the shared `Tabs` component from `frontend/components/ui/Tabs.tsx`
- Tab selectors must be standardized across pages (check `ba577bd` commit)
- Tabs should be keyboard-accessible (arrow keys, Enter)

### 3. Admin Page Conventions
- Admin pages live in `frontend/app/admin/`
- Use MetricCard for dashboard statistics
- DataTable for tabular admin data
- Toggle for feature flags and boolean settings
- Red "danger zone" styling for destructive actions

### 4. Mobile Responsiveness
- Playwright has a `mobile-chrome` project testing mobile nav (`frontend/e2e/tests/navigation/mobile-nav.spec.ts`)
- Sidebar collapses to hamburger menu on mobile
- Cards stack vertically on small screens
- Touch targets minimum 44x44px
- NumberStepper buttons must be easily tappable

### 5. Rarity Border Colors
- Blue = Rare heroes
- Purple = Epic heroes
- Gold/Yellow = Legendary heroes
- Applied via border color on hero cards

## Review Checklist

### Visual Consistency
- [ ] Uses CSS variables from `globals.css`, not hardcoded colors
- [ ] Card backgrounds use `--card-bg` or `--surface`
- [ ] Text uses `--text-primary`, `--text-secondary`, or `--text-muted`
- [ ] Interactive elements use `--ice` / `--ice-light`
- [ ] Status indicators use `--success` / `--warning` / `--error` / `--info`
- [ ] Borders use `--border` or `--border-subtle`
- [ ] No white or light backgrounds (dark theme only)

### Component Reuse
- [ ] Uses existing UI components instead of custom implementations
- [ ] NumberStepper for all increment/decrement inputs
- [ ] Tabs component for tabbed content
- [ ] Badge for status labels
- [ ] Modal for overlays (not custom dialogs)
- [ ] Tooltip for hover information
- [ ] Skeleton for loading states
- [ ] Toast for notifications

### Accessibility
- [ ] All images have alt text
- [ ] Interactive elements are focusable (tabIndex, role)
- [ ] Color is not the sole indicator (add text/icon)
- [ ] Sufficient color contrast (text on background)
- [ ] Keyboard navigation works (Tab, Enter, Escape, Arrow keys)
- [ ] ARIA labels on icon-only buttons
- [ ] Form inputs have associated labels

### Responsiveness
- [ ] Layout works on mobile (320px width)
- [ ] No horizontal scroll on small screens
- [ ] Touch targets are at least 44x44px
- [ ] Text is readable without zooming
- [ ] Tables scroll horizontally or reflow on mobile
- [ ] Modals are full-screen on mobile

### Auto-Save Pattern
- [ ] Uses `useAutoSave` hook (not manual save buttons)
- [ ] SaveIndicator visible near editable content
- [ ] Optimistic UI updates (don't wait for server)
- [ ] Error state reverts and shows feedback
- [ ] No "Submit" / "Save" / "Cancel" buttons on data entry forms

## Workflow

1. **Identify changed files** - Read the modified/new component or page files
2. **Check theme compliance** - Grep for hardcoded colors, verify CSS variable usage
3. **Verify component reuse** - Check if existing UI components could replace custom code
4. **Test accessibility** - Review ARIA attributes, focus management, keyboard nav
5. **Check responsiveness** - Look for fixed widths, overflow issues, small touch targets
6. **Verify patterns** - Auto-save, tab navigation, admin conventions
7. **Report findings** - Categorize as Critical / Warning / Suggestion

## Key Files to Reference

- `frontend/app/globals.css` - Theme definition and CSS variables
- `frontend/components/ui/index.ts` - UI component exports
- `frontend/components/hero/*.tsx` - Hero component patterns
- `frontend/components/HeroCard.tsx` - Reference implementation for auto-save pattern
- `frontend/hooks/useAutoSave.ts` - Auto-save hook implementation
- `frontend/components/ui/Tabs.tsx` - Tab component reference
- `frontend/app/layout.tsx` - Root layout structure

## Output Format

```markdown
## UI/UX Design Review

### Summary
Brief overview of changes reviewed and overall assessment.

### Critical Issues
Issues that MUST be fixed before deployment:
1. [CRITICAL] Description of issue with file:line reference

### Warnings
Issues that SHOULD be fixed:
1. [WARNING] Description with file:line reference

### Suggestions
Nice-to-have improvements:
1. [SUGGESTION] Description with file:line reference

### Theme Compliance: PASS/FAIL
### Component Reuse: PASS/FAIL
### Accessibility: PASS/FAIL
### Responsiveness: PASS/FAIL

### Overall: PASS / NEEDS CHANGES
```

## Common Anti-Patterns to Flag

1. **Hardcoded colors** - `color: #fff` instead of `color: var(--text-primary)`
2. **Custom modals** - Building dialogs from scratch instead of using Modal component
3. **Manual save buttons** - Adding Save/Cancel instead of using auto-save pattern
4. **Missing loading states** - Not using Skeleton component during data fetches
5. **Fixed pixel widths** - `width: 500px` instead of responsive units
6. **Emoji in buttons** - Streamlit quirk: emoji chars don't render in certain contexts
7. **Missing error states** - Not handling API errors with Toast or inline feedback
8. **Non-semantic HTML** - Using div for clickable elements instead of button
