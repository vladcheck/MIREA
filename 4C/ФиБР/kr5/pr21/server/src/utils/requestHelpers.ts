import type { Response } from "express";
import { ReasonPhrases, StatusCodes } from "http-status-codes";

const getRequestHelperFactory = (status: number, reason: string) => {
  return (res: Response, send?: unknown) => {
    res.status(status).send(send ?? reason);
  };
};
export const getOk = getRequestHelperFactory(StatusCodes.OK, ReasonPhrases.OK);
export const getNotFound = getRequestHelperFactory(
  StatusCodes.NOT_FOUND,
  ReasonPhrases.NOT_FOUND,
);
export const getBadRequest = getRequestHelperFactory(
  StatusCodes.BAD_REQUEST,
  ReasonPhrases.BAD_REQUEST,
);
export const getCreated = getRequestHelperFactory(
  StatusCodes.CREATED,
  ReasonPhrases.CREATED,
);
export const getUnauthorized = getRequestHelperFactory(
  StatusCodes.UNAUTHORIZED,
  ReasonPhrases.UNAUTHORIZED,
);
export const getInternalServerError = getRequestHelperFactory(
  StatusCodes.INTERNAL_SERVER_ERROR,
  ReasonPhrases.INTERNAL_SERVER_ERROR,
);

export const getErrorString = (msg: string, value: any, expected?: string) =>
  `${msg} (${value})${expected ? `. Ожидалось: ${expected}` : ""}`;
