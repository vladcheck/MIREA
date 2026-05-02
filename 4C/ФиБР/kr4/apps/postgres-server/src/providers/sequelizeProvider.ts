import { Sequelize } from "sequelize";

export function createSequelizeConnection({
  name,
  user,
  password,
  host = "localhost",
}: {
  name: string;
  user: string;
  password: string;
  host?: string;
}) {
  const sequelize = new Sequelize(name, user, password, {
    dialect: "postgres",
    host,
  });

  sequelize
    .authenticate()
    .then(() => console.log("Connected to PostgreSQL"))
    .catch((err) => console.error("Connection error:", err));

  return sequelize;
}
