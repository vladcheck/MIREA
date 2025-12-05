using restaurant;

class Program
{
    public static OrderSystemManager manager = new();
    public static Random random = new();

    static void Main()
    {
        manager.AddDish([new Dish("Борщ", "Свекла, капуста, картофель, мясо, вода", "300/50/30", 150.0, Category.Soup, 20,[ "горячее"]),
        new Dish("Оливье", "Картофель, морковь, огурцы, колбаса", "200/30", 120.0, Category.Salad, 10,[ "холодное"]),
        new Dish("Компот", "Ягоды, вода", "250", 80.0, Category.Beverage, 5, ["веганское"])]);

        bool running = true;
        while (running)
        {
            ShowMainMenu();

            if (!byte.TryParse(Console.ReadLine(), out byte choice))
            {
                Console.Clear();
                continue;
            }

            switch (choice)
            {
                case 1:
                    AddDish();
                    break;
                case 2:
                    EditDish();
                    break;
                case 3:
                    DeleteDish();
                    break;
                case 4:
                    ViewDish();
                    break;
                case 5:
                    AddOrder();
                    break;
                case 6:
                    EditOrder();
                    break;
                case 7:
                    CloseOrder();
                    break;
                case 8:
                    ViewOrder();
                    break;
                case 9:
                    PrintOrderCheck();
                    break;
                case 10:
                    manager.PrintMenu();
                    break;
                case 11:
                    ViewTotalRevenue();
                    break;
                case 12:
                    ViewWaiterStats();
                    break;
                case 13:
                    manager.PrintDishStatistics();
                    break;
                case 0:
                    running = false;
                    Console.WriteLine("Выход из программы...");
                    break;
                default:
                    Console.WriteLine("Неверный выбор. Попробуйте снова.");
                    break;
            }

            if (running && choice != 0)
            {
                Console.WriteLine("\nНажмите любую клавишу для продолжения...");
                Console.ReadKey();
                Console.Clear();
            }
        }
    }

    static void ShowMainMenu()
    {
        string menu = "Выберите действие (0-13)\n" +
                     "1. Добавить блюдо\n" +
                     "2. Редактировать блюдо\n" +
                     "3. Удалить блюдо\n" +
                     "4. Просмотреть блюдо\n" +
                     "5. Создать заказ\n" +
                     "6. Изменить заказ\n" +
                     "7. Закрыть заказ\n" +
                     "8. Просмотреть заказ\n" +
                     "9. Распечатать чек\n" +
                     "10. Просмотреть меню\n" +
                     "11. Общая выручка\n" +
                     "12. Статистика официанта\n" +
                     "13. Статистика по блюдам\n" +
                     "0. Выход\n";

        Console.Write(menu);
    }

    static int GetIntInput()
    {
        int result;
        while (!int.TryParse(Console.ReadLine(), out result))
        {
            Console.Write("Введите число: ");
        }
        return result;
    }

    static double GetDoubleInput()
    {
        double result;
        while (!double.TryParse(Console.ReadLine(), out result))
        {
            Console.Write("Введите число: ");
        }
        return result;
    }

