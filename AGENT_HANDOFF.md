# Portfolio Agent Handoff

Last audited: 2026-07-11 (IST)

This is the operational handoff for future agents working in this repository.
Read it before changing hosting, the AI companion, Azure resources, public
grounding, or Microsoft portfolio content.

## Current status

The portfolio rebuild, AI companion, Azure model proxy, GitHub push, and free
Vercel deployment are complete.

- Repository: <https://github.com/aadithva/portfolio>
- Branch: `main`
- Live frontend: <https://aadithva-portfolio.vercel.app>
- Public context feed:
  <https://aadithva-portfolio.vercel.app/aadith-context.json>
- Companion API:
  <https://ca-flowsense-processor.nicepond-68f95730.eastus.azurecontainerapps.io/api/aadith-chat>
- Shared processor health route:
  <https://ca-flowsense-processor.nicepond-68f95730.eastus.azurecontainerapps.io/health>

Functional implementation commits:

- `42aec9e` - grounded AI portfolio companion and richer portfolio surfaces
- `69920a8` - free Vercel deployment configuration
- `657a4bb` - canonical metadata aligned with the Vercel production URL

At the end of this audit:

- The Git worktree was clean.
- GitHub's Vercel deployment status was successful.
- The latest Vercel production deployment was ready.
- The Azure Container App revision was healthy.
- The static site, context feed, CORS preflight, and a live model answer worked.

## What is working

### Static portfolio

- Astro 5 static output.
- 35 generated HTML pages.
- Six primary Work chapters with focused Microsoft and DaoLens subpages.
- Curated Lab, About, Adventures, Contact, and Writing surfaces.
- Digibop is used for the `AADITH` wordmark; IBM Plex Mono remains the
  interface typeface.
- Canonical and Open Graph URLs use the live Vercel production host.
- Internal generated-link audit found zero missing internal routes or assets.
- Vercel deploys automatically from GitHub `main`.

### Aadith companion UX

- Persistent right-side companion on overview routes.
- Hidden on `/work/...` and `/lab/...` detail routes so projects use the full
  canvas.
- Mobile drawer works at 320 x 568:
  - panel opens,
  - page background becomes inert,
  - body scrolling is locked,
  - focus moves to the question field,
  - the panel is marked visible to assistive technology.
- Conversation history persists under
  `aadith-companion-session-v1`.
- Up to 10 messages are stored in the browser.
- Up to 8 messages and 3,600 characters are sent to the API.
- Visitor messages are limited to 600 characters.
- Responses lazily load React and the React Bits `DecryptedText` effect.
- Reduced-motion and stable screen-reader text are supported.
- At most three validated internal source links are displayed.
- Alternate origins fail closed if no explicit endpoint is configured.

Primary implementation:

- `src/components/organisms/AadithCompanion.astro`
- `src/components/atoms/DecryptedText.js`
- `src/components/atoms/DecryptedText.css`
- `src/layouts/BaseLayout.astro`
- `src/styles/editorial-mono.css`

### Public grounding and privacy boundary

- Context document version: `2`
- Current public chunks: 30
- Retrieval selects up to five chunks from the latest four conversation
  messages.
- The server returns links for at most the top three selected chunks.
- Context is assembled in `src/data/companion.ts`.
- Curated biographical grounding is in `src/data/agentGrounding.ts`.
- The generated frontend feed is `dist/aadith-context.json`.
- The API image embeds `api/context/aadith-context.json`.
- The two context files matched during the audit.

The raw private grounding source is not tracked, copied, or deployed. The
public boundary excludes health, finances, relationships, family information,
compensation, manager or promotion details, account data, third-party private
information, and unpublished Microsoft information.

Do not weaken this boundary. Do not import a private archive directly into the
site or model context.

### Azure companion API

Azure resources:

- Resource group: `rg-flowsense-prod`
- Container App: `ca-flowsense-processor`
- Registry: `crflowsense`
- Repository: `flowsense-processor`
- Active image tag: `aadith-companion-luna-v6`
- Active image digest:
  `sha256:57b39076b001ff37339a7a52f8f4c45ea47571f41e6e06209f25555a2dcc5935`
