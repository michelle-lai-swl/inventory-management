---
name: vue-analyze
description: Analyzes Vue 3 component structure in client/src/views/ and suggests concrete performance and code-reuse optimizations specific to this project's patterns.
---

# Vue Component Analysis

Analyze the Vue 3 components in `client/src/views/` for performance bottlenecks and code-reuse opportunities. Produce a structured report followed by concrete, actionable suggestions.

## Step 1 — Read the components

Read all files in `client/src/views/*.vue` plus `client/src/api.js` and `client/src/App.vue` to understand the full picture before making any judgements.

## Step 2 — Performance checks

For each component, flag:

### Methods called in templates (should be computed)
- Any method invocation inside `{{ }}`, `:prop`, `v-if`, or `v-for` that returns a derived value and is called more than once or depends on reactive state.
- Example pattern to detect: `getOrdersByStatus('Delivered').length` appearing multiple times → extract to `const deliveredOrders = computed(...)`.

### Inline template expressions that are too complex
- Style bindings with arithmetic: `:style="{ width: (summary.total_orders_value / revenueGoal * 100) + '%' }"` → move to computed.
- Ternary chains inside `{{ }}` that span more than one condition.

### Hardcoded values that bypass reactivity
- Literal numbers/strings in templates that should come from data or constants (e.g., hardcoded `style="width: 93.33%"`).

### Wasteful v-if / v-show usage
- `v-if` on elements toggled frequently at runtime → suggest `v-show`.
- `v-show` on elements that are almost never shown or are very heavy → suggest `v-if`.

### v-for key quality
- `key="index"` → flag and suggest a domain-specific unique key (sku, id, order_number, month, etc.).

## Step 3 — Code-reuse checks

### Repeated loading/error state pattern
All views repeat the same three-state guard:
```html
<div v-if="loading">…</div>
<div v-else-if="error">…</div>
<div v-else>…</div>
```
Suggest extracting a `<AsyncState :loading="loading" :error="error">` wrapper component in `client/src/components/`.

### Repeated KPI / stat card markup
Look for blocks of `<div class="kpi-card">` or `<div class="stat-card …">` that repeat an identical structure with different data. Suggest a `<KpiCard>` or `<StatCard>` component that accepts props.

### Shared formatting functions defined per-component
- `formatCurrency`, `calculatePercentage`, `formatNumber`, date utilities — if they appear in more than one component they belong in a `client/src/utils/format.js` module.

### Shared data-loading logic
All views follow the same `loading / error / try-catch / finally` pattern. Suggest a composable:
```javascript
// client/src/composables/useAsyncData.js
export function useAsyncData(fetchFn) { … }
```

### Filter state duplication
If multiple views independently call `getCurrentFilters()` and watch the same filter refs, suggest verifying the shared `useFilters` composable is used consistently rather than duplicated.

## Step 4 — Output format

Produce a report with these sections:

```
## Performance Issues
- [ComponentName.vue] <issue> → <suggested fix>

## Code Reuse Opportunities
- <opportunity> → <suggested extraction> (affects: ComponentA, ComponentB, …)

## Quick Wins (low-effort, high-impact)
Bullet list of the 3–5 highest-ROI changes.

## Suggested New Files
List any new composables, utilities, or components proposed, with a one-line description each.
```

Keep suggestions concrete — include the line or pattern being flagged, not just general advice. Where a fix is non-trivial, sketch the proposed API (component props or composable signature) in a short code block.

After producing the report, ask the user which items they want implemented, then delegate implementation of any `.vue` file changes to the **vue-expert** subagent.
