// 3. Проверка возраста
// Реализуйте функцию checkAge(age), возвращающую промис. Если age
// >= 18, промис выполняется успешно (resolve("Доступ разрешён")), иначе
// отклоняется (reject("Доступ запрещён")).

async function checkAge(age) {
  if (age >= 18) {
    return Promise.resolve("Доступ разрешен");
  } else {
    return Promise.reject("Доступ запрещён");
  }
}
