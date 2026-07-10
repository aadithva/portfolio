# Aadith V A — Portfolio

An evidence-led portfolio for Aadith V A: AI product designer at Microsoft, co-founder of Owly, and design-tool builder.

## What is inside

- Six selected Work chapters spanning enterprise AI, founder work, fintech, early-stage products, Web3, and information design.
- Focused subpages for Microsoft Copilot work and the DaoLens DAO Denver case study.
- A five-project AI Lab covering evaluation, agent behaviour, conversation design, and Figma tooling.
- A public-context AI companion that sits beside overview pages and steps away on project detail routes.
- An AI-ready design system with a generated codebase index and per-component metadata.
- Static, accessible Astro pages with vanilla CSS, one small React/Motion reply effect, and a secure Azure-hosted model endpoint.

## Run locally

```bash
npm install
npm install --prefix api
npm run dev
```

For local API work, start the Azure Function adapter after copying
`api/local.settings.example.json` to `api/local.settings.json` and filling in
the existing Azure OpenAI resource settings:

```bash
npm run api:start
```

Build and test both surfaces:

```bash
npm run build
npm run api:test
```

### Optional Work-page gate

Copy `.env.example` to `.env.local` and set `PUBLIC_WORK_GATE_PASSWORD` to enable the presentation gate on protected Work pages. Because the site is static, this is not secure access control; protected content must remain public-safe.

### Aadith portfolio companion

Production builds use the deployed `/api/aadith-chat` Container App route.
Set `PUBLIC_AADITH_CHAT_ENDPOINT` in `.env.local` only to override it with a
local Function or mock. The browser never receives an Azure credential.
The built-in production fallback activates only on `aadithva.com`, its `www`
host, and the approved local Astro origins. Staging or alternate hosts must set
an explicit endpoint and add that exact origin to `ALLOWED_ORIGINS`.

The portable handler expects:

- `AZURE_OPENAI_ENDPOINT`
- `AADITH_OPENAI_MODEL` or `AZURE_OPENAI_MODEL`
- `AADITH_CONTEXT_URL`
- `ALLOWED_ORIGINS`
- `RATE_LIMIT_SALT`

Microsoft Entra ID is preferred where the host supports managed identity. The
current shared Container App reuses its secret-backed Azure OpenAI key without
placing that credential in the portfolio or browser.

Production rate limits are stored in the existing FlowSense Azure Storage
account so they apply across replicas. `RATE_LIMIT_MODE=memory` is reserved for
local development.

The companion reads `/aadith-context.json`, a static feed generated from
approved portfolio data and the curated public-safe synthesis in
`src/data/agentGrounding.ts`. Raw private grounding documents are never copied,
committed, or deployed. Private WorkIQ results, credentials, health, finances,
relationships, colleague details, and confidential Microsoft material remain
outside the feed.

The live model deployment is `aadith-companion-luna` on GPT-5.6 Luna. The
Container App image layers the companion proxy over the immutable deployed
FlowSense processor digest, forwards existing processor routes unchanged, and
adds only `/api/aadith-chat`. Run `npm run api:sync-context` before rebuilding
that image so the approved public context is embedded.

## Project structure

```text
src/
  components/     Astro UI components
  data/           Work, Lab, navigation, and nested case-study data
  layouts/        Shared page shell
  pages/          Static routes
  styles/         Global and editorial visual system
api/
  src/             Portable handler, Function adapter, proxy, retrieval, and OpenAI client
  context/         Generated public context embedded in the proxy image
  test/            Node-based retrieval and request validation tests
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
python3 design-system/ai/adoption-report.py
```

## Publication boundary

Microsoft case studies and chatbot context are intentionally public-safe. Confidential product visuals, internal links, customer data, implementation details, metrics, colleague information, and private grounding sources are not included.
