import assert from "node:assert/strict";
import { Readable } from "node:stream";
import test from "node:test";
import { readBoundedBody } from "../src/boundedBody.js";
import { clientIdFromForwardedFor } from "../src/clientIdentity.js";
import type { ContextChunk } from "../src/contracts.js";
import { readBoundedNodeBody } from "../src/nodeBoundedBody.js";
import { getConfig } from "../src/config.js";
import { checkRateLimit, clearRateLimits } from "../src/rateLimit.js";
import { retrieveContext } from "../src/retrieval.js";
import { RequestError, validateChatRequest } from "../src/validation.js";

const chunks: ContextChunk[] = [
  {
    id: "profile-overview",
    title: "About Aadith",
    path: "/about",
    category: "Profile",
    tags: ["designer", "founder"],
    body: "Aadith is a product designer at Microsoft and co-founder of Owly.",
  },
  {
    id: "work-microsoft-copilot",
    title: "Microsoft Copilot",
    path: "/work/microsoft-copilot",
    category: "Work",
    tags: ["citations", "response ux", "trust"],
    body: "He works on citations, evidence, response structure, and evaluation.",
  },
  {
    id: "lab-flowsense",
    title: "FlowSense",
    path: "/lab/flowsense",
    category: "Lab",
    tags: ["figma", "design review"],
    body: "FlowSense reviews user flows and leaves structured evidence.",
  },
];

test("retrieval prioritizes matching project context", () => {
  const result = retrieveContext(
    [{ role: "user", content: "What does he do with citations at Microsoft?" }],
    chunks
  );

  assert.equal(result[0]?.id, "work-microsoft-copilot");
});

test("retrieval falls back to profile context", () => {
  const result = retrieveContext(
    [{ role: "user", content: "Tell me something useful" }],
    chunks
  );

  assert.equal(result[0]?.id, "profile-overview");
});

test("companion model override leaves the shared deployment untouched", () => {
  process.env.AZURE_OPENAI_ENDPOINT =
    "https://eastus.api.cognitive.microsoft.com/";
  process.env.AZURE_OPENAI_DEPLOYMENT = "gpt-4o-vision";
  process.env.AADITH_OPENAI_MODEL = "aadith-companion-luna";

  const config = getConfig();

  assert.equal(config.openAIModel, "aadith-companion-luna");
  assert.equal(config.allowedOrigins.has("https://www.aadithva.com"), true);
  assert.equal(process.env.AZURE_OPENAI_DEPLOYMENT, "gpt-4o-vision");

  delete process.env.AZURE_OPENAI_ENDPOINT;
  delete process.env.AZURE_OPENAI_DEPLOYMENT;
  delete process.env.AADITH_OPENAI_MODEL;
});

test("validation accepts a bounded conversation", () => {
  const request = validateChatRequest({
    messages: [
      { role: "assistant", content: "What would you like to know?" },
      { role: "user", content: "Tell me about Owly." },
    ],
  });

  assert.equal(request.messages.length, 2);
});

test("validation accepts model answers longer than the visitor limit", () => {
  const answer = "A".repeat(1_200);
  const request = validateChatRequest({
    messages: [
      { role: "assistant", content: answer },
      { role: "user", content: "What should I open next?" },
    ],
  });

  assert.equal(request.messages[0]?.content, answer);
});

test("validation compacts oversized assistant history", () => {
  const request = validateChatRequest({
    messages: [
      { role: "assistant", content: "A".repeat(4_000) },
      { role: "user", content: "Tell me more." },
    ],
  });
  const totalLength = request.messages.reduce(
    (total, message) => total + message.content.length,
    0
  );

  assert.ok(totalLength <= 3_600);
  assert.equal(request.messages.at(-1)?.role, "user");
  assert.match(request.messages[0]?.content ?? "", /Earlier answer shortened/);
});

test("validation keeps the visitor message limit", () => {
  assert.throws(
    () =>
      validateChatRequest({
        messages: [{ role: "user", content: "A".repeat(601) }],
      }),
    (error) => error instanceof RequestError && error.status === 400
  );
});

test("validation rejects an assistant as the final message", () => {
  assert.throws(
    () =>
      validateChatRequest({
        messages: [{ role: "assistant", content: "No question yet." }],
      }),
    (error) => error instanceof RequestError && error.status === 400
  );
});

test("memory rate limiting blocks requests over the local limit", async () => {
  process.env.RATE_LIMIT_MODE = "memory";
  clearRateLimits();

  for (let index = 0; index < 20; index += 1) {
    const result = await checkRateLimit("local-test-client");
    assert.equal(result.allowed, true);
  }

  const blocked = await checkRateLimit("local-test-client");
  assert.equal(blocked.allowed, false);
  assert.ok(blocked.retryAfterSeconds > 0);

  clearRateLimits();
  delete process.env.RATE_LIMIT_MODE;
});

test("distributed rate limiting retries initialization after a failure", async () => {
  delete process.env.RATE_LIMIT_MODE;
  delete process.env.AzureWebJobsStorage;
  process.env.RATE_LIMIT_SALT = "test-salt";
  clearRateLimits();

  await assert.rejects(
    checkRateLimit("retry-test-client"),
    /AzureWebJobsStorage or AZURE_STORAGE_CONNECTION_STRING is required/
  );

  process.env.AzureWebJobsStorage = "invalid-connection-string";
  await assert.rejects(
    checkRateLimit("retry-test-client"),
    (error) =>
      error instanceof Error &&
      !error.message.includes(
        "AzureWebJobsStorage or AZURE_STORAGE_CONNECTION_STRING is required"
      )
  );

  clearRateLimits();
  delete process.env.AzureWebJobsStorage;
  delete process.env.RATE_LIMIT_SALT;
});

test("client identity ignores spoofed leftmost forwarded values", () => {
  assert.equal(
    clientIdFromForwardedFor("198.51.100.20, 203.0.113.8:443"),
    "203.0.113.8"
  );
  assert.equal(
    clientIdFromForwardedFor("spoofed, [2001:db8::7]:8443"),
    "2001:db8::7"
  );
});

test("bounded body reads valid UTF-8 within the limit", async () => {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode("hello "));
      controller.enqueue(encoder.encode("Aadith"));
      controller.close();
    },
  });

  const result = await readBoundedBody(body, null, 32);

  assert.deepEqual(result, { text: "hello Aadith", exceeded: false });
});

test("bounded body rejects declared and streamed overflow", async () => {
  const declared = await readBoundedBody(null, "17", 16);
  assert.deepEqual(declared, { text: "", exceeded: true });

  const encoder = new TextEncoder();
  const streamed = await readBoundedBody(
    new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode("123456789"));
        controller.close();
      },
    }),
    null,
    8
  );
  assert.deepEqual(streamed, { text: "", exceeded: true });
});

test("node body reader stops once the byte cap is crossed", async () => {
  const body = Readable.from([
    Buffer.from("1234"),
    Buffer.from("5678"),
    Buffer.from("90"),
  ]);

  const result = await readBoundedNodeBody(body, undefined, 8);

  assert.deepEqual(result, { text: "", exceeded: true });
  assert.equal(body.readableFlowing, false);
});
