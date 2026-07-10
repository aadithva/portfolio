export interface BoundedBody {
  text: string;
  exceeded: boolean;
}

interface ReadableBody {
  getReader(): {
    read(): Promise<{ done: boolean; value?: unknown }>;
    cancel(reason?: unknown): Promise<void>;
    releaseLock(): void;
  };
}

export async function readBoundedBody(
  body: ReadableBody | null,
  contentLength: string | null,
  maxBytes: number
): Promise<BoundedBody> {
  const declaredBytes = Number(contentLength);
  if (
    contentLength &&
    Number.isFinite(declaredBytes) &&
    declaredBytes >= 0 &&
    declaredBytes > maxBytes
  ) {
    return { text: "", exceeded: true };
  }

  if (!body) return { text: "", exceeded: false };

  const reader = body.getReader();
  const decoder = new TextDecoder();
  let bytes = 0;
  let text = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        return {
          text: text + decoder.decode(),
          exceeded: false,
        };
      }

      if (!(value instanceof Uint8Array)) {
        throw new TypeError("Request body contained a non-byte chunk");
      }

      bytes += value.byteLength;
      if (bytes > maxBytes) {
        await reader.cancel();
        return { text: "", exceeded: true };
      }

      text += decoder.decode(value, { stream: true });
    }
  } finally {
    reader.releaseLock();
  }
}
