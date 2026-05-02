import 'dotenv-defaults/config';
import { StatusCodes } from "http-status-codes";
import { createPool } from "./src/providers/poolProvider.ts";
import { createSequelizeConnection } from "./src/providers/sequelizeProvider.ts";
import { defineUserModel } from "./src/models/UserModel.ts";
import express from "express";
import { getEnvVarSafely } from "./src/utils/env.ts";

export const config: Config = {};

try {
  config.POSTGRES_PASSWORD = getEnvVarSafely("POSTGRES_PASSWORD");
  config.POSTGRES_DB = getEnvVarSafely("POSTGRES_DB");
  config.POSTGRES_USER = getEnvVarSafely("POSTGRES_USER");
} catch (error: any) {
  throw new Error(error, { cause: error });
}

const sequelize = createSequelizeConnection({
  name: config.POSTGRES_DB,
  password: config.POSTGRES_PASSWORD,
  user: config.POSTGRES_USER,
});
const User = defineUserModel(sequelize);
sequelize.sync({ force: true });

createPool(config);

const app = express();
app.use(express.json());

app.get("/api/users", async (req, res) => {
  try {
    const users = await User.findAll();
    res.send(users);
  } catch (err: any) {
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(err.message);
  }
});

app.post("/api/users", async (req, res) => {
  try {
    const user = await User.create(req.body);
    res.status(StatusCodes.CREATED).send(user);
  } catch (err: any) {
    res.status(StatusCodes.BAD_REQUEST).send(err.message);
  }
});

app.get("/api/users/:id", async (req, res) => {
  try {
    const user = await User.findOne({
      where: {
        id: req.body.id,
      },
    });
    res.send(user);
  } catch (err: any) {
    res.status(StatusCodes.BAD_REQUEST).send(err.message);
  }
});

app.patch("/api/users/:id", async (req, res) => {
  try {
    const user = await User.update(req.body, {
      returning: true,
      where: { id: req.params.id }, // Для PostgreSQL (возвращает обновленную запись)
    });
    res.send(user);
  } catch (err: any) {
    res.status(StatusCodes.BAD_REQUEST).send(err.message);
  }
});

app.delete("/api/users/:id", async (req, res) => {
  try {
    await User.destroy({ where: { id: req.params.id } });
    res.send({ message: "User deleted" });
  } catch (err: any) {
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(err.message);
  }
});

app.get("/api", async (_, res) => {
  res.status(StatusCodes.OK).send("OK")
});

app.listen(process.env.PORT, () => {
  console.log(`Server is running on http://localhost:${config.POSTGRES_PORT}`);
});
