import { Pool } from "pg";

export const createPool = (config: Config) =>
  new Pool({
    database: config.POSTGRES_DB,
    host: "localhost",
    password: config.POSTGRES_PASSWORD,
    port: parseInt(config.POSTGRES_PORT ?? "5432"),
    user: config.POSTGRES_USER,
  });
