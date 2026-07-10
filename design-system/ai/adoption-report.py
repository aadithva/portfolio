#!/usr/bin/env python3
"""Regenerate the human-readable design-system docs from machine-readable data.

Run after the index and metadata generators:
    python3 design-system/ai/codebase-index.py
    python3 design-system/ai/component-metadata.py
    python3 design-system/ai/adoption-report.py

Writes:
  - design-system/component-inventory.md  (atomic inventory)
  - design-system/adoption-report.md      (utilization + risks)

Everything is derived from design-system/ai/index.json and design-system/ai/metadata/*,
so the docs never drift from the Astro source as long as the generators are re-run.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
AI_ROOT = REPO_ROOT / "design-system" / "ai"
INDEX_PATH = AI_ROOT / "index.json"
META_ROOT = AI_ROOT / "metadata"
INVENTORY_OUT = REPO_ROOT / "design-system" / "component-inventory.md"
ADOPTION_OUT = REPO_ROOT / "design-system" / "adoption-report.md"

TIER_ORDER = ["atom", "molecule", "organism", "layout", "component"]
TIER_HEADINGS = {
    "atom": "Atoms",
    "molecule": "Molecules",
    "organism": "Organisms",
    "layout": "Layouts",
    "component": "Other components",
}


def load_metadata() -> Dict[str, dict]:
    meta: Dict[str, dict] = {}
    if META_ROOT.exists():
        for f in sorted(META_ROOT.glob("*.json")):
            data = json.loads(f.read_text())
            meta[data["path"]] = data
    return meta


def reverse_used_by(index: dict) -> Dict[str, List[str]]:
    used_by: Dict[str, List[str]] = defaultdict(list)
    for key, info in index["components"].items():
        for dep in info["localComponentDependencies"]:
            used_by[dep].append(info["name"])
    for key, info in index["pages"].items():
        for dep in info["importedComponents"]:
            used_by[dep].append(f"route {info['route']}")
    return {k: sorted(set(v)) for k, v in used_by.items()}


def md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def build_inventory(index: dict, meta: Dict[str, dict], used_by: Dict[str, List[str]]) -> str:
    comps = index["components"]
    by_tier: Dict[str, List[str]] = defaultdict(list)
    for key, info in comps.items():
        by_tier[info["tier"]].append(key)

    lines: List[str] = []
    lines.append("# Component Inventory")
    lines.append("")
    lines.append("Atomic-design inventory for the Astro portfolio implementation.")
    lines.append(f"Generated from `{INDEX_PATH.relative_to(REPO_ROOT).as_posix()}` — do not edit by hand.")
    lines.append("")
    lines.append("## Tokens")
    lines.append("")
    lines.append("- **Source**: `design-system/tokens.css` / `design-system/tokens.json` (`--ds-*` custom properties).")
    lines.append("- **Color**: background `#fff`, foreground `#0a0a0a`, muted `#f7f6f3`, muted-fg `#787774`, border `#eaeaea`.")
    lines.append("- **Type**: IBM Plex Mono for the interface and Digibop exclusively for the AADITH wordmark.")
    lines.append("- **Layout**: `.container` max-width 1440px with responsive side padding (20 / 48 / 80px).")
    lines.append("- **Motion**: entrance reveals via the global IntersectionObserver (`.reveal`/`.line`/`.routemap` → `.is-visible`), with reduced-motion fallbacks.")
    lines.append("")

    for tier in TIER_ORDER:
        keys = sorted(by_tier.get(tier, []))
        if not keys:
            continue
        lines.append(f"## {TIER_HEADINGS[tier]}")
        lines.append("")
        lines.append("| Component | Path | Purpose | Dependencies | Used by |")
        lines.append("|---|---|---|---|---|")
        for key in keys:
            info = comps[key]
            name = info["name"]
            m = meta.get(key)
            purpose = md_escape(m["summary"]) if m else "—"
            deps = sorted(set(Path(d).stem for d in info["localComponentDependencies"]) |
                          set(Path(d).stem for d in info["localDataDependencies"]))
            deps_str = ", ".join(f"`{d}`" for d in deps) or "—"
            ub = used_by.get(key, [])
            ub_str = ", ".join(ub) or "_not imported_"
            lines.append(f"| `{name}` | `{key}` | {purpose} | {deps_str} | {md_escape(ub_str)} |")
        lines.append("")

    lines.append("## Routes")
    lines.append("")
    lines.append("| Route | Page file | Imported components |")
    lines.append("|---|---|---|")
    for key in sorted(index["pages"]):
        info = index["pages"][key]
        imported = ", ".join(f"`{Path(c).stem}`" for c in info["importedComponents"]) or "—"
        lines.append(f"| `{info['route']}` | `{key}` | {imported} |")
    lines.append("")
    return "\n".join(lines)


def build_adoption(index: dict, meta: Dict[str, dict], used_by: Dict[str, List[str]]) -> str:
    comps = index["components"]
    stats = index["stats"]
    total = len(comps)
    used = [k for k in comps if used_by.get(k)]
    unused = [k for k in comps if not used_by.get(k)]
    pct = round(100 * len(used) / total) if total else 0

    meta_names = sorted(Path(p).stem for p in meta)
    covered = sum(1 for k in comps if k in meta)

    lines: List[str] = []
    lines.append("# Design-System Adoption Report")
    lines.append("")
    lines.append(f"Generated from `{INDEX_PATH.relative_to(REPO_ROOT).as_posix()}` and "
                 f"`design-system/ai/metadata/` by `adoption-report.py`. Re-run after code changes.")
    lines.append("")
    lines.append("## Freshness")
    lines.append("")
    lines.append(f"- Index version: `{index.get('version')}` ({index.get('framework', 'n/a')})")
    lines.append(f"- Index generated at: `{index.get('generatedAt')}`")
    lines.append(f"- Metadata files: {len(meta_names)} ({', '.join(meta_names)})")
    lines.append("- Caveat: utilization is static import-based; dynamic or runtime-only references may need manual review.")
    lines.append("")
    lines.append("## Index stats")
    lines.append("")
    lines.append(f"- Components scanned: **{stats['componentCount']}**")
    lines.append(f"- Routes scanned: **{stats['pageRouteCount']}**")
    lines.append(f"- Data/helper files scanned: **{stats['dataFileCount']}**")
    lines.append(f"- Approx index token size: **{stats['approxJsonTokens']} tokens**")
    dupes = stats.get("duplicatePageFilenamesPreserved") or []
    lines.append(f"- Duplicate page filenames preserved by full-path keys: **{', '.join(dupes) or 'none'}**")
    lines.append("")
    lines.append("### Tier distribution")
    lines.append("")
    for tier, count in sorted(stats.get("tierCounts", {}).items()):
        lines.append(f"- {TIER_HEADINGS.get(tier, tier)}: **{count}**")
    lines.append("")
    lines.append("## Component utilization")
    lines.append("")
    lines.append(f"Static import utilization: **{len(used)} used / {total} total** ({pct}%).")
    lines.append("")
    lines.append("### Components with direct usage")
    lines.append("")
    for key in sorted(used):
        lines.append(f"- `{comps[key]['name']}` (`{key}`) — used by {', '.join(used_by[key])}.")
    lines.append("")
    lines.append("### Components not directly imported")
    lines.append("")
    if unused:
        for key in sorted(unused):
            note = " (top-level shell, rendered by Astro routing)" if comps[key]["tier"] == "layout" else ""
            lines.append(f"- `{comps[key]['name']}` (`{key}`){note}.")
    else:
        lines.append("- None — every component is imported somewhere.")
    lines.append("")
    lines.append("## Metadata coverage")
    lines.append("")
    lines.append(f"Components documented in `metadata/`: **{covered} / {total}**.")
    missing = sorted(comps[k]["name"] for k in comps if k not in meta)
    if missing:
        lines.append("")
        lines.append(f"Missing metadata: {', '.join(f'`{m}`' for m in missing)}.")
    lines.append("")
    lines.append("## Automated risk flags")
    lines.append("")
    flags: List[str] = []
    for key in sorted(unused):
        if comps[key]["tier"] != "layout":
            flags.append(f"Unused component `{comps[key]['name']}` — confirm it is intentional or remove it.")
    for key in sorted(comps):
        if key not in meta:
            flags.append(f"`{comps[key]['name']}` has no metadata entry — AI selection guidance is incomplete.")
    if not flags:
        flags.append("No structural risks detected: all components are used and documented.")
    for f in flags:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Adoption summary")
    lines.append("")
    lines.append(
        f"The Astro portfolio runs an organism-led system: a `BaseLayout` shell, a data-driven "
        f"`CaseStudySection`, the `HoverRevealList` work index, and the `LabCard` Lab grid are reusable "
        f"and consistently tokenized. {len(used)}/{total} components are imported and {covered}/{total} are "
        f"documented. The maintenance priority is to re-run the index/metadata/report generators on every "
        f"component change so AI assistants keep choosing existing high-craft patterns before inventing new UI."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    index = json.loads(INDEX_PATH.read_text())
    meta = load_metadata()
    used_by = reverse_used_by(index)

    INVENTORY_OUT.write_text(build_inventory(index, meta, used_by).rstrip() + "\n", encoding="utf-8")
    ADOPTION_OUT.write_text(build_adoption(index, meta, used_by).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {INVENTORY_OUT.relative_to(REPO_ROOT)}")
    print(f"Wrote {ADOPTION_OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
