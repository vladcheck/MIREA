import path from "node:path";
import type { Request, Response } from "express";
import { Router } from "express";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import multer from "multer";
import type { Product as ProductEntity } from "../../../shared/types/Product";
import authMiddleware from "../middleware/authMiddleware";
import roleMiddleware from "../middleware/roleMiddleware";
import type { ProductRequestBody } from "../types/productsRouter";
import dbFacade from "../utils/DbFacade";
import nextId from "../utils/nextId";
import {
  getBadRequest,
  getErrorString,
  getInternalServerError,
  getNotFound,
  getOk,
} from "../utils/requestHelpers";

const DEFAULT_PAGE = 1;
const DEFAULT_LIMIT = 20;

const storage = multer.diskStorage({
  destination: (_req: any, _file: any, cb: any) => {
    cb(null, path.resolve(__dirname, "../../public/images/products"));
  },
  filename: (_req: any, file: any, cb: any) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});
const upload = multer({ storage: storage });

const productsRouter: Router = Router();
export const productsPath = path.resolve(__dirname, "../db/products.json");

productsRouter
  .get("/", async (req: Request, res: Response) => {
    const queryParams: { author_id?: string; page?: string; limit?: string } =
      req.query as any;
    const entries: ProductEntity[] = await dbFacade.readEntries(productsPath);
    const filteredEntries = entries.filter((p) => {
      return queryParams.author_id
        ? p.author_id === queryParams.author_id
        : true;
    });

    const page = parseInt(queryParams.page || String(DEFAULT_PAGE), 10);
    const limit = parseInt(queryParams.limit || String(DEFAULT_LIMIT), 10);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    const items = filteredEntries.slice(startIndex, endIndex);

    return res.status(StatusCodes.OK).json({
      items,
      total: filteredEntries.length,
      page,
      limit,
      totalPages: Math.ceil(filteredEntries.length / limit),
    });
  })
  .post(
    "/",
    authMiddleware,
    roleMiddleware(["seller"]),
    upload.array("images", 10),
    async (req: Request, res: Response) => {
      const body: ProductRequestBody = req.body;
      if (!body) {
        return getBadRequest(res, "body is empty");
      }
      if (!body.price || !body.title || !body.category) {
        return getBadRequest(res);
      }
      if (Number.isNaN(parseFloat(body.price)) || parseFloat(body.price) < 0) {
        return res
          .status(StatusCodes.BAD_REQUEST)
          .send(
            getErrorString(
              `Некорректная цена`,
              req.body.price,
              `неотрицательное число`,
            ),
          );
      }

      const files = req.files as Express.Multer.File[];
      const uploadedImages =
        files?.map((f) => `/api/public/images/products/${f.filename}`) || [];

      const newProduct: ProductEntity = {
        id: nextId(),
        title: req.body.title,
        category: req.body.category,
        price: parseFloat(req.body.price),
        description: req.body.description ?? "",
        author_id: (req as any).user.sub,
      };

      if (uploadedImages.length > 0) {
        newProduct.images = uploadedImages;
      }

      try {
        await dbFacade.appendEntry(productsPath, newProduct);
        return res
          .status(StatusCodes.CREATED)
          .json(newProduct)
          .send(ReasonPhrases.CREATED);
      } catch (error) {
        console.error(error);
        return getInternalServerError(res, error);
      }
    },
  );

productsRouter
  .get("/:id", async (req: Request, res: Response) => {
    // TODO: нужен ли нам authMiddleware для GET?
    const { id } = req.params;
    if (!id) {
      return getBadRequest(res);
    }

    const products: ProductEntity[] = await dbFacade.readEntries(productsPath);
    const product = products.find((p) => p.id === id);
    if (!product) {
      return getNotFound(res);
    }

    return res.status(StatusCodes.OK).json(product);
  })
  .post(
    "/:id",
    authMiddleware,
    roleMiddleware(["seller"]),
    upload.array("images", 10),
    async (req: Request, res: Response) => {
      const { id } = req.params;
      if (!id) {
        return getBadRequest(res);
      }

      const products: ProductEntity[] =
        await dbFacade.readEntries(productsPath);
      const productIndex = products.findIndex((p) => p.id === id);
      if (productIndex === -1) {
        return getNotFound(res);
      }

      const p = products[productIndex]!;
      const userId = (req as any).user.sub;
      const isAdmin = (req as any).user.roles?.includes("admin");

      if (p.author_id !== userId && !isAdmin) {
        return res
          .status(StatusCodes.FORBIDDEN)
          .send("Access denied: You are not the author of this product.");
      }

      const b: Record<keyof typeof p, string> = req.body;

      if (b.title) p.title = b.title;
      if (b.description) p.description = b.description;

      const files = req.files as any[];
      if (files && files.length > 0) {
        const uploadedImages = files.map(
          (f) => `/api/public/images/products/${f.filename}`,
        );
        p.images = p.images ? [...p.images, ...uploadedImages] : uploadedImages;
      }

      if (b.price) {
        if (Number.isNaN(parseFloat(b.price)) || parseFloat(b.price) < 0) {
          return getBadRequest(
            res,
            getErrorString(
              "Некорректная цена",
              b.price,
              "неотрицательное число",
            ),
          );
        } else {
          p.price = parseFloat(b.price);
        }
      }

      return getOk(res);
    },
  )
  .delete(
    "/:id",
    authMiddleware,
    roleMiddleware(["seller"]),
    async (req: Request, res: Response) => {
      const { id } = req.params;
      if (!id) {
        return getBadRequest(res);
      }

      const products: ProductEntity[] =
        await dbFacade.readEntries(productsPath);
      const product = products.find((p) => p.id === id);
      if (!product) {
        return getNotFound(res, "product not found");
      }

      const userId = (req as any).user.sub;
      const isAdmin = (req as any).user.roles?.includes("admin");

      if (product.author_id !== userId && !isAdmin) {
        return res
          .status(StatusCodes.FORBIDDEN)
          .send("Access denied: You are not the author of this product.");
      }

      try {
        await dbFacade.deleteEntryById(productsPath, product.id);
        return getOk(res);
      } catch (error) {
        console.error(error);
        return getInternalServerError(res, error);
      }
    },
  );

export default productsRouter;