    static void AddDish()
    {
        string name;
        do
        {
            Console.Write("Введите название блюда (не может быть пустым): ");
            name = Console.ReadLine();
            if (string.IsNullOrWhiteSpace(name))
                Console.WriteLine("Название блюда не может быть пустым.");
        } while (string.IsNullOrWhiteSpace(name));

        string composition;
        do
        {
            Console.Write("Введите состав блюда (не может быть пустым): ");
            composition = Console.ReadLine();
            if (string.IsNullOrWhiteSpace(composition))
                Console.WriteLine("Состав блюда не может быть пустым.");
        } while (string.IsNullOrWhiteSpace(composition));

        string weight;
        do
        {
            Console.Write("Введите вес блюда (формат: 100/20/50): ");
            weight = Console.ReadLine();
            if (!Dish.ValidateWeightFormat(weight))
                Console.WriteLine("Неверный формат веса. Ожидается формат: 100/20/50 (числа, разделенные слэшами).");
        } while (!Dish.ValidateWeightFormat(weight));

        double price;
        do
        {
            Console.Write("Введите цену блюда (положительное число): ");
            price = GetDoubleInput();
            if (price <= 0)
                Console.WriteLine("Цена должна быть положительным числом.");
        } while (price <= 0);

        Console.WriteLine("Выберите категорию:");
        var categories = Enum.GetValues(typeof(Category));
        for (int i = 0; i < categories.Length; i++)
        {
            Console.WriteLine($"{i}. {categories.GetValue(i)}");
        }
        int catIndex;
        do
        {
            Console.Write("Введите номер категории: ");
            catIndex = GetIntInput();
            if (catIndex < 0 || catIndex >= categories.Length)
                Console.WriteLine($"Номер должен быть от 0 до {categories.Length - 1}");
        } while (catIndex < 0 || catIndex >= categories.Length);
        Category category = (Category)categories.GetValue(catIndex);

        int cookingTime;
        do
        {
            Console.Write("Введите время готовки (в минутах, положительное число): ");
            cookingTime = GetIntInput();
            if (cookingTime <= 0)
                Console.WriteLine("Время готовки должно быть положительным числом.");
        } while (cookingTime <= 0);

        Console.Write("Введите типы блюда через запятую (например, острое,веганское): ");
        string typesInput = Console.ReadLine();
        string[] types = typesInput.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(t => t.Trim()).ToArray();

        // Проверка валидности ввода
        if (manager.ValidateDishInput(name, composition, weight, price, category, cookingTime, types, out string message))
        {
            Dish dish = new(name, composition, weight, price, category, cookingTime, types);
            manager.AddDish(dish);
            Console.WriteLine($"Блюдо добавлено успешно! Назначен ID: {dish.Id}");
        } else
        {
            Console.WriteLine($"Ошибка добавления блюда: {message}");
        }
    }

