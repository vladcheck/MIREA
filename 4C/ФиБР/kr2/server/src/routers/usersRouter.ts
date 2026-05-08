import path from "node:path";
import type { Request, Response } from "express";
import { Router } from "express";
import { StatusCodes } from "http-status-codes";
import authMiddleware from "../middleware/authMiddleware";
import type { UserEntity } from "../types/UserEntity";
import dbFacade from "../utils/DbFacade";
import { getBadRequest, getNotFound, getOk } from "../utils/requestHelpers";

const usersRouter: Router = Router();
const usersPath = path.resolve(__dirname, "../db/users.json");

usersRouter.get("/", async (_req: Request, res: Response) => {
  const entries: UserEntity[] = await dbFacade.readEntries(usersPath);
  return res.status(StatusCodes.OK).json(entries);
});

usersRouter
  .get("/:id", async (req: Request, res: Response) => {
    const { id } = req.params;
    if (!id) {
      return getBadRequest(res);
    }
    const entries: UserEntity[] = await dbFacade.readEntries(usersPath);
    const user = entries.find((u) => u.id === id);
    if (!user) {
      return getNotFound(res);
    }

    return res.status(StatusCodes.OK).json(user);
  })
  .delete(
    "/:id",
    authMiddleware,
    // roleMiddleware(["admin"]), // FIXME: должно быть наверное два маршрута - для удаления своего аккаунта (auth) и удаления других пользователей напрямую (users)
    async (req: Request, res: Response) => {
      const { id } = req.params;
      if (!id) {
        return getBadRequest(res, "id not provided");
      }

      try {
        // TODO: удалять товары пользователя
        await dbFacade.deleteEntryById(usersPath, id as string);
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
        return getOk(res, "user deleted");
      } catch (error) {
        console.error(error);
        return getNotFound(
          res,
          `user with id ${id} was not found or doesn't exist`,
        );
      }
    },
  );

export default usersRouter;
