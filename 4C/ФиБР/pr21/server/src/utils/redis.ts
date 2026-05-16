import { createClient, RedisClientType } from "redis";

export const redisClient: RedisClientType = createClient({
  url: `redis://127.0.0.1:${process.env["REDIS_PORT"]}`,
});

redisClient.on("error", (err: any) => {
  console.error("Redis error:", err);
});

export async function initRedis() {
  await redisClient.connect();
  console.log("Redis connected");
}