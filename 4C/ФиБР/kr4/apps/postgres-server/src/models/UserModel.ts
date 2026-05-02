import { DataTypes, type Sequelize } from "sequelize";
import injectId from "../utils/injectId.ts";

export const defineUserModel = (sequelize: Sequelize) =>
  sequelize.define(
    "User",
    injectId({
      age: { allowNull: false, type: DataTypes.INTEGER },
      created_at: { allowNull: false, type: DataTypes.DATE },
      first_name: { allowNull: false, type: DataTypes.STRING },
      last_name: { allowNull: false, type: DataTypes.STRING },
      updated_at: { allowNull: false, type: DataTypes.DATE },
    }),
  );
