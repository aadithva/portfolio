import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import type { ContextChunk, ContextDocument } from "./contracts.js";

const CACHE_TTL_MS = 5 * 60 * 1000;

let cached:
  | {
      url: string;
      expiresAt: number;
      document: ContextDocument;
    }
  | undefined;

const isStringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === "string");

const isContextChunk = (value: unknown): value is ContextChunk => {
  if (!value || typeof value !== "object") return false;
  const chunk = value as Record<string, unknown>;
  return (
    typeof chunk.id === "string" &&
    typeof chunk.title === "string" &&
    typeof chunk.path === "string" &&
    chunk.path.startsWith("/") &&
    typeof chunk.category === "string" &&
    isStringArray(chunk.tags) &&
    typeof chunk.body === "string"
  );
};

const isContextDocument = (value: unknown): value is ContextDocument => {
  if (!value || typeof value !== "object") return false;
  const document = value as Record<string, unknown>;
  return (
    typeof document.version === "string" &&
    typeof document.owner === "string" &&
    typeof document.boundary === "string" &&
    Array.isArray(document.chunks) &&
    document.chunks.length > 0 &&
    document.chunks.every(isContextChunk)
  );
};

export async function loadContext(url: string): Promise<ContextDocument> {
  if (cached && cached.url === url && cached.expiresAt > Date.now()) {
    return cached.document;
  }

  let payload: unknown;
  if (url.startsWith("file:")) {
    payload = JSON.parse(await readFile(fileURLToPath(url), "utf8"));
  } else {
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(4_000),
    });

    if (!response.ok) {
      throw new Error(`Context feed returned ${response.status}`);
    }
    payload = await response.json();
  }

  if (!isContextDocument(payload)) {
    throw new Error("Context feed has an invalid shape");
  }

  cached = {
    url,
    expiresAt: Date.now() + CACHE_TTL_MS,
    document: payload,
  };

  return payload;
}

export function clearContextCache(): void {
  cached = undefined;
}