- Active/ready revision: `ca-flowsense-processor--0000007`
- Replica range: 0 to 2
- Proxy port: 3003
- Original FlowSense processor port: 3002

Azure OpenAI:

- Account: `aoai-flowsense`
- Deployment: `aadith-companion-luna`
- Model: `gpt-5.6-luna`
- Model version: `2026-07-09`
- Capacity: 10
- Provisioning state: succeeded

The production image layers the portfolio route over the immutable FlowSense
base image. Every non-companion route is forwarded to the original processor.
Do not replace or remove the original FlowSense behavior while changing the
portfolio companion.

API safeguards:

- Exact-origin CORS allowlist.
- 16 KB request-body cap with early streamed rejection.
- 8-message request cap.
- 600-character visitor-message cap.
- 3,600-character conversation cap with assistant-history compaction.
- 500 output-token cap.
- 24-second model timeout.
- 40-second proxy request timeout.
- 20 requests per client per 10 minutes.
- Distributed rate limits in Azure Table Storage.
- Salted SHA-256 client identifiers.
- Model requests use `store: false`.
- Unknown origins receive `403`.
- Oversized bodies receive `413`.

Primary implementation:

- `api/src/chatHandler.ts`
- `api/src/proxyServer.ts`
- `api/src/config.ts`
- `api/src/context.ts`
- `api/src/retrieval.ts`
- `api/src/prompt.ts`
- `api/src/rateLimit.ts`
- `api/src/clientIdentity.ts`
- `api/src/boundedBody.ts`
- `api/src/nodeBoundedBody.ts`
- `api/Dockerfile.flowsense-proxy`

### Vercel

- Project: `aadithva-portfolio`
- Plan: free Hobby
- Production alias: <https://aadithva-portfolio.vercel.app>
- GitHub `main` is connected for automatic production deployments.
- Production environment contains
  `PUBLIC_AADITH_CHAT_ENDPOINT`.
- `vercel.json` explicitly builds Astro and serves `dist`.
- `.vercelignore` excludes `api/`.

Keep `api/` excluded. Without `.vercelignore`, Vercel interprets the Azure API
source files as Vercel Functions and exceeds the Hobby plan's function limit.

The Vercel dashboard still reports the project framework preset as `Other`.
The committed `vercel.json` is authoritative, and production builds currently
succeed. Aligning the dashboard preset to Astro is optional cleanup.

## Audit results

### Verified clean

- `npm run api:test`: 14 tests passed.
- `npm run build`: 35 pages built.
- Context feed and embedded API context matched.
- Generated internal-link audit: zero missing internal targets.
- Repository credential-pattern scan: no committed key material found.
- Public-context scan: no private grounding terms found in chunk bodies.
- Live site returned `200`.
- Live context feed returned `200`.
- Live CORS preflight from Vercel returned `204`.
- Live companion request returned `200` with grounded sources.
- Mobile drawer and detail-route companion visibility behaved as designed.
- Current Vercel release and GitHub deployment check are successful.
- Azure revision `0000007` is healthy.

### No critical code defect found

A high-confidence review found one real configuration-drift risk, documented
below. A second reviewer concern about forwarded IP handling was investigated
and rejected using Azure's official platform behavior.

### Configuration drift: canonical origin vs checked-in defaults

The live deployment works because:

- Vercel explicitly provides `PUBLIC_AADITH_CHAT_ENDPOINT`, and
- the live Container App `ALLOWED_ORIGINS` includes
  `https://aadithva-portfolio.vercel.app`.

However, checked-in fallback defaults in these files still emphasize the old
`aadithva.com` host:

- `src/components/organisms/AadithCompanion.astro`
- `api/src/config.ts`
- `README.md`

If the Vercel environment variable or Azure runtime setting is lost, the
canonical Vercel host disables the frontend fallback or receives a CORS
rejection. Centralize the canonical host, browser fallback origins, and API
default origins so they cannot drift.

### Forwarded IP handling: keep the rightmost value

Do not change `api/src/clientIdentity.ts` to trust the leftmost
`X-Forwarded-For` value.

