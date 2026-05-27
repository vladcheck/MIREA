import type { ModelStatic } from "sequelize";

export async function seedUsers(User: ModelStatic<any>) {
  const now = new Date();
  const mockUsers = [
    { age: 22, created_at: now, first_name: "Ivan", last_name: "Petrov", updated_at: now },
    { age: 25, created_at: now, first_name: "Anna", last_name: "Sidorova", updated_at: now },
    { age: 30, created_at: now, first_name: "Dmitry", last_name: "Volkov", updated_at: now },
  ];

  await User.bulkCreate(mockUsers);
  console.log("Database seeded with 3 mock users");
}
