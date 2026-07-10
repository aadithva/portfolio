import { createHash } from "node:crypto";
import { TableClient, type TableEntityResult } from "@azure/data-tables";

const WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS = 20;
const TABLE_NAME = "CompanionRateLimits";
const PARTITION_KEY = "client";
const MAX_RETRIES = 5;

interface RateLimitEntity {
  windowStart: number;
  count: number;
  updatedAt: string;
}

const memoryRequests = new Map<string, number[]>();
let tableClientPromise: Promise<TableClient> | undefined;

const statusCodeOf = (error: unknown): number | undefined => {
  if (!error || typeof error !== "object") return undefined;
  const statusCode = (error as { statusCode?: unknown }).statusCode;
  return typeof statusCode === "number" ? statusCode : undefined;
};

const hashClientId = (clientId: string): string => {
  const salt = process.env.RATE_LIMIT_SALT?.trim();
  if (!salt) {
    throw new Error("RATE_LIMIT_SALT is required for distributed rate limiting");
  }

  return createHash("sha256")
    .update(`${salt}:${clientId}`)
    .digest("hex");
};

const getTableClient = async (): Promise<TableClient> => {
  if (tableClientPromise) return tableClientPromise;

  const pendingClient = (async () => {
    const connectionString =
      process.env.AzureWebJobsStorage?.trim() ||
      process.env.AZURE_STORAGE_CONNECTION_STRING?.trim();
    if (!connectionString) {
      throw new Error(
        "AzureWebJobsStorage or AZURE_STORAGE_CONNECTION_STRING is required for distributed rate limiting"
      );
    }

    const client = TableClient.fromConnectionString(
      connectionString,
      TABLE_NAME
    );

    try {
      await client.createTable();
    } catch (error) {
      if (statusCodeOf(error) !== 409) throw error;
    }

    return client;
  })();
  tableClientPromise = pendingClient;

  try {
    return await pendingClient;
  } catch (error) {
    if (tableClientPromise === pendingClient) {
      tableClientPromise = undefined;
    }
    throw error;
  }
};

const memoryRateLimit = (clientId: string) => {
  const now = Date.now();
  const cutoff = now - WINDOW_MS;
  const recent = (memoryRequests.get(clientId) ?? []).filter(
    (timestamp) => timestamp > cutoff
  );

  if (recent.length >= MAX_REQUESTS) {
    const retryAt = recent[0] + WINDOW_MS;
    return {
      allowed: false,
      retryAfterSeconds: Math.max(1, Math.ceil((retryAt - now) / 1000)),
    };
  }

  recent.push(now);
  memoryRequests.set(clientId, recent);
  return { allowed: true, retryAfterSeconds: 0 };
};

const distributedRateLimit = async (clientId: string) => {
  const client = await getTableClient();
  const now = Date.now();
  const windowStart = Math.floor(now / WINDOW_MS) * WINDOW_MS;
  const windowEnd = windowStart + WINDOW_MS;
  const rowKey = hashClientId(clientId);

  for (let attempt = 0; attempt < MAX_RETRIES; attempt += 1) {
    let entity: TableEntityResult<RateLimitEntity> | undefined;

    try {
      entity = await client.getEntity<RateLimitEntity>(
        PARTITION_KEY,
        rowKey
      );
    } catch (error) {
      if (statusCodeOf(error) !== 404) throw error;
    }

    if (!entity) {
      try {
        await client.createEntity({
          partitionKey: PARTITION_KEY,
          rowKey,
          windowStart,
          count: 1,
          updatedAt: new Date(now).toISOString(),
        });
        return { allowed: true, retryAfterSeconds: 0 };
      } catch (error) {
        if (statusCodeOf(error) === 409) continue;
        throw error;
      }
    }

    const inCurrentWindow = entity.windowStart === windowStart;
    if (inCurrentWindow && entity.count >= MAX_REQUESTS) {
      return {
        allowed: false,
        retryAfterSeconds: Math.max(
          1,
          Math.ceil((windowEnd - now) / 1000)
        ),
      };
    }

    const nextEntity = {
      partitionKey: PARTITION_KEY,
      rowKey,
      windowStart,
      count: inCurrentWindow ? entity.count + 1 : 1,
      updatedAt: new Date(now).toISOString(),
    };

    try {
      await client.updateEntity(nextEntity, "Replace", {
        etag: entity.etag,
      });
      return { allowed: true, retryAfterSeconds: 0 };
    } catch (error) {
      if (statusCodeOf(error) === 412) continue;
      throw error;
    }
  }

  throw new Error("Rate limit counter could not be updated");
};

export async function checkRateLimit(clientId: string): Promise<{
  allowed: boolean;
  retryAfterSeconds: number;
}> {
  if (process.env.RATE_LIMIT_MODE === "memory") {
    return memoryRateLimit(clientId);
  }

  return distributedRateLimit(clientId);
}

export function clearRateLimits(): void {
  memoryRequests.clear();
  tableClientPromise = undefined;
}