Azure Container Apps documents that it appends to an incoming header, only the
rightmost IP is provided by Azure Container Apps, and earlier values must be
validated to prevent spoofing. The current code intentionally uses the
rightmost value.

Official reference:
<https://learn.microsoft.com/azure/container-apps/ingress-overview#protocol-types>

### Cold-start behavior

The Container App has `minReplicas: 0`. During this audit, the first `/health`
request timed out after 20 seconds. The next request succeeded in about 0.9
seconds, and chat then completed normally.

This is a scale-to-zero cold start, not a persistent outage. Decide whether the
latency is acceptable or whether paying for `minReplicas: 1` is worthwhile.

Also note that `/health` is forwarded to the original FlowSense processor. It
does not independently prove that context loading, rate limiting, and the
Azure OpenAI call are ready.

### Pre-existing FlowSense SQL failure

The original FlowSense poller still logs repeated
`AggregateAuthenticationError` failures while requesting an Azure SQL token.
Managed identity reports that the IMDS endpoint is unavailable.

This predates the portfolio companion and was intentionally not changed because
the proxy must preserve the existing processor. Investigate it as a separate
FlowSense task or disable the poller if it is obsolete.

### Runtime secrets are inline Container App values

These production values currently use inline environment values instead of
Container App secret references:

- `AZURE_OPENAI_API_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_STORAGE_ACCOUNT_KEY`
- `WEBHOOK_SECRET`

They are not committed to Git, but they should be migrated to Container App
secrets after checking all FlowSense dependencies and rollback requirements.
Never print or copy their values into this repository.

### Custom domain is not configured

`aadithva.com` and `www.aadithva.com` currently have no resolving A or CNAME
records. The live canonical host is the Vercel URL.

If the custom domain is added later, update all of these together:

1. Vercel domain settings and DNS.
2. `src/data/siteConfig.ts`.
3. `astro.config.mjs`.
4. Vercel `PUBLIC_AADITH_CHAT_ENDPOINT`, if needed.
5. Azure `ALLOWED_ORIGINS`.
6. Companion fallback origins.
7. README and this handoff.

### Asset weight

- `public/`: about 51 MB
- `dist/`: about 59 MB
- Largest asset:
  `public/shots/owly-website/owly-website__home-desktop-full.png`
  at about 10 MB

Several full-page PNGs are between 1 MB and 4 MB. They do not all load on the
home page, but detail pages and deployment uploads are heavier than necessary.
Convert large screenshots to responsive WebP/AVIF variants, preserve readable
detail, and lazy-load below-the-fold media.

### Response headers

Vercel provides HSTS. The audited home response did not include an explicit
Content Security Policy, `X-Content-Type-Options`, `Referrer-Policy`, or
`Permissions-Policy`.

Add low-risk headers first. Treat CSP as a separate tested task because the
site currently uses inline Astro scripts and third-party Google/Adobe fonts.

### Expected non-blocking warnings

- Vite reports ignored Framer Motion `"use client"` directives during build.
  The production bundle still completes.
- Vercel deployment history contains one failed initial release from before
  `api/` was added to `.vercelignore`.

## Pending and blocked work

### Blocked

`ms-connect-review`: richer Microsoft Connect/performance evidence.

WorkIQ and organizational policy restricted Connect, performance-review,
reflection, impact, priority, and growth documents. Do not bypass the policy or
attempt to retrieve the same restricted content through another tool. Continue
using approved public evidence unless the user supplies explicitly publishable
material.

### No other active implementation task

The portfolio, companion, Azure deployment, GitHub integration, and Vercel
hosting are operational. New work should begin from the priorities below rather
than reopening completed tasks without evidence of a regression.

## Recommended next work

### Priority 1: production safety and reliability

1. Migrate the four inline Container App credentials to secret references.
   Preserve FlowSense rollback and verify `/health`, protected `/process`, and
   `/api/aadith-chat` afterward.
2. Fix or intentionally disable the pre-existing FlowSense Azure SQL poller.
   Confirm whether the Container App should have a managed identity and the
   required SQL role.
