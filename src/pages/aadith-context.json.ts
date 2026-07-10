import { buildCompanionContext } from "@/data/companion";

export const prerender = true;

export function GET() {
  return new Response(JSON.stringify(buildCompanionContext()), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=300, s-maxage=3600",
    },
  });
}
