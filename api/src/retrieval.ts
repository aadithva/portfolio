import type { ChatMessage, ContextChunk } from "./contracts.js";

const STOP_WORDS = new Set([
  "a",
  "about",
  "an",
  "and",
  "are",
  "as",
  "at",
  "be",
  "can",
  "do",
  "does",
  "for",
  "from",
  "he",
  "his",
  "how",
  "i",
  "in",
  "is",
  "it",
  "me",
  "of",
  "on",
  "or",
  "tell",
  "that",
  "the",
  "this",
  "to",
  "what",
  "which",
  "who",
  "why",
  "with",
]);

const normalize = (value: string): string =>
  value
    .toLocaleLowerCase("en")
    .normalize("NFKD")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();

const tokens = (value: string): string[] =>
  [...new Set(normalize(value).split(/\s+/))]
    .filter((token) => token.length > 1 && !STOP_WORDS.has(token));

const countMatches = (haystack: string, terms: string[], weight: number): number =>
  terms.reduce(
    (score, term) => score + (haystack.includes(term) ? weight : 0),
    0
  );

export function retrieveContext(
  messages: ChatMessage[],
  chunks: ContextChunk[],
  limit = 5
): ContextChunk[] {
  const recent = messages
    .slice(-4)
    .map((message) => message.content)
    .join(" ");
  const query = normalize(recent);
  const queryTokens = tokens(recent);

  const ranked = chunks
    .map((chunk, index) => {
      const title = normalize(chunk.title);
      const tags = normalize([chunk.category, ...chunk.tags].join(" "));
      const body = normalize(chunk.body);
      let score = 0;

      if (query.includes(title) && title.length > 2) score += 18;
      score += countMatches(title, queryTokens, 7);
      score += countMatches(tags, queryTokens, 5);
      score += countMatches(body, queryTokens, 1);

      if (chunk.id === "profile-overview") score += 0.25;

      return { chunk, index, score };
    })
    .sort((a, b) => b.score - a.score || a.index - b.index);

  const matched = ranked.filter((item) => item.score > 0.25).slice(0, limit);
  if (matched.length > 0) return matched.map((item) => item.chunk);

  const fallbacks = ["profile-overview", "working-style"];
  return fallbacks
    .map((id) => chunks.find((chunk) => chunk.id === id))
    .filter((chunk): chunk is ContextChunk => Boolean(chunk))
    .slice(0, limit);
}
