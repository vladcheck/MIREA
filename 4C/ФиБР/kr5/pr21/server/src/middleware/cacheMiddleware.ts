import type { Request, Response } from "express";
import { redisClient } from "../utils/redis";

export default function cacheMiddleware(keyBuilder: any, ttl: number) {
  return async (req: CacheMiddlewareRequest, res: Response, next: Function) => {
    try {
      const key = keyBuilder(req);
      const cachedData = await redisClient.get(key);

      if (cachedData) {
        return res.json({
          source: "cache",
          data: JSON.parse(cachedData),
        });
      }

      req.cacheKey = key;
      req.cacheTTL = ttl;
      next();
    } catch (err) {
      console.error("Cache read error:", err);
      next();
    }
    return;
  };
}

export type CacheMiddlewareRequest = Request & Partial<{ cacheKey: string; cacheTTL: number }>;
