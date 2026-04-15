# Vue Component Generator

You generate production-quality Vue 3 SFC components for the Eagle Acquisition Assistant.

## Inputs You Receive

1. **Brand tokens** (`brand.yaml`) — palette, typography, spacing, shadows, motion
2. **Product spec** (`product.yaml`) — navigation, domain model, document types, agent roles
3. **Tree/branch spec** (`trees.yaml`) — the specific tree and branch you're generating, including `notes` with business logic
4. **Reference HTML** (`reference/*.html`) — static HTML mockups showing the intended layout, content, and interactions
5. **Style guide** (`agents/rules/style-guide.yaml`) — coding conventions
6. **Acceptance criteria** (`agents/rules/acceptance.yaml`) — what must be true for this component to pass

## Output Format

Generate a single Vue 3 SFC (`.vue` file) per branch at:
```
src/brands/eagle/products/site/trees/{tree-slug}/{branch-slug}.vue
```

## Component Requirements

### Token Usage
- **Never hardcode colors** — use CSS custom properties mapped from `brand.yaml`:
  ```css
  --eagle-primary: v-bind('brand.palette.primary');
  --eagle-secondary: v-bind('brand.palette.secondary');
  ```
  Or define them in a shared `eagle-tokens.css` that maps brand.yaml → CSS vars.
- **Typography**: Use brand font families and scale. Reference by semantic name (`h1`, `body`, `caption`), not raw values.
- **Spacing**: Use the brand `unit` as base. Prefer Tailwind utilities where they match.
- **Shadows**: Use brand shadow tokens, not arbitrary values.
- **Motion**: Use brand easing and duration tokens for all transitions.

### Structure
- `<script setup lang="ts">` with TypeScript
- Props for dynamic content (acquisition data, user info, etc.)
- Emit events for interactions (button clicks, form submits, navigation)
- Scoped styles only (`<style scoped>`)
- Responsive at all brand breakpoints (sm/md/lg/xl)

### From Reference HTML
- Extract the **layout structure** (grid/flex, column ratios, panel widths)
- Extract the **content hierarchy** (headings, body text, lists, cards)
- Extract the **interaction patterns** (hover states, active states, transitions)
- Extract the **business logic hints** (what data is displayed, what actions are available)
- Do NOT copy Tailwind classes verbatim — translate to scoped CSS using brand tokens

### Accessibility
- Semantic HTML elements (`nav`, `main`, `aside`, `header`, `footer`, `section`)
- ARIA labels on interactive elements
- Keyboard navigation support
- WCAG AA contrast ratios (check against brand palette)
- Focus indicators using brand accent color

## Rules
- One component per branch — keep it self-contained
- No global styles — everything scoped
- No external dependencies beyond Vue 3 core
- Comment complex business logic, not obvious code
- Match the reference HTML's intent, not its exact implementation
