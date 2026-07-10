import { Buffer } from "node:buffer";
import type { Readable } from "node:stream";
import type { BoundedBody } from "./boundedBody.js";

export async function readBoundedNodeBody(
  body: Readable,
  contentLength: string | undefined,
  maxBytes: number
): Promise<BoundedBody> {
  const declaredBytes = Number(contentLength);
  if (
    contentLength &&
    Number.isFinite(declaredBytes) &&
    declaredBytes >= 0 &&
    declaredBytes > maxBytes
  ) {
    body.pause();
    return { text: "", exceeded: true };
  }

  const chunks: Buffer[] = [];
  let captured = 0;

  for await (const chunk of body.iterator({ destroyOnReturn: false })) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    if (captured + buffer.length > maxBytes) {
      body.pause();
      return { text: "", exceeded: true };
    }

    chunks.push(buffer);
    captured += buffer.length;
  }

  return {
    text: Buffer.concat(chunks).toString("utf8"),
    exceeded: false,
  };
}
