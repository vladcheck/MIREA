import "dotenv/config";
import { StatusCodes } from "http-status-codes";
import { asyncHandler } from "./src/utils/asyncHandler.ts";
import { createPool } from "./src/providers/poolProvider.ts";
import { createSequelizeConnection } from "./src/providers/sequelizeProvider.ts";
import { defineUserModel } from "./src/models/UserModel.ts";
import express from "express";
import { getEnvVarSafely } from "./src/utils/env.ts";
import { seedUsers } from "./src/seeds/userSeed.ts";

export const config: Config = {};
try {
  config.POSTGRES_PASSWORD = getEnvVarSafely("POSTGRES_PASSWORD");
  config.POSTGRES_DB = getEnvVarSafely("POSTGRES_DB");
  config.POSTGRES_USER = getEnvVarSafely("POSTGRES_USER");
  config.POSTGRES_PORT = getEnvVarSafely("POSTGRES_PORT");
  config.POSTGRES_HOST = process.env.POSTGRES_HOST || "localhost";
} catch (error: any) {
  throw new Error(error, { cause: error });
}

const SERVER_ID = process.env.SERVER_ID || "pg-unknown";

const sequelize = createSequelizeConnection({
  name: config.POSTGRES_DB,
  password: config.POSTGRES_PASSWORD,
  port: parseInt(config.POSTGRES_PORT),
  user: config.POSTGRES_USER,
  host: config.POSTGRES_HOST,
});

const User = defineUserModel(sequelize);

async function startServer() {
  await sequelize.sync({ force: true });
  if (process.env.NODE_ENV === "development") {
    await seedUsers(User);
  }
  createPool(config);

  const app = express();
  app.use(express.json());

  // Add server ID to all responses
  app.use((req, res, next) => {
    const originalSend = res.send.bind(res);
    res.send = (body) => {
      if (typeof body === "object" && body !== null && !Array.isArray(body)) {
        return originalSend({ ...body, _server_id: SERVER_ID });
      }
      return originalSend(body);
    };
    next();
  });

  app.get(
    "/api/users",
    asyncHandler(async (req, res) => {
      const users = await User.findAll();
      res.send(users);
    }),
  );

  app.post(
    "/api/users",
    asyncHandler(async (req, res) => {
      const user = await User.create(req.body);
      res.status(StatusCodes.CREATED).send(user);
    }),
  );

  app.get(
    "/api/users/:id",
    asyncHandler(async (req, res) => {
      const user = await User.findOne({
        where: { id: req.params.id },
      });
      res.send(user);
    }),
  );

  app.patch(
    "/api/users/:id",
    asyncHandler(async (req, res) => {
      const user = await User.update(req.body, {
        returning: true,
        where: { id: req.params.id },
      });
      res.send(user);
    }),
  );

  app.delete(
    "/api/users/:id",
    asyncHandler(async (req, res) => {
      await User.destroy({ where: { id: req.params.id } });
      res.send({ message: "User deleted" });
    }),
  );

  app.get("/api", (_, res) => {
    res.status(StatusCodes.OK).send({ status: "OK", server: SERVER_ID });
  });

  app.get("/", (_, res) => {
    res.status(StatusCodes.OK).send({ status: "OK", server: SERVER_ID });
  });

  const PORT = parseInt(process.env.PORT || "3000");
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server ${SERVER_ID} running on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error("Failed to start server:", err);
  process.exit(1);
});
