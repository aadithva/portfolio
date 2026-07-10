# Component Metadata Schema

Each reusable component should have a metadata record that captures **What**, **How**, and **Why** in a structured form. JSON is preferred for machine parsing; Markdown may be used for longer narrative docs.

## Required fields

```json
{
  "name": "ComponentName",
  "path": "src/components/.../ComponentName.tsx",
  "tier": "atom | molecule | organism | template | page",
  "summary": "One-sentence description of what the component is.",
  "what": "What UI/function this component provides.",
  "why": "Why this component exists in the design system and what consistency it protects.",
  "whenToUse": ["Specific usage scenario."],
  "whenNotToUse": ["Anti-pattern or unsuitable scenario."],
  "propsOrInputs": [
    { "name": "propName", "type": "Type", "required": true, "description": "Meaning and constraints." }
  ],
  "variants": ["Supported visual/behavioral variants."],
  "dependencies": ["Local atoms, molecules, data, hooks, or libraries used."],
  "usedBy": ["Known parents/routes."],
  "examples": [
    { "context": "Where/why", "snippet": "<Component />" }
  ],
  "a11yNotes": ["Accessibility considerations."],
  "version": "0.1.0",
  "lastUpdated": "2026-06-20",
  "source": "Observed from current codebase and generated design-system foundation."
}
```

## Guidance

- `summary` should be compact enough for retrieval.
- `what`, `why`, `whenToUse`, and `whenNotToUse` are the most important AI-selection fields.
- `propsOrInputs` should mirror the real component API. A future validator should compare these to TypeScript source.
- `dependencies` and `usedBy` should be checked against `design-system/ai/index.json`.
- `lastUpdated` should change whenever source or metadata changes.
- Prefer full relative paths as identifiers; avoid filename-only keys.
