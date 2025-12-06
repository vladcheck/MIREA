using System.Reflection.PortableExecutable;

namespace restaurant
{
    public class OrderSystemManager
    {
        public double TotalCost = 0;
        public List<Dish> Dishes = new List<Dish>();
        public List<Order> Orders = new List<Order>();

        public void PrintMenu()
        {
            foreach (var dish in this.Dishes)
            {
                dish.PrintDishInfo();
            }
        }

        public bool DeleteDish(int dishId)
        {
            var dishToRemove = Dishes.FirstOrDefault(d => d.Id == dishId);
            if (dishToRemove != null)
            {
                Dishes.Remove(dishToRemove);
                TotalCost -= dishToRemove.Price;
                return true;
            }
            return false;
        }

        public Order CreateOrder(int tableId, int waiterId, string comment)
        {
            Order order = new Order(tableId, comment, waiterId);
            this.Orders.Add(order);
            return order;
        }

        public int GetWaiterClosedOrdersCount(int waiterId)
        {
            return Orders.Count(order => order.WaiterId == waiterId && order.IsClosed);
        }

        public double CalculateTotalRevenue()
        {
            return Orders.Where(o => o.IsClosed).Sum(o => o.TotalCost);
        }

        public bool ValidateDishInput(string name, string composition, string weight, double price, Category category, int cookingTime, string[] types, out string message)
        {
            message = "";

            if (string.IsNullOrWhiteSpace(name))
            {
                message = "Название блюда не может быть пустым.";
                return false;
            }

            if (string.IsNullOrWhiteSpace(composition))
            {
                message = "Состав блюда не может быть пустым.";
                return false;
            }

            if (!Dish.ValidateWeightFormat(weight))
            {
                message = "Неверный формат веса. Ожидается формат: 100/20/50 (числа, разделенные слэшами).";
                return false;
            }

            if (price <= 0)
            {
                message = "Цена должна быть положительным числом.";
                return false;
            }

            if (cookingTime <= 0)
            {
                message = "Время готовки должно быть положительным числом.";
                return false;
            }

            return true;
        }

        public Dish? GetDishById(int id)
        {
            return Dishes.FirstOrDefault(d => d.Id == id);
        }

        public Order? GetOrderById(int id)
        {
            return Orders.FirstOrDefault(o => o.OrderId == id);
        }

        public void AddDish(params Dish[] dishes)
        {
            foreach (var dish in dishes)
            {
                Dishes.Add(dish);
                TotalCost += dish.Price;
            }
        }

        public void PrintDishStatistics()
        {
            Console.WriteLine("\n=== Статистика по проданным блюдам ===");

            // Получаем все закрытые заказы
            var closedOrders = Orders.Where(o => o.IsClosed).ToList();

            if (closedOrders.Count == 0)
            {
                Console.WriteLine("Нет закрытых заказов для анализа.");
                return;
            }

            // Собираем все проданные блюда из закрытых заказов
            var allSoldDishes = closedOrders
                .SelectMany(o => o.Dishes) // Нужно добавить этот метод в класс Order
                .ToList();

            if (allSoldDishes.Count == 0)
            {
                Console.WriteLine("Нет проданных блюд.");
                return;
            }

            // Группируем проданные блюда по названию
            var dishStats = allSoldDishes
                .GroupBy(d => d.Name)
                .Select(g => new {
                    Name = g.Key,
                    TotalCount = g.Count(), // Количество продаж этого блюда
                    TotalRevenue = g.Sum(d => d.Price), // Общая выручка от этого блюда
                    AveragePrice = g.Average(d => d.Price), // Средняя цена (обычно равна цене блюда)
                    Category = g.First().Category // Категория блюда
                })
                .OrderByDescending(s => s.TotalRevenue)
                .ToList();

            if (dishStats.Count == 0)
            {
                Console.WriteLine("Нет данных для статистики.");
                return;
            }

            var header = $"{"Блюдо",-15} | {"Кол-во",6} | {"Выручка",10} | {"Сред. цена",10} | {"Категория",12}";
            Console.WriteLine(header);
            Console.WriteLine(new string('-', header.Length));

            foreach (var stat in dishStats)
            {
                Console.WriteLine($"{stat.Name,-15} | {stat.TotalCount,6} | {stat.TotalRevenue,10:F2} | {stat.AveragePrice,10:F2} | {stat.Category,12}");
            }

            Console.WriteLine("\nОбщая статистика:");
            Console.WriteLine($"Всего продано блюд: {allSoldDishes.Count}");
            Console.WriteLine($"Уникальных блюд продано: {dishStats.Count}");
            Console.WriteLine($"Общая выручка от продаж: {allSoldDishes.Sum(d => d.Price):F2} руб.");

            // Топ-3 самых продаваемых блюд
            var top3 = dishStats.Take(3).ToList();
            Console.WriteLine("\nТоп-3 самых продаваемых блюд:");
            for (int i = 0; i < Math.Min(3, top3.Count); i++)
            {
                Console.WriteLine($"{i + 1}. {top3[i].Name} - {top3[i].TotalCount} продаж, выручка: {top3[i].TotalRevenue:F2} руб.");
            }
        }
    }
}