    static void EditDish()
    {
        Console.Write("Введите ID блюда для редактирования: ");
        int id = GetIntInput();

        var dish = manager.GetDishById(id);
        if (dish == null)
        {
            Console.WriteLine("Блюдо с таким ID не найдено.");
            return;
        }

        dish.PrintDishInfo();

        Console.WriteLine("Что вы хотите изменить?");
        Console.WriteLine("1. Название");
        Console.WriteLine("2. Состав");
        Console.WriteLine("3. Вес");
        Console.WriteLine("4. Цена");
        Console.WriteLine("5. Категория");
        Console.WriteLine("6. Время готовки");
        Console.WriteLine("7. Типы");
        Console.WriteLine("8. Всё сразу");
        Console.Write("Выберите: ");

        int choice = GetIntInput();

        try
        {
            switch (choice)
            {
                case 1:
                    string newName;
                    do
                    {
                        Console.Write("Введите новое название (не может быть пустым): ");
                        newName = Console.ReadLine();
                        if (string.IsNullOrWhiteSpace(newName))
                            Console.WriteLine("Название блюда не может быть пустым.");
                    } while (string.IsNullOrWhiteSpace(newName));
                    dish.EditDish(changeName: true, newName: newName);
                    break;
                case 2:
                    string newComposition;
                    do
                    {
                        Console.Write("Введите новый состав (не может быть пустым): ");
                        newComposition = Console.ReadLine();
                        if (string.IsNullOrWhiteSpace(newComposition))
                            Console.WriteLine("Состав блюда не может быть пустым.");
                    } while (string.IsNullOrWhiteSpace(newComposition));
                    dish.EditDish(changeComposition: true, newComposition: newComposition);
                    break;
                case 3:
                    string newWeight;
                    do
                    {
                        Console.Write("Введите новый вес (формат: 100/20/50): ");
                        newWeight = Console.ReadLine();
                        if (!Dish.ValidateWeightFormat(newWeight))
                            Console.WriteLine("Неверный формат веса. Ожидается формат: 100/20/50 (числа, разделенные слэшами).");
                    } while (!Dish.ValidateWeightFormat(newWeight));
                    dish.EditDish(changeWeight: true, newWeight: newWeight);
                    break;
                case 4:
                    double newPrice;
                    do
                    {
                        Console.Write("Введите новую цену (положительное число): ");
                        newPrice = GetDoubleInput();
                        if (newPrice <= 0)
                            Console.WriteLine("Цена должна быть положительным числом.");
                    } while (newPrice <= 0);
                    dish.EditDish(changePrice: true, newPrice: newPrice);
                    break;
                case 5:
                    Console.WriteLine("Выберите новую категорию:");
                    var categories = Enum.GetValues(typeof(Category));
                    for (int i = 0; i < categories.Length; i++)
                    {
                        Console.WriteLine($"{i}. {categories.GetValue(i)}");
                    }
                    int catIndex;
                    do
                    {
                        Console.Write("Введите номер категории: ");
                        catIndex = GetIntInput();
                        if (catIndex < 0 || catIndex >= categories.Length)
                            Console.WriteLine($"Номер должен быть от 0 до {categories.Length - 1}");
                    } while (catIndex < 0 || catIndex >= categories.Length);
                    Category newCategory = (Category)categories.GetValue(catIndex);
                    dish.EditDish(changeCategory: true, newCategory: newCategory);
                    break;
                case 6:
                    int newCookingTime;
                    do
                    {
                        Console.Write("Введите новое время готовки (положительное число): ");
                        newCookingTime = GetIntInput();
                        if (newCookingTime <= 0)
                            Console.WriteLine("Время готовки должно быть положительным числом.");
                    } while (newCookingTime <= 0);
                    dish.EditDish(changeCookingTime: true, newCookingTime: newCookingTime);
                    break;
                case 7:
                    Console.Write("Введите новые типы через запятую: ");
                    string typesInput = Console.ReadLine();
                    string[] newTypes = typesInput.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(t => t.Trim()).ToArray();
                    dish.EditDish(newType: newTypes);
                    break;
                case 8:
                    // Редактирование всех полей с проверками
                    string allName;
                    do
                    {
                        Console.Write("Введите новое название (не может быть пустым): ");
                        allName = Console.ReadLine();
                        if (string.IsNullOrWhiteSpace(allName))
                            Console.WriteLine("Название блюда не может быть пустым.");
                    } while (string.IsNullOrWhiteSpace(allName));

                    string allComposition;
                    do
                    {
                        Console.Write("Введите новый состав (не может быть пустым): ");
                        allComposition = Console.ReadLine();
                        if (string.IsNullOrWhiteSpace(allComposition))
                            Console.WriteLine("Состав блюда не может быть пустым.");
                    } while (string.IsNullOrWhiteSpace(allComposition));

                    string allWeight;
                    do
                    {
                        Console.Write("Введите новый вес (формат: 100/20/50): ");
                        allWeight = Console.ReadLine();
                        if (!Dish.ValidateWeightFormat(allWeight))
                            Console.WriteLine("Неверный формат веса. Ожидается формат: 100/20/50 (числа, разделенные слэшами).");
                    } while (!Dish.ValidateWeightFormat(allWeight));

                    double allPrice;
                    do
                    {
                        Console.Write("Введите новую цену (положительное число): ");
                        allPrice = GetDoubleInput();
                        if (allPrice <= 0)
                            Console.WriteLine("Цена должна быть положительным числом.");
                    } while (allPrice <= 0);

                    Console.WriteLine("Выберите новую категорию:");
                    categories = Enum.GetValues(typeof(Category));
                    for (int i = 0; i < categories.Length; i++)
                    {
                        Console.WriteLine($"{i}. {categories.GetValue(i)}");
                    }
                    int allCatIndex;
                    do
                    {
                        Console.Write("Введите номер категории: ");
                        allCatIndex = GetIntInput();
                        if (allCatIndex < 0 || allCatIndex >= categories.Length)
                            Console.WriteLine($"Номер должен быть от 0 до {categories.Length - 1}");
                    } while (allCatIndex < 0 || allCatIndex >= categories.Length);
                    Category allCategory = (Category)categories.GetValue(allCatIndex);

                    int allCookingTime;
                    do
                    {
                        Console.Write("Введите новое время готовки (положительное число): ");
                        allCookingTime = GetIntInput();
                        if (allCookingTime <= 0)
                            Console.WriteLine("Время готовки должно быть положительным числом.");
                    } while (allCookingTime <= 0);

                    Console.Write("Введите новые типы через запятую: ");
                    string allTypesInput = Console.ReadLine();
                    string[] allTypes = allTypesInput.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(t => t.Trim()).ToArray();

                    dish.EditDish(
                        changeName: true, newName: allName,
                        changeComposition: true, newComposition: allComposition,
                        changeWeight: true, newWeight: allWeight,
                        changePrice: true, newPrice: allPrice,
                        changeCategory: true, newCategory: allCategory,
                        changeCookingTime: true, newCookingTime: allCookingTime,
                        newType: allTypes
                    );
                    break;
                default:
                    Console.WriteLine("Неверный выбор.");
                    return;
            }

            Console.WriteLine("Блюдо успешно отредактировано!");
        }
        catch (ArgumentException ex)
        {
            Console.WriteLine($"Ошибка при редактировании: {ex.Message}");
        }
    }

