import type { ChatMessage, ChatRequest } from "./contracts.js";

const MAX_MESSAGES = 8;
const MAX_USER_MESSAGE_LENGTH = 600;
const MAX_TOTAL_LENGTH = 3_600;
const TRUNCATION_MARKER = "\n[Earlier answer shortened]\n";
export const MAX_BODY_BYTES = 16_384;

export class RequestError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "RequestError";
  }
}

const isMessage = (value: unknown): value is ChatMessage => {
  if (!value || typeof value !== "object") return false;
  const message = value as Record<string, unknown>;
  return (
    (message.role === "user" || message.role === "assistant") &&
    typeof message.content === "string"
  );
};

const shortenAssistantMessage = (content: string, limit: number): string => {
  if (content.length <= limit) return content;
  if (limit <= TRUNCATION_MARKER.length) return content.slice(0, limit);

  const available = limit - TRUNCATION_MARKER.length;
  const headLength = Math.ceil(available * 0.6);
  const tailLength = available - headLength;
  return `${content.slice(0, headLength)}${TRUNCATION_MARKER}${content.slice(-tailLength)}`;
};

const compactMessages = (messages: ChatMessage[]): ChatMessage[] => {
  const compacted: ChatMessage[] = [];
  let remaining = MAX_TOTAL_LENGTH;

  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.content.length <= remaining) {
      compacted.unshift(message);
      remaining -= message.content.length;
      continue;
    }

    if (message.role === "assistant" && remaining > 0) {
      compacted.unshift({
        role: message.role,
        content: shortenAssistantMessage(message.content, remaining),
      });
    }
    break;
  }

  return compacted;
};

export function validateChatRequest(value: unknown): ChatRequest {
  if (!value || typeof value !== "object") {
    throw new RequestError("Request body must be a JSON object.", 400);
  }

  const request = value as Record<string, unknown>;
  if (!Array.isArray(request.messages) || request.messages.length === 0) {
    throw new RequestError("At least one message is required.", 400);
  }

  if (request.messages.length > MAX_MESSAGES) {
    throw new RequestError(`Keep the conversation to ${MAX_MESSAGES} messages.`, 400);
  }

  if (!request.messages.every(isMessage)) {
    throw new RequestError("Each message needs a valid role and text content.", 400);
  }

  const messages = request.messages.map((message) => ({
    role: message.role,
    content: message.content.trim(),
  }));

  if (messages.some((message) => message.content.length === 0)) {
    throw new RequestError("Messages cannot be empty.", 400);
  }

  if (
    messages.some(
      (message) =>
        message.role === "user" &&
        message.content.length > MAX_USER_MESSAGE_LENGTH
    )
  ) {
    throw new RequestError(
      `Visitor messages must be ${MAX_USER_MESSAGE_LENGTH} characters or fewer.`,
      400
    );
  }

  if (messages.at(-1)?.role !== "user") {
    throw new RequestError("The final message must be from the visitor.", 400);
  }

  return { messages: compactMessages(messages) };
}
