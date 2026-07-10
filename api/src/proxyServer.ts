import { spawn, type ChildProcess } from "node:child_process";
import http, {
  type IncomingHttpHeaders,
  type IncomingMessage,
  type ServerResponse,
} from "node:http";
import { handleChatRequest } from "./chatHandler.js";
import { clientIdFromForwardedFor } from "./clientIdentity.js";
import { readBoundedNodeBody } from "./nodeBoundedBody.js";
import { MAX_BODY_BYTES } from "./validation.js";

const listenPort = Number(process.env.PORT ?? 3003);
const originalPort = Number(process.env.ORIGINAL_PROCESSOR_PORT ?? 3002);
const originalRoot = process.env.ORIGINAL_PROCESSOR_ROOT ?? "/app";
const chatPath = process.env.PORTFOLIO_CHAT_PATH ?? "/api/aadith-chat";
const skipOriginal = process.env.SKIP_ORIGINAL_PROCESSOR === "true";

let originalProcess: ChildProcess | undefined;
let shuttingDown = false;

const headerValue = (
  headers: IncomingHttpHeaders,
  name: string
): string | undefined => {
  const value = headers[name];
  return Array.isArray(value) ? value[0] : value;
};

const clientIdFrom = (request: IncomingMessage): string =>
  clientIdFromForwardedFor(
    headerValue(request.headers, "x-forwarded-for"),
    request.socket.remoteAddress
  );

const writeJson = (
  response: ServerResponse,
  status: number,
  body: object | undefined,
  headers: Record<string, string>
) => {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  response.end(body ? JSON.stringify(body) : undefined);
};

const proxyToOriginal = (
  request: IncomingMessage,
  response: ServerResponse
) => {
  const headers = { ...request.headers };
  headers.host = `127.0.0.1:${originalPort}`;

  const upstream = http.request(
    {
      hostname: "127.0.0.1",
      port: originalPort,
      method: request.method,
      path: request.url,
      headers,
    },
    (upstreamResponse) => {
      response.writeHead(
        upstreamResponse.statusCode ?? 502,
        upstreamResponse.headers
      );
      upstreamResponse.pipe(response);
    }
  );

  upstream.on("error", (error) => {
    console.error("FlowSense upstream request failed", error.name);
    if (!response.headersSent) {
      writeJson(response, 502, { error: "The processor is unavailable." }, {});
    } else {
      response.destroy(error);
    }
  });

  request.pipe(upstream);
};

const server = http.createServer(async (request, response) => {
  const url = new URL(request.url ?? "/", "http://localhost");
  if (url.pathname !== chatPath) {
    proxyToOriginal(request, response);
    return;
  }

  try {
    const body =
      request.method === "POST"
        ? await readBoundedNodeBody(
            request,
            headerValue(request.headers, "content-length"),
            MAX_BODY_BYTES
          )
        : { text: "", exceeded: false };
    if (body.exceeded) response.shouldKeepAlive = false;

    const result = await handleChatRequest(
      {
        method: request.method ?? "GET",
        origin: headerValue(request.headers, "origin") ?? null,
        contentType: headerValue(request.headers, "content-type") ?? "",
        clientId: clientIdFrom(request),
        bodyText: body.exceeded
          ? "x".repeat(MAX_BODY_BYTES + 1)
          : body.text,
      },
      (message, error) => {
        console.error(
          message,
          error instanceof Error ? error.name : "UnknownError"
        );
      }
    );
    writeJson(response, result.status, result.body, result.headers);
  } catch (error) {
    console.error(
      "Portfolio companion transport failed",
      error instanceof Error ? error.name : "UnknownError"
    );
    writeJson(
      response,
      500,
      { error: "The companion request could not be processed." },
      {}
    );
  }
});

server.requestTimeout = 40_000;
server.headersTimeout = 45_000;

if (!skipOriginal) {
  originalProcess = spawn(
    "npm",
    ["start", "--workspace=@interactive-flow/processor"],
    {
      cwd: originalRoot,
      env: {
        ...process.env,
        PORT: String(originalPort),
      },
      stdio: "inherit",
    }
  );

  originalProcess.once("exit", (code, signal) => {
    if (shuttingDown) return;
    console.error(
      `FlowSense processor exited unexpectedly (${signal ?? code ?? "unknown"})`
    );
    server.close(() => process.exit(code ?? 1));
  });
}

server.listen(listenPort, () => {
  console.log(
    `FlowSense proxy listening on ${listenPort}; companion route ${chatPath}`
  );
});

const shutdown = (signal: NodeJS.Signals) => {
  if (shuttingDown) return;
  shuttingDown = true;
  server.close(() => process.exit(0));
  originalProcess?.kill(signal);
  setTimeout(() => process.exit(1), 8_000).unref();
};

process.once("SIGTERM", () => shutdown("SIGTERM"));
process.once("SIGINT", () => shutdown("SIGINT"));
