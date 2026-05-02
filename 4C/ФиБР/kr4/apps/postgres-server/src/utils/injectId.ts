import { DataTypes, type Model, type ModelAttributes } from "sequelize";

export default function injectId<T extends ModelAttributes<Model<any, any>, any>>(
  modelDefinition: T,
): T & {
  id: { allowNull: false, autoIncrement: true, primaryKey: true, type: typeof DataTypes.BIGINT }
} {
  return {
    id: { allowNull: false, autoIncrement: true, primaryKey: true, type: DataTypes.BIGINT },
    ...modelDefinition,
  };
}
