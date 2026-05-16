import { redisClient } from "../../redis";

export default function buildInvalidator(key: string) {
  return async (entityId?: string) => {
    try {
      await redisClient.del(key);
      if (entityId) {
        await redisClient.del(`${key}:${entityId}`);
      }
    } catch (err) {
      console.error(`${key} cache invalidate error:`, err);
    }
  };
}
