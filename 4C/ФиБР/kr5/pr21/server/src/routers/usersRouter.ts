import path from "node:path";
import type { Request, Response } from "express";
import { Router } from "express";
import { StatusCodes } from "http-status-codes";
import authMiddleware from "../middleware/authMiddleware";
import type { UserEntity } from "../types/UserEntity";
import dbFacade from "../utils/DbFacade";
import { getBadRequest, getNotFound, getOk } from "../utils/requestHelpers";
import cacheMiddleware, { CacheMiddlewareRequest } from "../middleware/cacheMiddleware";
import saveToCache from "../utils/cache/saveToCache";
import invalidateUsersCache from "../utils/cache/invalidateUsersCache";
import roleMiddleware from "../middleware/roleMiddleware";

const USERS_CACHE_TTL = 60; // 1 минута

const usersRouter: Router = Router();
const usersPath = path.resolve(__dirname, "../db/users.json");

usersRouter.get(
  "/",
  cacheMiddleware(() => "users:all", USERS_CACHE_TTL),
  async (req: CacheMiddlewareRequest, res: Response) => {
    const entries: UserEntity[] = await dbFacade.readEntries(usersPath);
    if (req.cacheKey && req.cacheKey?.length > 0) {
      await saveToCache(req.cacheKey, entries, req.cacheTTL);
    }
    return res.status(StatusCodes.OK).json(entries);
  },
);

usersRouter
  .get(
    "/:id",
    cacheMiddleware((req: Request) => `users:${req.params["id"]}`, USERS_CACHE_TTL),
    async (req: CacheMiddlewareRequest, res: Response) => {
      const { id } = req.params;
      if (!id) {
        return getBadRequest(res);
      }
      const entries: UserEntity[] = await dbFacade.readEntries(usersPath);
      const user = entries.find((u) => u.id === id);
      if (!user) {
        return getNotFound(res);
      }
      if (req.cacheKey && req.cacheKey?.length > 0) {
        await saveToCache(req.cacheKey, entries, req.cacheTTL);
      }
      return res.status(StatusCodes.OK).json(user);
    },
  )
  .put("/:id", authMiddleware, roleMiddleware(["admin"]), async (req: Request, res: Response) => {
    const { id, firstName, lastName, email, roles, blocked } = req.body;
    const entries: UserEntity[] = await dbFacade.readEntries(usersPath);
    const user = entries.find((u) => u.id === id);

    if (!user) {
      return res.status(404).json({
        error: "User not found",
      });
    }

    if (roles !== undefined) user.roles = roles;
    if (blocked !== undefined) user.blocked = blocked;
    if (firstName !== undefined) user.firstName = firstName;
    if (lastName !== undefined) user.lastName = lastName;
    if (email !== undefined) user.email = email;

    await dbFacade.updateEntryById(usersPath, id, user);
    await invalidateUsersCache(user.id);

    return res.json({
      id: user.id,
      firstName: user.firstName,
      lastName: user.lastName,
      roles: user.roles,
      blocked: user.blocked,
    });
  })
  .delete(
    "/:id",
    authMiddleware,
    // roleMiddleware(["admin"]), // FIXME: должно быть наверное два маршрута - для удаления своего аккаунта (auth) и удаления других пользователей напрямую (users)
    async (req: Request, res: Response) => {
      const { id } = req.params;
      const users = await dbFacade.readEntries<UserEntity>(usersPath);
      const user = users.find((u) => u.id === id);

      if (!user) {
        return res.status(404).json({
          error: "User not found",
        });
      }

      try {
        // TODO: удалять товары пользователя
        user.blocked = true;
        await invalidateUsersCache(user.id);
        // const products =
        //   await dbFacade.readEntries<ProductEntity>(productsPath);
        // const productsNotFromDeletedUser = products.filter(
        //   (p) => p.author_id !== id,
        // );
        // await dbFacade.deleteAllEntries(productsPath);
        // await dbFacade.createFile<ProductEntity>(
        //   productsPath,
        //   productsNotFromDeletedUser,
        // );
        return getOk(res, "user blocked");
      } catch (error) {
        console.error(error);
        return getNotFound(res, `user with id ${id} was not found or doesn't exist`);
      }
    },
  );

export default usersRouter;
