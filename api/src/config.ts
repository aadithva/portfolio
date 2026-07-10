const required = (name: string): string => {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Missing required setting: ${name}`);
  return value;
};

const normalizeEndpoint = (value: string): string => {
  const base = value.replace(/\/+$/, "");
  return base.endsWith("/openai/v1")
    ? `${base}/`
    : `${base}/openai/v1/`;
};

export interface ChatConfig {
  openAIEndpoint: string;
  openAIModel: string;
  openAIKey?: string;
  contextUrl: string;
  allowedOrigins: Set<string>;
}

export function getConfig(): ChatConfig {
  const origins =
    process.env.ALLOWED_ORIGINS ??
    "https://aadithva.com,https://www.aadithva.com,http://localhost:4321,http://127.0.0.1:4321";

  return {
    openAIEndpoint: normalizeEndpoint(
      process.env.AADITH_OPENAI_ENDPOINT?.trim() ||
        required("AZURE_OPENAI_ENDPOINT")
    ),
    openAIModel:
      process.env.AADITH_OPENAI_MODEL?.trim() ||
      process.env.AZURE_OPENAI_MODEL?.trim() ||
      required("AZURE_OPENAI_DEPLOYMENT"),
    openAIKey:
      process.env.AADITH_OPENAI_API_KEY?.trim() ||
      process.env.AZURE_OPENAI_API_KEY?.trim() ||
      undefined,
    contextUrl:
      process.env.AADITH_CONTEXT_URL?.trim() ||
      "https://aadithva.com/aadith-context.json",
    allowedOrigins: new Set(
      origins
        .split(",")
        .map((origin) => origin.trim())
        .filter(Boolean)
    ),
  };
}
