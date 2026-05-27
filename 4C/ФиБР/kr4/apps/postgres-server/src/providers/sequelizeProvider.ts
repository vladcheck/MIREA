import { Sequelize } from "sequelize";

const DEFAULT_PORT = 5432;

interface ConnectionConfig {
  name: string;
  user: string;
  password: string;
  host?: string;
  port?: number;
  logging?: boolean;
}

export function createSequelizeConnection({
  name,
  user,
  password,
  host = "localhost",
  port = DEFAULT_PORT,
  logging = false,
}: ConnectionConfig) {
  const sequelize = new Sequelize(name, user, password, {
    dialect: "postgres",
    host,
    logging,
    port,
  });

  sequelize.authenticate();
  sequelize
    .authenticate()
    .then(async () => {
      console.log("Connected to PostgreSQL");
      const result = await sequelize.query("SELECT current_user;");
      // oxlint-disable-next-line no-magic-numbers
      console.log("Connected as:", result[0][0]);
    })
    .catch((err) => console.error("Connection error:", err));

  return sequelize;
}