    static void DeleteDish()
    {
        Console.Write("Введите ID блюда для удаления: ");
        int id = GetIntInput();

        var dish = manager.GetDishById(id);
        if (dish == null)
        {
            Console.WriteLine("Блюдо с таким ID не найдено.");
            return;
        }

        dish.PrintDishInfo();

        Console.Write("Вы уверены, что хотите удалить это блюдо? (y/n): ");
        var confirm = Console.ReadLine();

        if (confirm.Equals("y", StringComparison.OrdinalIgnoreCase) || confirm.Equals("yes", StringComparison.OrdinalIgnoreCase))
        {
            if (dish.DeleteDish(out bool success))
            {
                Console.WriteLine("Блюдо удалено успешно!");
            }
        }
        else
        {
            Console.WriteLine("Удаление отменено.");
        }
    }

    static void ViewDish()
    {
        Console.Write("Введите ID блюда для просмотра: ");
        int id = GetIntInput();

        var dish = manager.GetDishById(id);
        if (dish == null)
        {
            Console.WriteLine("Блюдо с таким ID не найдено.");
            return;
        }

        dish.PrintDishInfo();
    }

    static void AddOrder()
    {
        int tableId;
        do
        {
            Console.Write("Введите ID стола (положительное число): ");
            tableId = GetIntInput();
            if (tableId <= 0)
                Console.WriteLine("ID стола должно быть положительным числом.");
        } while (tableId <= 0);

        int waiterId;
        do
        {
            Console.Write("Введите ID официанта (положительное число): ");
            waiterId = GetIntInput();
            if (waiterId <= 0)
                Console.WriteLine("ID официанта должно быть положительным числом.");
        } while (waiterId <= 0);

        Console.Write("Введите комментарий (или Enter для пропуска): ");
        string comment = Console.ReadLine();

        var order = manager.CreateOrder(tableId, waiterId, comment ?? "");

        Console.WriteLine($"Заказ создан успешно! Назначен ID: {order.OrderId}");

        Console.WriteLine("Добавьте блюда в заказ:");
        Console.WriteLine("Доступные блюда:");
        manager.PrintMenu();

        bool addingDishes = true;
        while (addingDishes)
        {
            Console.Write("Введите ID блюда для добавления (или 0 для завершения): ");
            int dishId = GetIntInput();

            if (dishId == 0)
            {
                addingDishes = false;
            }
            else
            {
                var dish = manager.GetDishById(dishId);
                if (dish != null)
                {
                    order.AddDish(dish);
                    Console.WriteLine($"Блюдо {dish.Name} добавлено в заказ.");
                }
                else
                {
                    Console.WriteLine("Блюдо с таким ID не найдено.");
                }
            }
        }

        Console.WriteLine($"Заказ {order.OrderId} полностью сформирован!");
    }

