import type { ChatResponse, ContextSource } from "./contracts.js";
import { getConfig } from "./config.js";
import { loadContext } from "./context.js";
import { createOpenAIClient } from "./openai.js";
import { buildInstructions } from "./prompt.js";
import { checkRateLimit } from "./rateLimit.js";
import { retrieveContext } from "./retrieval.js";
import {
  MAX_BODY_BYTES,
  RequestError,
  validateChatRequest,
} from "./validation.js";

export interface ChatHandlerRequest {
  method: string;
  origin: string | null;
  contentType: string;
  clientId: string;
  bodyText: string;
}

export interface ChatHandlerResponse {
  status: number;
  body?: object;
  headers: Record<string, string>;
}

type ErrorLogger = (message: string, error: unknown) => void;

const corsHeaders = (
  origin: string | null,
  allowedOrigins: Set<string>
): Record<string, string> => {
  if (!origin || !allowedOrigins.has(origin)) {
    return { Vary: "Origin" };
  }

  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "600",
    Vary: "Origin",
  };
};

export async function handleChatRequest(
  request: ChatHandlerRequest,
  logError: ErrorLogger = () => undefined
): Promise<ChatHandlerResponse> {
  let config;
  try {
    config = getConfig();
  } catch (error) {
    logError("Portfolio companion configuration failed", error);
    return {
      status: 503,
      body: { error: "The companion is not configured." },
      headers: { Vary: "Origin" },
    };
  }

  const cors = corsHeaders(request.origin, config.allowedOrigins);

  if (request.method === "OPTIONS") {
    if (request.origin && !config.allowedOrigins.has(request.origin)) {
      return {
        status: 403,
        body: { error: "Origin is not allowed." },
        headers: cors,
      };
    }
    return { status: 204, headers: cors };
  }

  if (request.method !== "POST") {
    return {
      status: 405,
      body: { error: "Method is not allowed." },
      headers: { ...cors, Allow: "POST, OPTIONS" },
    };
  }

  if (request.origin && !config.allowedOrigins.has(request.origin)) {
    return {
      status: 403,
      body: { error: "Origin is not allowed." },
      headers: cors,
    };
  }

  if (!request.contentType.toLowerCase().includes("application/json")) {
    return {
      status: 415,
      body: { error: "Content-Type must be application/json." },
      headers: cors,
    };
  }

  let rateLimit;
  try {
    rateLimit = await checkRateLimit(request.clientId);
  } catch (error) {
    logError("Portfolio companion rate limiting failed", error);
    return {
      status: 503,
      body: { error: "The companion's request limit is unavailable." },
      headers: cors,
    };
  }

  if (!rateLimit.allowed) {
    return {
      status: 429,
      body: { error: "Too many questions. Please try again shortly." },
      headers: {
        ...cors,
        "Retry-After": String(rateLimit.retryAfterSeconds),
      },
    };
  }

  try {
    if (Buffer.byteLength(request.bodyText, "utf8") > MAX_BODY_BYTES) {
      return {
        status: 413,
        body: { error: "Request body is too large." },
        headers: cors,
      };
    }

    let raw: unknown;
    try {
      raw = JSON.parse(request.bodyText);
    } catch {
      throw new RequestError("Request body must be valid JSON.", 400);
    }

    const { messages } = validateChatRequest(raw);
    const contextDocument = await loadContext(config.contextUrl);
    const selected = retrieveContext(messages, contextDocument.chunks);
    const openai = await createOpenAIClient(config);

    const response = await openai.responses.create(
      {
        model: config.openAIModel,
        instructions: buildInstructions(contextDocument.boundary, selected),
        input: messages,
        max_output_tokens: 500,
        store: false,
      },
      { signal: AbortSignal.timeout(24_000) }
    );

    const answer = response.output_text?.trim();
    if (!answer) {
      throw new Error("Model returned no text");
    }

    const sources: ContextSource[] = selected.slice(0, 3).map(
      ({ id, title, path, category }) => ({ id, title, path, category })
    );
    const payload: ChatResponse = { answer, sources };
    return { status: 200, body: payload, headers: cors };
  } catch (error) {
    if (error instanceof RequestError) {
      return {
        status: error.status,
        body: { error: error.message },
        headers: cors,
      };
    }

    logError("Portfolio companion request failed", error);
    return {
      status: 502,
      body: {
        error: "The companion could not answer just now. Please try again.",
      },
      headers: cors,
    };
  }
}
