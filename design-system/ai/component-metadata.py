#!/usr/bin/env python3
"""Generate AI-ready component metadata (the HOW/WHY layer) for the Astro design system.

Run after codebase-index.py:
    python3 design-system/ai/component-metadata.py

Structural fields (tier, props, dependencies, usedBy) are derived from the source and
index.json so they never drift; the curated What/Why/when-to-use prose lives in CONTENT.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Dict, List

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
SRC_ROOT = REPO_ROOT / "src"
AI_ROOT = REPO_ROOT / "design-system" / "ai"
META_ROOT = AI_ROOT / "metadata"
INDEX_PATH = AI_ROOT / "index.json"

# Curated reasoning per component. Keyed by component name (file stem).
CONTENT: Dict[str, dict] = {
    "BaseLayout": {
        "summary": "App shell: document head, mono typography, header/footer, and global client behaviour.",
        "what": "Wraps every page with metadata, IBM Plex Mono, the base and editorial theme stylesheets, GridBackdrop, Header/Footer, and the small observer used for route-line drawing.",
        "why": "Centralises page chrome and the restrained vanilla-JS behaviour so individual pages only describe content.",
        "whenToUse": ["Wrap any new page.", "Set per-page <title> and meta description.", "Use bare=true for gated/standalone screens that should hide nav."],
        "whenNotToUse": ["Do not import inside another component — it is a top-level layout.", "Do not re-implement route/reveal observers in a page; they already live here."],
        "a11yNotes": ["Includes a skip link.", "Respects prefers-reduced-motion and keeps content visible without JavaScript."],
    },
    "BrandLockup": {
        "summary": "Aadith's reusable nested-frame symbol and mono wordmark.",
        "what": "Renders the original open-frame inspection mark, the uppercase AADITH wordmark in IBM Plex Mono, or both through symbol/wordmark/lockup variants.",
        "why": "Creates a personal identity that reflects layered inspection and avoids employer-like four-square marks or a generic initials monogram.",
        "whenToUse": ["Use the lockup in Header and Footer identity areas.", "Use wordmark-only for the oversized clipped footer signature.", "Use symbol-only for future compact branded controls."],
        "whenNotToUse": ["Do not recreate the nested-frame SVG inline.", "Do not pair it with unrelated display fonts or multiple accent colours."],
        "a11yNotes": ["The symbol is decorative; surrounding links or visible wordmark provide the accessible name.", "The footer display wordmark is hidden from assistive technology as repeated decoration."],
    },
    "Line": {
        "summary": "Tokenised 1px editorial divider.",
        "what": "Renders a presentational full-width rule; the current mono editorial theme keeps it static and immediately visible.",
        "why": "Provides one consistent separator across compact publishing-style sections.",
        "whenToUse": ["Separate major content sections.", "Introduce stats or nav blocks with a subtle reveal."],
        "whenNotToUse": ["Do not use as a border inside dense controls.", "Do not animate it manually — the observer handles it."],
        "a11yNotes": ["Decorative; role=presentation, no semantics.", "Static when reduced motion is requested."],
    },
    "GridBackdrop": {
        "summary": "Fixed large-cell grid behind the entire portfolio.",
        "what": "Renders one decorative hook; editorial-mono.css draws an original 2041px CSS grid plane with broad 408×261 cells and very low-contrast rules.",
        "why": "Adds the missing research-lab background structure while keeping the page readable and avoiding a copied image asset.",
        "whenToUse": ["Render once inside BaseLayout behind all non-bare and bare page content."],
        "whenNotToUse": ["Do not place it inside individual sections.", "Do not add text or interactive content to the backdrop."],
        "a11yNotes": ["Hidden from assistive technology.", "Pointer events are disabled."],
    },
    "Reveal": {
        "summary": "Semantic wrapper retained for optional restrained entrance behaviour.",
        "what": "Outputs a configurable tag with class `reveal`; the mono editorial theme resolves it visible and static, while preserving the shared hook for future motion changes.",
        "why": "Keeps content wrappers consistent without tying critical content visibility to JavaScript.",
        "whenToUse": ["Reveal a block on scroll.", "Stagger a list by passing an increasing delay.", "Change the wrapper element with `as` (e.g. h1, section)."],
        "whenNotToUse": ["Do not nest Reveal inside Reveal.", "Do not use for always-visible critical content that must not depend on JS."],
        "a11yNotes": ["Content is in the DOM regardless of JS; only opacity/transform animate.", "Reduced motion resolves it visible immediately."],
    },
    "SectionLabel": {
        "summary": "Small uppercase eyebrow label for section headings.",
        "what": "Renders slotted text with the `.section-label` token style (uppercase, tracked, muted).",
        "why": "Consistent section eyebrows ('Selected Work', 'Timeline') without re-declaring type styles.",
        "whenToUse": ["Label a section above a heading or grid.", "Tag editorial groupings."],
        "whenNotToUse": ["Do not use as a primary heading (not semantic h-level).", "Do not use for body copy."],
        "a11yNotes": ["Plain paragraph; pair with a real heading for structure."],
    },
    "CaseStudySection": {
        "summary": "Data-driven renderer for case-study blocks: text, image-full, image-grid, stats, quote, and editorial frameworks.",
        "what": "Branches on `section.type` from project data to emit the matching layout; framework sections render a structured ordered model and missing images fall back to `.placeholder-image` blocks.",
        "why": "Turns `Project.sections` and `WorkItem.sections` data into consistent editorial sections so project pages never hand-code layouts.",
        "whenToUse": ["Render each section of a work project or nested work item.", "Add case-study content by editing data when a section type fits."],
        "whenNotToUse": ["Do not hand-write raw markup for supported section types.", "Do not invent a new type if text/image/stats/quote/framework already fits."],
        "a11yNotes": ["Uses semantic blockquote/cite for quotes and an ordered list for framework steps.", "Placeholder blocks carry the section title as visible text."],
    },
    "HoverRevealList": {
        "summary": "Numbered, hover-aware list of work projects linking to case studies.",
        "what": "Maps `projects` to numbered rows (index, title, category, year) each linking to /work/<slug>, with reveal stagger.",
        "why": "The shared 'selected work' / work-index list, so the homepage and Work page stay identical.",
        "whenToUse": ["List work projects on the home and Work pages.", "Show a compact, scannable index of case studies."],
        "whenNotToUse": ["Do not use for Lab projects — use LabCard grid.", "Do not duplicate the row markup elsewhere."],
        "a11yNotes": ["Each row is a single anchor with readable text order.", "Numbers are decorative context, not list semantics."],
    },
    "LabCard": {
        "summary": "Ranked editorial row for a shortlisted Lab project.",
        "what": "Shows rank, theme, status, tagline, proof-oriented metadata, and the best screenshot from lib/shots.getThumb; missing previews use a typed orange empty state.",
        "why": "Makes the five-project Lab shortlist scannable without flattening each experiment into a generic card.",
        "whenToUse": ["Render one of the five showcase Lab projects.", "Preview a project with its rank, theme, and first screenshot."],
        "whenNotToUse": ["Do not use for work case studies (use HoverRevealList).", "Do not embed full screenshot galleries here — that is the detail page."],
        "a11yNotes": ["Thumbnails are lazy-loaded with descriptive alt text.", "Status conveyed by badge text, not colour alone."],
    },
    "FeaturedWork": {
        "summary": "Homepage 'Selected Work' organism: section label plus the featured project list.",
        "what": "Renders a SectionLabel and HoverRevealList of featured projects with an 'All projects' link.",
        "why": "Composes the home work teaser from smaller parts so ordering/copy live in one place.",
        "whenToUse": ["Show featured work on the homepage."],
        "whenNotToUse": ["Do not reuse on the Work index — that page lists all projects directly."],
        "a11yNotes": ["Inherits list semantics from HoverRevealList."],
    },
    "Footer": {
        "summary": "Global footer with an interactive network diagram, identity, social links, and secondary nav.",
        "what": "Renders a linked working model where context branches into questions and evidence, converges in a prototype, moves through testing, and loops back as learning.",
        "why": "Keeps the original network-like visual character while making every relationship and destination meaningful.",
        "whenToUse": ["Rendered automatically by BaseLayout."],
        "whenNotToUse": ["Do not import directly into pages.", "Hidden on bare/gated layouts by design."],
        "a11yNotes": ["Uses contentinfo landmark via <footer>.", "Links have discernible text."],
    },
    "Header": {
        "summary": "Static mono editorial header with Aadith's custom brand lockup and wrapping primary navigation.",
        "what": "Renders the nested-frame BrandLockup and nav from data/navigation; links wrap directly on small screens instead of opening a menu overlay.",
        "why": "Single source for navigation across the site.",
        "whenToUse": ["Rendered automatically by BaseLayout."],
        "whenNotToUse": ["Do not import directly into pages.", "Do not hard-code nav links — edit data/navigation."],
        "a11yNotes": ["Uses banner and navigation landmarks.", "Active links expose aria-current=page."],
    },
    "Hero": {
        "summary": "Homepage hero: compact mono positioning and role line.",
        "what": "Renders Aadith's AI-product positioning with a technical eyebrow and role context, leaving the landing page intentionally free of project screenshots.",
        "why": "Sets the research-lab tone without prematurely privileging one Lab project.",
        "whenToUse": ["Top of the homepage only."],
        "whenNotToUse": ["Do not reuse as a generic page header — use the page-header pattern."],
        "a11yNotes": ["Headline is a real h1.", "Motion is opacity/transform only."],
    },
    "DottedIndiaMap": {
        "summary": "Accurate dotted India map with the Kashmir-to-Kanyakumari cycling route.",
        "what": "Uses the verified India silhouette as an SVG pattern-filled dot field, then layers the simplified animated route, endpoints, and labels.",
        "why": "Keeps the Adventures map geographically grounded while matching the portfolio's technical diagram language.",
        "whenToUse": ["Render the Ride for Unity route on the Adventures page."],
        "whenNotToUse": ["Do not use as a turn-by-turn route or claim GPS accuracy.", "Do not duplicate the SVG inline in a page."],
        "a11yNotes": ["Includes a descriptive title and description.", "Start and finish remain visible as text, not colour alone."],
    },
    "ProfileSignals": {
        "summary": "Homepage proof section connecting enterprise AI, founder work, and design-to-code practice.",
        "what": "Renders an editorial statement and three linked evidence areas between the homepage hero and featured work.",
        "why": "Gives hiring managers and founder/investor readers a fast, credible explanation of Aadith's differentiated range before they enter a case study.",
        "whenToUse": ["Show the homepage positioning summary below Hero."],
        "whenNotToUse": ["Do not reuse as a generic feature grid.", "Do not duplicate its claims on the Work index."],
        "a11yNotes": ["Uses a labelled section with real h2/h3 hierarchy.", "Every signal includes a descriptive text link."],
    },
    "ProjectHero": {
        "summary": "Case-study hero: title, Role/Year/Client/Category meta, and hero image.",
        "what": "Renders the project title, description, meta grid, optional confidentiality note, and a hero image only when the configured public asset exists.",
        "why": "Consistent opening for every work case study.",
        "whenToUse": ["Top of a /work/<slug> case study."],
        "whenNotToUse": ["Do not use for Lab detail pages — those have their own header.", "Do not duplicate the meta grid by hand."],
        "a11yNotes": ["Title is the page h1.", "Meta labels are readable and ordered."],
    },
    "ProjectNav": {
        "summary": "Previous/next navigation between work case studies.",
        "what": "Renders prev/next links (or empty slots) under a divider at the foot of a case study.",
        "why": "Keeps users moving between projects without returning to the index.",
        "whenToUse": ["Foot of a /work/<slug> case study, fed by getAdjacentProjects."],
        "whenNotToUse": ["Do not use for Lab — the Lab detail page inlines its own equivalent nav."],
        "a11yNotes": ["Directional labels ('Previous'/'Next') precede titles.", "Empty side renders a spacer, not a dead link."],
    },
    "WorkGate": {
        "summary": "Reusable password gate for protected Microsoft work pages.",
        "what": "Wraps parent and nested work content with an optional environment-configured, session-scoped presentation gate, inline validation, and shared unlock state.",
        "why": "Keeps the protected-page behaviour consistent across the Microsoft overview and its focused child case studies without duplicating gate markup and script.",
        "whenToUse": ["Wrap work content whose Project or WorkItem is marked passwordProtected.", "Reuse the default storage key so one unlock opens the full Microsoft chapter."],
        "whenNotToUse": ["Do not treat this client-side gate as server-grade access control.", "Do not wrap public case studies."],
        "a11yNotes": ["Uses a real form, labelled password input placeholder, submit button, and inline error text.", "Protected content remains in the document but is hidden until unlock."],
    },
    "WorkItemIndex": {
        "summary": "Editorial child-project index for multi-part Work chapters.",
        "what": "Lists the focused WorkItems belonging to a parent Project with number, domain label, title, description, documentation status, and a nested route.",
        "why": "Lets Microsoft Copilot and DaoLens act as portfolio collections instead of forcing unrelated bodies of work into one long case study.",
        "whenToUse": ["Render below ProjectHero when getWorkItemsFor(project.slug) returns entries.", "Add a focused work item through src/data/work/<parent>/<item>/index.ts."],
        "whenNotToUse": ["Do not use on projects with no child case studies.", "Do not duplicate a child's full evidence inside the parent overview."],
        "a11yNotes": ["Every row is one descriptive anchor.", "Documentation status is written as text rather than conveyed by colour alone."],
    },
}

PROP_LINE_RE = re.compile(r"^\s*(?:/\*\*.*?\*/\s*)?([A-Za-z_][A-Za-z0-9_]*)(\??):\s*([^;]+);")


def find_source(name: str) -> Path | None:
    for sub in ("components/atoms", "components/molecules", "components/organisms", "layouts"):
        p = SRC_ROOT / sub / f"{name}.astro"
        if p.exists():
            return p
    return None


def parse_props(text: str) -> List[dict]:
    m = re.search(r"interface Props\s*\{([\s\S]*?)\}", text)
    if not m:
        return []
    body = m.group(1)
    props: List[dict] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("/") or line.startswith("*"):
            continue
        pm = PROP_LINE_RE.match(line)
        if pm:
            props.append({
                "name": pm.group(1),
                "type": pm.group(3).strip(),
                "required": pm.group(2) != "?",
            })
    return props


def main() -> None:
    index = json.loads(INDEX_PATH.read_text())
    comps = index["components"]
    pages = index["pages"]

    # name -> repo path (from index)
    name_to_path = {info["name"]: key for key, info in comps.items()}

    # reverse usedBy: for each component path, who imports it
    used_by: Dict[str, List[str]] = {key: [] for key in comps}
    for key, info in comps.items():
        for dep in info["localComponentDependencies"]:
            used_by.setdefault(dep, []).append(comps[key]["name"])
    for key, info in pages.items():
        for dep in info["importedComponents"]:
            used_by.setdefault(dep, []).append(f"route {info['route']}")

    # wipe stale metadata
    META_ROOT.mkdir(parents=True, exist_ok=True)
    for old in META_ROOT.glob("*.json"):
        old.unlink()

    today = date.today().isoformat()
    written = 0
    for name, content in CONTENT.items():
        path = name_to_path.get(name) or (find_source(name) and Path(find_source(name)).relative_to(REPO_ROOT).as_posix())
        if not path:
            print(f"  skip {name}: source not found")
            continue
        src = find_source(name)
        props = parse_props(src.read_text()) if src else []
        info = comps.get(path, {})
        dep_names = [Path(d).stem for d in info.get("localComponentDependencies", [])]
        data_deps = [Path(d).stem for d in info.get("localDataDependencies", [])]
        meta = {
            "name": name,
            "path": path,
            "tier": info.get("tier", "component"),
            "summary": content["summary"],
            "what": content["what"],
            "why": content["why"],
            "whenToUse": content["whenToUse"],
            "whenNotToUse": content["whenNotToUse"],
            "propsOrInputs": props,
            "componentDependencies": sorted(set(dep_names)),
            "dataDependencies": sorted(set(data_deps)),
            "usedBy": sorted(set(used_by.get(path, []))),
            "a11yNotes": content["a11yNotes"],
            "version": "0.3.0",
            "lastUpdated": today,
            "source": "Generated from Astro source + design-system/ai/index.json by component-metadata.py.",
        }
        (META_ROOT / f"{name}.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        written += 1

    print(f"Wrote {written} component metadata files to {META_ROOT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