3. Centralize first-party origin configuration so the canonical host, frontend
   fallback, API defaults, Vercel environment, and Azure CORS list cannot drift.
4. Add companion-specific readiness monitoring. Keep it cheap: verify
   configuration, embedded context, and rate-limit storage without making a
   model call on every health probe.
5. Decide whether to keep scale-to-zero or set `minReplicas: 1`.

### Priority 2: delivery automation

1. Add GitHub Actions for:
   - `npm run api:test`
   - `npm run build`
   - `git diff --check`
   - context-sync comparison
   - design-system regeneration drift
   - generated internal-link checks
2. Add handler-level tests for:
   - Vercel-origin CORS,
   - unknown-origin rejection,
   - preflight behavior,
   - model timeout/failure,
   - context-load failure,
   - rate-limit storage failure.
3. Make backend image versioning and rollback a documented script rather than
   a manual sequence.

### Priority 3: performance and discoverability

1. Optimize the large screenshot library with responsive WebP/AVIF outputs.
2. Add and test conservative security headers.
3. Add a social preview image and verify Open Graph/Twitter previews.
4. Configure `aadithva.com` in Vercel when DNS access is available.
5. Run Lighthouse on representative home, Work, Lab, and mobile routes after
   image optimization.

### Priority 4: content quality

1. Continue enriching Microsoft case studies only with publishable evidence.
2. Review all dates, roles, and claims whenever portfolio data changes.
3. Regenerate and redeploy companion context after content changes.
4. Add new grounding only as curated public-safe chunks, never as raw private
   source material.

## Safe operating runbook

### Local verification

```bash
npm install
npm install --prefix api
npm run api:test
npm run build
cmp dist/aadith-context.json api/context/aadith-context.json
git diff --check
```

After changing components or routes:

```bash
python3 design-system/ai/codebase-index.py
python3 design-system/ai/component-metadata.py
python3 design-system/ai/adoption-report.py
```

### Frontend deployment

Push a verified commit to `main`. Vercel deploys automatically.

Check:

```bash
vercel ls aadithva-portfolio
gh api repos/aadithva/portfolio/commits/main/status
curl -I https://aadithva-portfolio.vercel.app/
```

If the production origin changes, update Azure `ALLOWED_ORIGINS` before
expecting browser chat requests to work.

### Context and backend deployment

When public portfolio context changes:

```bash
npm run api:sync-context
npm run api:test
```

Build a new immutable image tag:

```bash
cd api
az acr build \
  --registry crflowsense \
  --image flowsense-processor:aadith-companion-luna-vNEXT \
  --file Dockerfile.flowsense-proxy \
  .
cd ..
```

Deploy it:

```bash
az containerapp update \
  --resource-group rg-flowsense-prod \
  --name ca-flowsense-processor \
  --image crflowsense.azurecr.io/flowsense-processor:aadith-companion-luna-vNEXT
```

Then verify the latest ready revision, original FlowSense routes, CORS, live
chat, rate limiting, and oversized-body rejection.

Rollback target:

```text
crflowsense.azurecr.io/flowsense-processor:aadith-companion-luna-v6
```

### CORS update

Preserve every intentional existing origin when updating the list:

```bash
az containerapp update \
  --resource-group rg-flowsense-prod \
  --name ca-flowsense-processor \
  --set-env-vars 'ALLOWED_ORIGINS=<comma-separated exact origins>'
```

Never use a wildcard for the chat API.

## Non-negotiable guardrails

- Do not commit credentials, tokens, connection strings, or private grounding.
- Do not expose Azure credentials to browser code.
- Do not bypass Microsoft organizational content restrictions.
- Do not publish private Connect, performance, colleague, customer, health,
  relationship, family, financial, compensation, or manager information.
- Do not replace the original FlowSense processor behavior.
- Do not trust leftmost forwarded IP values on Azure Container Apps without a
  new platform-specific trust model.
- Do not remove `api/` from `.vercelignore`.
- Do not change the production origin without updating Vercel and Azure CORS
  together.
- Do not deploy new backend context without running `api:sync-context`.
