import { RedisArgument } from "redis";
import { redisClient } from "../redis";

export default async function saveToCache(key: RedisArgument, data: any, ttl: any) {
  try {
    await redisClient.set(key, JSON.stringify(data), {
      EX: ttl,
    });
  } catch (err) {
    console.error("Cache save error:", err);
  }
}
