import type { NextFunction, Request, Response } from "express";
import type { JwtPayload } from "jsonwebtoken";
import type { UserRole } from "../../../shared/types/User";
import { getBadRequest } from "../utils/requestHelpers";

export default function roleMiddleware(_allowedRoles: UserRole[]) {
  return (
    req: Request & { user?: JwtPayload },
    res: Response,
    next: NextFunction,
  ) => {
    if (!req.user) {
      return getBadRequest(res);
    }
    // if (!req.user["roles"].some((r: UserRole) => allowedRoles.includes(r))) {
    //   return res.status(403).json({
    //     error: "Forbidden",
    //   });
    // }
    next();
    return;
  };
}