    static void EditOrder()
    {
        Console.Write("Введите ID заказа для редактирования: ");
        int id = GetIntInput();

        var order = manager.GetOrderById(id);
        if (order == null)
        {
            Console.WriteLine("Заказ с таким ID не найден.");
            return;
        }

        order.PrintOrderInfo();

        Console.WriteLine("Что вы хотите изменить?");
        Console.WriteLine("1. ID стола");
        Console.WriteLine("2. Комментарий");
        Console.WriteLine("3. ID официанта");
        Console.WriteLine("4. Всё сразу");
        Console.Write("Выберите: ");

        int choice = GetIntInput();

        switch (choice)
        {
            case 1:
                Console.Write("Введите новый ID стола (положительное число): ");
                int newTableId;
                do
                {
                    newTableId = GetIntInput();
                    if (newTableId <= 0)
                        Console.WriteLine("ID стола должно быть положительным числом.");
                } while (newTableId <= 0);
                order.ChangeOrder(changeTableId: true, newTableId: newTableId);
                break;
            case 2:
                Console.Write("Введите новый комментарий: ");
                string newComment = Console.ReadLine();
                order.ChangeOrder(changeComment: true, newComment: newComment);
                break;
            case 3:
                Console.Write("Введите новый ID официанта (положительное число): ");
                int newWaiterId;
                do
                {
                    newWaiterId = GetIntInput();
                    if (newWaiterId <= 0)
                        Console.WriteLine("ID официанта должно быть положительным числом.");
                } while (newWaiterId <= 0);
                order.ChangeOrder(changeWaiterId: true, newWaiterId: newWaiterId);
                break;
            case 4:
                Console.Write("Введите новый ID стола (положительное число): ");
                int allTableId;
                do
                {
                    allTableId = GetIntInput();
                    if (allTableId <= 0)
                        Console.WriteLine("ID стола должно быть положительным числом.");
                } while (allTableId <= 0);

                Console.Write("Введите новый комментарий: ");
                string allComment = Console.ReadLine();

                Console.Write("Введите новый ID официанта (положительное число): ");
                int allWaiterId;
                do
                {
                    allWaiterId = GetIntInput();
                    if (allWaiterId <= 0)
                        Console.WriteLine("ID официанта должно быть положительным числом.");
                } while (allWaiterId <= 0);

                order.ChangeOrder(
                    changeTableId: true, newTableId: allTableId,
                    changeComment: true, newComment: allComment,
                    changeWaiterId: true, newWaiterId: allWaiterId
                );
                break;
            default:
                Console.WriteLine("Неверный выбор.");
                return;
        }

        Console.WriteLine("Заказ успешно отредактирован!");
    }

    static void CloseOrder()
    {
        Console.Write("Введите ID заказа для закрытия: ");
        int id = GetIntInput();

        var order = manager.GetOrderById(id);
        if (order == null)
        {
            Console.WriteLine("Заказ с таким ID не найден.");
            return;
        }

        if (order.IsClosed)
        {
            Console.WriteLine("Заказ уже закрыт.");
            return;
        }

        order.PrintOrderInfo();

        Console.Write("Вы уверены, что хотите закрыть этот заказ? (y/n): ");
        string confirm = Console.ReadLine();

        if (confirm.ToLower() == "y" || confirm.ToLower() == "yes")
        {
            order.CloseOrder();
            Console.WriteLine("Заказ закрыт успешно!");
        }
        else
        {
            Console.WriteLine("Закрытие заказа отменено.");
        }
    }

    static void ViewOrder()
    {
        Console.Write("Введите ID заказа для просмотра: ");
        int id = GetIntInput();

        var order = manager.GetOrderById(id);
        if (order == null)
        {
            Console.WriteLine("Заказ с таким ID не найден.");
            return;
        }

        order.PrintOrderInfo();
    }

    static void PrintOrderCheck()
    {
        Console.Write("Введите ID заказа для печати чека: ");
        int id = GetIntInput();

        var order = manager.GetOrderById(id);
        if (order == null)
        {
            Console.WriteLine("Заказ с таким ID не найден.");
            return;
        }

        order.PrintCheck();
    }

    static void ViewTotalRevenue()
    {
        double revenue = manager.CalculateTotalRevenue();
        Console.WriteLine($"Общая выручка: {revenue} руб.");
    }

    static void ViewWaiterStats()
    {
        Console.Write("Введите ID официанта: ");
        int waiterId = GetIntInput();

        int count = manager.GetWaiterClosedOrdersCount(waiterId);
        Console.WriteLine($"Количество закрытых заказов официанта {waiterId}: {count}");
    }
}