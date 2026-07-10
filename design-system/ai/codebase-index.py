#!/usr/bin/env python3
"""Generate a compact AI-ready codebase index for the portfolio design system.

Run from the repository root:
    python3 design-system/ai/codebase-index.py

The index intentionally uses full repository-relative paths as object keys to avoid
filename-stem collisions (for example, multiple [slug].astro files in different folders).

Targets the Astro source tree: atomic components live under src/components/{atoms,
molecules,organisms}, layouts under src/layouts, routes under src/pages, and shared
data/helpers under src/data and src/lib.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
SRC_ROOT = REPO_ROOT / "src"
COMPONENTS_ROOT = SRC_ROOT / "components"
LAYOUTS_ROOT = SRC_ROOT / "layouts"
PAGES_ROOT = SRC_ROOT / "pages"
DATA_ROOT = SRC_ROOT / "data"
LIB_ROOT = SRC_ROOT / "lib"
OUT_PATH = REPO_ROOT / "design-system" / "ai" / "index.json"

# Components/layouts/pages are .astro; data and helpers are .ts.
COMPONENT_EXTENSIONS = {".astro"}
SOURCE_EXTENSIONS = {".astro", ".ts", ".tsx", ".js", ".jsx"}
DATA_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".json"}

# Prefixes that count as a "component" dependency vs a "data" dependency.
COMPONENT_PREFIXES: Tuple[str, ...] = ("src/components/", "src/layouts/")
DATA_PREFIXES: Tuple[str, ...] = ("src/data/", "src/lib/")

IMPORT_RE = re.compile(
    r"import(?:\s+type)?[\s\S]*?from\s+[\"']([^\"']+)[\"']"
    r"|import\s*\(\s*[\"']([^\"']+)[\"']\s*\)"
)


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def files_with_ext(base: Path, exts: set) -> Iterable[Path]:
    if not base.exists():
        return []
    return sorted(p for p in base.rglob("*") if p.is_file() and p.suffix in exts)


def imports_from(text: str) -> List[str]:
    imports: List[str] = []
    for match in IMPORT_RE.finditer(text):
        spec = match.group(1) or match.group(2)
        if spec:
            imports.append(spec)
    return sorted(set(imports))


def resolve_import(spec: str, from_file: Path) -> Optional[str]:
    if spec.startswith("@/"):
        candidate = SRC_ROOT / spec[2:]
    elif spec.startswith("."):
        candidate = (from_file.parent / spec).resolve()
    else:
        return None

    candidates: List[Path] = []
    if candidate.suffix:
        candidates.append(candidate)
    else:
        for ext in SOURCE_EXTENSIONS:
            candidates.append(candidate.with_suffix(ext))
        for ext in SOURCE_EXTENSIONS:
            candidates.append(candidate / f"index{ext}")
        candidates.append(candidate / "index.json")

    for item in candidates:
        if item.exists() and item.is_file():
            return rel(item)
    return None


def local_deps(imports: List[str], from_file: Path, prefixes: Tuple[str, ...]) -> List[str]:
    deps = []
    for spec in imports:
        resolved = resolve_import(spec, from_file)
        if resolved and resolved.startswith(prefixes):
            deps.append(resolved)
    return sorted(set(deps))


def component_tier(path: Path) -> str:
    """Tier is the atomic-design folder under src/components; layouts are their own tier."""
    if LAYOUTS_ROOT in path.parents:
        return "layout"
    parts = path.relative_to(COMPONENTS_ROOT).parts
    folder = parts[0] if len(parts) > 1 else ""
    mapping = {
        "atoms": "atom",
        "molecules": "molecule",
        "organisms": "organism",
    }
    return mapping.get(folder, "component")


def route_from_page(path: Path) -> str:
    relative = path.relative_to(PAGES_ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "index":
        parts.pop()
    if not parts:
        return "/"
    return "/" + "/".join(parts)


def page_kind(path: Path) -> str:
    return "dynamic-page" if "[" in path.name else "page"


def compact_note(component_count: int, page_count: int) -> str:
    return (
        f"This index summarizes {component_count} components and {page_count} routes using full "
        "relative path keys, so an AI can retrieve structure and dependencies in a few thousand "
        "tokens instead of reading every source file."
    )


def main() -> None:
    components: Dict[str, dict] = {}
    pages: Dict[str, dict] = {}
    data_files: Dict[str, dict] = {}

    component_paths = list(files_with_ext(COMPONENTS_ROOT, COMPONENT_EXTENSIONS))
    component_paths += list(files_with_ext(LAYOUTS_ROOT, COMPONENT_EXTENSIONS))
    for path in sorted(component_paths):
        text = read(path)
        imports = imports_from(text)
        key = rel(path)
        components[key] = {
            "path": key,
            "tier": component_tier(path),
            "name": path.stem,
            "imports": imports,
            "localComponentDependencies": local_deps(imports, path, COMPONENT_PREFIXES),
            "localDataDependencies": local_deps(imports, path, DATA_PREFIXES),
        }

    for path in files_with_ext(PAGES_ROOT, COMPONENT_EXTENSIONS):
        text = read(path)
        imports = imports_from(text)
        key = rel(path)
        pages[key] = {
            "path": key,
            "kind": page_kind(path),
            "route": route_from_page(path),
            "name": path.stem,
            "imports": imports,
            "importedComponents": local_deps(imports, path, COMPONENT_PREFIXES),
            "importedData": local_deps(imports, path, DATA_PREFIXES),
        }

    for path in list(files_with_ext(DATA_ROOT, DATA_EXTENSIONS)) + list(files_with_ext(LIB_ROOT, DATA_EXTENSIONS)):
        text = read(path)
        key = rel(path)
        exports = sorted(set(re.findall(
            r"export\s+(?:const|function|type|interface)\s+([A-Za-z0-9_]+)", text
        )))
        data_files[key] = {"path": key, "exports": exports, "imports": imports_from(text)}

    index = {
        "version": "0.2.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generator": rel(SCRIPT_PATH),
        "framework": "astro",
        "uniqueKeyPolicy": "All maps are keyed by full repository-relative path; filename stems are never used as unique keys.",
        "tokenEfficiencyNote": compact_note(len(components), len(pages)),
        "stats": {
            "componentCount": len(components),
            "pageCount": len(pages),
            "pageRouteCount": sum(1 for item in pages.values() if item["kind"] in ("page", "dynamic-page")),
            "dataFileCount": len(data_files),
            "tierCounts": {
                tier: sum(1 for c in components.values() if c["tier"] == tier)
                for tier in sorted({c["tier"] for c in components.values()})
            },
            "duplicatePageFilenamesPreserved": sorted(
                name for name in {Path(k).name for k in pages}
                if sum(1 for key in pages if Path(key).name == name) > 1
            ),
            "approxJsonTokens": None,
        },
        "components": components,
        "pages": pages,
        "data": data_files,
    }

    raw = json.dumps(index, indent=2, sort_keys=True)
    approx_tokens = max(1, len(raw) // 4)
    index["stats"]["approxJsonTokens"] = approx_tokens
    OUT_PATH.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {rel(OUT_PATH)}")
    print(f"Components: {len(components)} (tiers: {index['stats']['tierCounts']})")
    print(f"Pages: {len(pages)} ({index['stats']['pageRouteCount']} routes)")
    dupes = index["stats"]["duplicatePageFilenamesPreserved"]
    print(f"Duplicate page filenames preserved: {', '.join(dupes) or 'none'}")
    print(f"Approx JSON tokens: {approx_tokens}")


if __name__ == "__main__":
    main()
