import path from "node:path";
import type { Request, Response } from "express";
import { Router } from "express";
import { StatusCodes } from "http-status-codes";
import type { JwtPayload } from "jsonwebtoken";
import type { UserRequestBody } from "../../../shared/types/User";
import authMiddleware from "../middleware/authMiddleware";
import type { UserEntity } from "../types/UserEntity";
import dbFacade from "../utils/DbFacade";
import jwtSingleton, { type TokenType } from "../utils/jwt";
import nextId from "../utils/nextId";
import { hashPassword, verifyPassword } from "../utils/password";
import {
  getBadRequest,
  getErrorString,
  getInternalServerError,
  getNotFound,
  getUnauthorized,
} from "../utils/requestHelpers";

function sanitize<T extends { hash: string }>(value: T): Omit<T, "hash"> {
  const valueCopy = Object.assign(value);
  delete valueCopy.hash;
  return valueCopy;
}

const authRouter: Router = Router();
const userPath = path.resolve("src", "db", "users.json");

function getUserTokenBody(user: UserEntity, type: TokenType) {
  return type === "access"
    ? Object.entries(user).filter(([k]) => {
        return k !== "id";
      })
    : { firstName: user.firstName };
}

authRouter.post("/register", async (req: Request, res: Response) => {
  const b: UserRequestBody = req.body;

  if (!b.email || !b.firstName || !b.lastName || !b.password) {
    return getBadRequest(res);
  }
  if (b.password.length < 4) {
    return getBadRequest(
      res,
      getErrorString("Слишком короткий пароль", b.password),
    );
  } else if (b.password.length > 32) {
    return getBadRequest(
      res,
      getErrorString("Слишком длинный пароль", b.password),
    );
  } else if (!b.password.match(/^[a-zA-Z0-9_{}\[\]();:!?$%.,^\\\/]{4,32}$/)) {
    return getBadRequest(
      res,
      getErrorString(
        "Пароль может содержать только латинские буквы, цифры от 0 до 9, и символы !?:;.,$^/[](){}%",
        b.password,
      ),
    );
  }

  if (!b.firstName.match(/^[A-ZА-ЯЁ][a-zа-яё]{1,63}$/)) {
    return getBadRequest(res, getErrorString("Некорретное имя", b.firstName));
  }

  if (!b.lastName.match(/^[A-ZА-ЯЁ][a-zа-яё]{1,63}$/)) {
    return getBadRequest(
      res,
      getErrorString("Некорретная фамилия", b.lastName),
    );
  }

  if (b.email.length < 5) {
    return getBadRequest(
      res,
      getErrorString("Почта не может быть короче пяти символов", b.firstName),
    );
  } else if (!b.email.match(/[a-zA-Z0-9_]{1,}@[a-z0-9]{1,}\.[a-z]{2,6}/)) {
    return getBadRequest(
      res,
      getErrorString("Неправильная почта", b.firstName),
    );
  } else {
    const entries: UserEntity[] = await dbFacade.readEntries(userPath);
    if (entries.some((u) => u.email === b.email)) {
      return res
        .status(StatusCodes.CONFLICT)
        .send("Профиль с такой почтой уже существует.");
    }
  }

  if (!b.roles || b.roles.length === 0) {
    return getBadRequest(res, "Роли не указаны");
  }

  const u: UserEntity = {
    id: nextId(),
    firstName: b.firstName,
    lastName: b.lastName,
    email: b.email,
    hash: await hashPassword(b.password),
    roles: b.roles,
  };

  try {
    await dbFacade.appendEntry(userPath, u);
  } catch (error) {
    console.error(error);
    return res
      .status(StatusCodes.INTERNAL_SERVER_ERROR)
      .send(`couldn't write to database: ${error}`);
  }

  const accessToken = jwtSingleton.grantAccessToken(
    u.id,
    getUserTokenBody(u, "access"),
  );
  const refreshToken = jwtSingleton.grantRefreshToken(u.id, {
    firstName: u.firstName,
  });

  return res
    .status(StatusCodes.CREATED)
    .json({ accessToken, refreshToken, id: u.id });
});

authRouter.post("/login", async (req: Request, res: Response) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return getBadRequest(res);
  }

  const entries: UserEntity[] = await dbFacade.readEntries(userPath);
  const u = entries.find((u) => u.email === email);
  if (!u) {
    return getNotFound(res);
  }

  const passwordsMatch = await verifyPassword(password, u.hash);
  if (!passwordsMatch) {
    return getBadRequest(res, "Invalid credentials.");
  }

  const accessToken = jwtSingleton.grantAccessToken(
    u.id,
    getUserTokenBody(u, "access"),
  );
  const refreshToken = jwtSingleton.grantRefreshToken(u.id, {
    firstName: u.firstName,
  });

  return res
    .status(StatusCodes.OK)
    .json({ accessToken, refreshToken, id: u.id });
});

authRouter.post("/refresh", async (req: Request, res: Response) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    return getBadRequest(res, "Refresh token is required");
  }

  if (jwtSingleton.isTokenValid(refreshToken, "refresh")) {
    return getUnauthorized(res, "Invalid refresh token");
  }

  try {
    const payload = jwtSingleton.verify(refreshToken, "refresh");

    const entries: UserEntity[] = await dbFacade.readEntries(userPath);
    const u = entries.find((u) => u.id === payload.sub);
    if (!u) {
      return getNotFound(res, "user not found");
    }

    const { newAccessToken, newRefreshToken } = jwtSingleton.rotateTokens(
      refreshToken,
      u.id,
      getUserTokenBody(u, "access"),
      getUserTokenBody(u, "refresh"),
    );

    return res
      .status(StatusCodes.OK)
      .json({ accessToken: newAccessToken, refreshToken: newRefreshToken });
  } catch {
    return getUnauthorized(res, "Invalid or expired refresh token");
  }
});

authRouter.get(
  "/me",
  authMiddleware,
  async (req: Request & JwtPayload, res: Response) => {
    const id = req["user"]?.sub;
    if (!id) {
      return getInternalServerError(res);
    }

    const entries: UserEntity[] = await dbFacade.readEntries(userPath);
    const u = entries.find((u) => u.id === id);
    if (!u) {
      return getNotFound(res);
    }

    res.status(StatusCodes.OK).json(sanitize(u));
  },
);

export default authRouter;
