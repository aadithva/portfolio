# Behance case-study content and image plan

The copy in `src/data/projects.ts` now follows the source material embedded in the Behance
boards. Image replacement is a separate pass.

## Reachify

### Verified story

- Four-month freelance project in 2023.
- AI-assisted LinkedIn personal-branding product, not a creator-brand marketplace.
- More than 100 outreach messages and 15–20 interviews.
- 30+ screens.
- Core areas: Create, Engagement, Analytics, and Dashboard.
- Two-day MVP sprint for onboarding and Create.
- Aadith also produced content that helped Reachify's LinkedIn page reach 2,000 followers.

### Image mapping

| Portfolio section | Behance module |
|---|---|
| Hero | `reachify/01` |
| Market and literature research | `reachify/02` |
| Interview method | `reachify/03` |
| Segmentation and persona | `reachify/04`, `reachify/05` |
| Information architecture | `reachify/07` |
| Design system | `reachify/08` |
| MVP constraint | `reachify/11` |
| Create flow | `reachify/12` |
| Mobile UI and early feedback | `reachify/13` |

## MetaMask AD

### Verified story

- Semester thesis, January–March 2023.
- ConsenSys problem statement for Team 45 at the Inter IIT Tech Meet.
- Aadith was the sole designer on a six-person team.
- Decentralized advertising DSP proposed as a MetaMask Snap.
- Advertiser dashboard, wallet-native payments, opt-in Ad World, and conceptual FOX token.
- Four-step ad publishing flow.
- Second place at the competition.
- Later presented in a ConsenSys community call with 1,000+ attendees.
- Not a commissioned or shipped MetaMask product.

### Image mapping

| Portfolio section | Behance module |
|---|---|
| Hero | `metamask/01` |
| System map and MetaMask rationale | `metamask/13` |
| Visual system and four-step flow | `metamask/15` |
| Motion walkthrough | `metamask/16` or `metamask/17` |
| Competition outcome | `metamask/18` |
| Team credit | `metamask/19` |
| Information architecture | `metamask/20` |
| Ad World onboarding | `metamask/21` |
| Final advertiser dashboard | `metamask/22` |

## Nomad

### Verified story

- Collaborative project with Aarya Kabara.
- Multi-city vacation planner, not a digital-nomad or remote-work product.
- Eight traveler interviews.
- Personas: Karan and Ashna.
- Competitors: TripIt, Wanderlog, and TripAdvisor.
- Core areas: Explore, Plan, Messages, and Profile.
- Group decision-making, itinerary editing, chat, and shared expenses.

### Image mapping

| Portfolio section | Behance module |
|---|---|
| Brief / alternate hero | `nomad/01` |
| Research findings | `nomad/03` |
| Competitive analysis | `nomad/05` |
| Personas | `nomad/11`, `nomad/12` |
| Feature ideation | `nomad/13` |
| User flow | `nomad/14` |
| Information architecture | `nomad/15` |
| Design system | `nomad/16` |
| Explore UI / preferred visual hero | `nomad/17` |
| Plan UI | `nomad/18` |
| Messages, budget, and profile | `nomad/19` |

## DaoLens at DAO Denver

### Verified story

- Client: DaoLens.
- Collaborative Behance project with Ans K James; no documented person-by-person role split.
- Two-week event sprint.
- Three-day DAO Denver event during ETHDenver 2023.
- Shifted the brand from sleek B2B/cyberpunk to a brighter, playful event expression.
- Eight named deliverable formats plus the booth itself.
- Included booth graphics, banners, merch, social posts, pamphlets, website work, a
  dartboard activation, and a paper fortune-teller game.

### Image mapping

| Portfolio section | Behance module |
|---|---|
| Hero | `dao-denver/07` |
| Brief | `dao-denver/02` |
| B2B-to-event identity shift | `dao-denver/04` |
| Stickers and illustration language | `dao-denver/06`, `dao-denver/13` |
| Banners and booth | `dao-denver/07`, `dao-denver/10` |
| Social posts | `dao-denver/08` |
| Paper game and copy | `dao-denver/11` |
| Website mockups | `dao-denver/12` |

## Sarthebari

### Verified story

- Co-created with Mohammed Nadil.
- Secondary research, stakeholder mapping, field observation, and interviews.
- Research covered a retail shop owner, cooperative employee, and craftsmen.
- Source estimates: 5,000+ workers, 280+ units, two cooperatives, 41 shopkeepers,
  roughly 30 agents, and products worth approximately ₹3.5 crore.
- Distinctive finding: Sarthebari cymbals and vessels were being re-aged, repackaged, and
  sold abroad under Tibetan, Chinese, or generic singing-bowl identities.
- ABMI identity, e-commerce concept, social strategy, and targeted ads.
- Health messaging is a brand claim from source material, not verified medical research.

### Image mapping

| Portfolio section | Behance module |
|---|---|
| Documentary hero | `sarthebari/06` |
| Brand-led alternate hero | `sarthebari/20` |
| Context and estimates | `sarthebari/03` |
| Craft process | `sarthebari/07` |
| Findings and identity loss | `sarthebari/09` |
| Interview voices | `sarthebari/10` |
| Logo exploration | `sarthebari/17` |
| Brand system | `sarthebari/18`, `sarthebari/19` |
| E-commerce | `sarthebari/22` |
| Social strategy | `sarthebari/23` |
| Targeted ads | `sarthebari/24` |

## Junkea

### Verified story

- IIT Guwahati Art & Aesthetics group project.
- Seven-plus credited collaborators; no individual role split.
- Process: Collection → Ideation → Manufacturing/Product.
- Salvaged material included old chair parts, bicycle rims and springs, rods, plywood,
  used cloth, and sponge.
- Black-and-orange identity.
- Exhibited at IIT Guwahati.
- The final furniture was documented in use at the Media Lab.
- Best treated as a collaboration entry rather than a flagship solo case study.

### Image mapping

| Portfolio section | Behance module |
|---|---|
| Hero | `junkea/01` |
| Found-material inspiration | crop from `junkea/02` |
| Materials and construction | `junkea/04` |
| Brand rationale and workshop | crops from `junkea/05` |
| Exhibition and mentor credit | `junkea/06` |
| Furniture in use | top of `junkea/07` |

## Image production rules

1. Download the creator-owned exports and store them locally; do not hotlink Behance CDN
   assets in production.
2. Use the prepared vision copies only for analysis:
   `/Users/aadith/.copilot/session-state/8131a7b4-2018-474d-8a22-d80cec3661b3/files/behance-vision/`
3. Vision copies use a maximum long edge of 1568 px.
4. Tall Behance boards are split into overlapping 1280 px tiles so embedded text remains
   readable.
5. Process no more than four images per vision request.
6. Re-export final portfolio assets from the best source files with page-specific crops,
   descriptive alt text, and responsive dimensions.
