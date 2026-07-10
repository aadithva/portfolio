import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";
import OpenAI from "openai";
import type { ChatConfig } from "./config.js";

const credential = new DefaultAzureCredential();
const tokenProvider = getBearerTokenProvider(
  credential,
  "https://cognitiveservices.azure.com/.default"
);

export async function createOpenAIClient(config: ChatConfig): Promise<OpenAI> {
  const apiKey = config.openAIKey ?? (await tokenProvider());
  return new OpenAI({
    baseURL: config.openAIEndpoint,
    apiKey,
  });
}
