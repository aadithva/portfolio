import {
  app,
  type HttpRequest,
  type HttpResponseInit,
  type InvocationContext,
} from "@azure/functions";
import { readBoundedBody } from "../boundedBody.js";
import { handleChatRequest } from "../chatHandler.js";
import { clientIdFromForwardedFor } from "../clientIdentity.js";
import { MAX_BODY_BYTES } from "../validation.js";

const json = (
  status: number,
  body: object,
  headers: Record<string, string> = {}
): HttpResponseInit => ({
  status,
  jsonBody: body,
  headers: {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  },
});

const clientIdFrom = (request: HttpRequest): string =>
  clientIdFromForwardedFor(request.headers.get("x-forwarded-for"));

async function chat(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  let bodyText = "";
  if (request.method !== "OPTIONS") {
    try {
      const body = await readBoundedBody(
        request.body,
        request.headers.get("content-length"),
        MAX_BODY_BYTES
      );
      bodyText = body.exceeded ? "x".repeat(MAX_BODY_BYTES + 1) : body.text;
    } catch (error) {
      context.error(
        "Portfolio companion request body failed",
        error instanceof Error ? error.name : "UnknownError"
      );
      return json(400, { error: "Request body could not be read." });
    }
  }

  const result = await handleChatRequest(
    {
      method: request.method,
      origin: request.headers.get("origin"),
      contentType: request.headers.get("content-type") ?? "",
      clientId: clientIdFrom(request),
      bodyText,
    },
    (message, error) => {
      context.error(
        message,
        error instanceof Error ? error.name : "UnknownError"
      );
    }
  );

  if (result.status === 204) {
    return { status: 204, headers: result.headers };
  }
  return json(result.status, result.body ?? {}, result.headers);
}

app.http("aadithCompanionChat", {
  methods: ["POST", "OPTIONS"],
  authLevel: "anonymous",
  route: "chat",
  handler: chat,
});
