# Aadith V A — Portfolio

An evidence-led portfolio for Aadith V A: AI product designer at Microsoft, co-founder of Owly, and design-tool builder.

## What is inside

- Six selected Work chapters spanning enterprise AI, founder work, fintech, early-stage products, Web3, and information design.
- Focused subpages for Microsoft Copilot work and the DaoLens DAO Denver case study.
- A five-project AI Lab covering evaluation, agent behaviour, conversation design, and Figma tooling.
- An AI-ready design system with a generated codebase index and per-component metadata.
- Static, accessible Astro pages with vanilla CSS and minimal client-side JavaScript.

## Run locally

```bash
npm install
npm run dev
```

Build the static site:

```bash
npm run build
```

### Optional Work-page gate

Copy `.env.example` to `.env.local` and set `PUBLIC_WORK_GATE_PASSWORD` to enable the presentation gate on protected Work pages. Because the site is static, this is not secure access control; protected content must remain public-safe.

## Project structure

```text
src/
  components/     Astro UI components
  data/           Work, Lab, navigation, and nested case-study data
  layouts/        Shared page shell
  pages/          Static routes
  styles/         Global and editorial visual system
design-system/
  ai/             Generated index, metadata, and component-selection guidance
public/
  images/         Work imagery and placeholders
  shots/          Lab and product screenshots
```

## Design-system regeneration

After changing components or routes:

```bash
python3 design-system/ai/codebase-index.py
python3 design-system/ai/component-metadata.py
```

## Publication boundary

Microsoft case studies are intentionally public-safe. Confidential product visuals, internal links, customer data, implementation details, metrics, and colleague information are not included.
