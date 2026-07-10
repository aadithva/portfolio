import fs from "node:fs";
import path from "node:path";

const SHOTS_DIR = path.join(process.cwd(), "public", "shots");

export interface RouteShots {
  route: string;
  desktopFull?: string;
  desktopHero?: string;
  mobileFull?: string;
}

function fileFor(slug: string, name: string): string {
  return `/shots/${slug}/${name}`;
}

/** Read all screenshots for a project, grouped by route, in route order. */
export function getShots(slug: string): RouteShots[] {
  const dir = path.join(SHOTS_DIR, slug);
  let files: string[] = [];
  try {
    files = fs.readdirSync(dir).filter((f) => f.endsWith(".png"));
  } catch {
    return [];
  }
  const byRoute = new Map<string, RouteShots>();
  const order: string[] = [];
  for (const f of files.sort()) {
    const m = f.match(/^.+?__(.+)-(desktop-full|desktop-hero|mobile-full)\.png$/);
    if (!m) continue;
    const [, route, kind] = m;
    if (!byRoute.has(route)) {
      byRoute.set(route, { route });
      order.push(route);
    }
    const entry = byRoute.get(route)!;
    if (kind === "desktop-full") entry.desktopFull = fileFor(slug, f);
    else if (kind === "desktop-hero") entry.desktopHero = fileFor(slug, f);
    else if (kind === "mobile-full") entry.mobileFull = fileFor(slug, f);
  }
  return order.map((r) => byRoute.get(r)!);
}

/** Best single thumbnail for a project card, or null if none. */
export function getThumb(slug: string): string | null {
  const shots = getShots(slug);
  for (const s of shots) {
    if (s.desktopHero) return s.desktopHero;
    if (s.desktopFull) return s.desktopFull;
  }
  return null;
}

/** Human label for a route key. */
export function routeLabel(route: string): string {
  if (route === "home" || route === "") return "Home";
  return route
    .replace(/^\//, "")
    .split(/[-_/]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
