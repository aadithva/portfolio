export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
}

export interface ContextSource {
  id: string;
  title: string;
  path: string;
  category: string;
}

export interface ContextChunk extends ContextSource {
  tags: string[];
  body: string;
}

export interface ContextDocument {
  version: string;
  owner: string;
  boundary: string;
  chunks: ContextChunk[];
}

export interface ChatResponse {
  answer: string;
  sources: ContextSource[];
}
