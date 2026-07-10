import { isIP } from "node:net";

const normalizeAddress = (value: string): string => {
  const candidate = value.trim().replace(/^"|"$/g, "");
  if (isIP(candidate)) return candidate;

  const bracketed = candidate.match(/^\[([^\]]+)\](?::\d+)?$/);
  if (bracketed?.[1] && isIP(bracketed[1])) return bracketed[1];

  const ipv4WithPort = candidate.match(/^(\d{1,3}(?:\.\d{1,3}){3}):\d+$/);
  if (ipv4WithPort?.[1] && isIP(ipv4WithPort[1])) return ipv4WithPort[1];

  return candidate.slice(0, 128);
};

export function clientIdFromForwardedFor(
  forwardedFor: string | undefined | null,
  fallback = "unknown"
): string {
  const chain = forwardedFor
    ?.split(",")
    .map((value) => value.trim())
    .filter(Boolean);

  // Azure supplies only the rightmost value; earlier hops may be client-spoofed.
  return normalizeAddress(chain?.at(-1) ?? fallback);
}
