// Order.cs
using System;
using System.Collections.Generic;
using System.Linq;

namespace restaurant
{
    public class Order(int tableId, string comment, int waiterId)
    {
        public readonly int OrderId = _nextOrderId++;
        public int TableId { get; set; } = tableId;
        public string Comment { get; set; } = comment;
        public int WaiterId { get; set; } = waiterId;
        public DateTime OrderTime { get; } = DateTime.Now;
        public DateTime? CloseTime { get; private set; }
        public bool IsClosed { get; private set; } = false;
        public double TotalCost { get; private set; } = 0;

        private readonly List<Dish> _dishes = [];

        private static int _nextOrderId = 1;

        public IReadOnlyList<Dish> Dishes => _dishes.AsReadOnly();

        public void AddDish(Dish dish)
        {
            if (IsClosed)
                throw new InvalidOperationException("Нельзя добавлять блюда в закрытый заказ.");

            _dishes.Add(dish);
            TotalCost += dish.Price;
        }

        public void ChangeOrder(
            bool changeTableId = false, int newTableId = 0,
            bool changeComment = false, string newComment = "",
            bool changeWaiterId = false, int newWaiterId = 0)
        {
            if (IsClosed)
                throw new InvalidOperationException("Нельзя изменять закрытый заказ.");

            if (changeTableId && newTableId > 0)
                TableId = newTableId;

            if (changeComment)
                Comment = newComment;

            if (changeWaiterId && newWaiterId > 0)
                WaiterId = newWaiterId;
        }

        public void CloseOrder()
        {
            if (IsClosed)
                return;

            IsClosed = true;
            CloseTime = DateTime.Now;
        }

        public void PrintOrderInfo()
        {
            Console.WriteLine($"Заказ ID: {OrderId}");
            Console.WriteLine($"Столик: {TableId}");
            Console.WriteLine($"Официант ID: {WaiterId}");
            Console.WriteLine($"Комментарий: {Comment}");
            Console.WriteLine($"Время создания: {OrderTime:yyyy-MM-dd HH:mm:ss}");
            Console.WriteLine($"Статус: {(IsClosed ? $"Закрыт в {CloseTime:HH:mm:ss}" : "Открыт")}");
            Console.WriteLine($"Общая стоимость: {TotalCost:F2} руб.");

            Console.WriteLine("\nБлюда в заказе:");
            if (_dishes.Count == 0)
            {
                Console.WriteLine("Нет блюд");
            }
            else
            {
                foreach (var dish in _dishes)
                {
                    Console.WriteLine($"- {dish.Name} ({dish.Price:F2} руб.)");
                }
            }
            Console.WriteLine("------------------------");
        }

        public void PrintCheck()
        {
            if (!IsClosed)
            {
                Console.WriteLine("Чек можно распечатать только для закрытого заказа.");
                return;
            }

            Console.WriteLine("*************************************************");
            Console.WriteLine($"Столик: {TableId}");
            Console.WriteLine($"Официант: {WaiterId}");
            Console.WriteLine($"Период обслуживания: с {OrderTime:HH:mm:ss} по {CloseTime:HH:mm:ss}");
            Console.WriteLine();

            // Группируем блюда по категориям
            var groupedDishes = _dishes.GroupBy(d => d.Category);
            double grandTotal = 0;

            foreach (var categoryGroup in groupedDishes)
            {
                Console.WriteLine($"{categoryGroup.Key}:");

                // Группируем блюда внутри категории
                var dishCounts = categoryGroup.GroupBy(d => d.Name)
                    .Select(g => new {
                        Name = g.Key,
                        Dish = g.First(),
                        Count = g.Count(),
                        SubTotal = g.First().Price * g.Count()
                    }).ToList();

                foreach (var dishCount in dishCounts)
                {
                    Console.WriteLine($"  {dishCount.Name} {dishCount.Count}*{dishCount.Dish.Price:F2}={dishCount.SubTotal:F2}");
                }

                double categoryTotal = dishCounts.Sum(dc => dc.SubTotal);
                Console.WriteLine($"  Под_итог категории: {categoryTotal:F2}");
                Console.WriteLine();

                grandTotal += categoryTotal;
            }

            Console.WriteLine($"Итог счета: {grandTotal:F2}");
            Console.WriteLine("*************************************************");
        }
    }
}