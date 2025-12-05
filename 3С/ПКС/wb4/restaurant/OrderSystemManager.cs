using restaurant;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Linq;

namespace restaurant
{
    public class OrderSystemManager
    {
        public double TotalCost = 0;
        public List<Dish> Dishes = [];
        public List<Order> Orders = [];

        public void PrintMenu()
        {
            foreach (var dish in this.Dishes)
            {
                dish.PrintDishInfo();
            }
        }
        public Order CreateOrder(int tableId, int waiterId, string comment)
        {
            Order order = new(tableId, comment, waiterId);
            this.Orders.Add(order);
            return order;
        }

        public bool ValidateDishInput(string name)
        {

        }
        public Dish? GetDishById(int id)  {
            foreach (var dish in Dishes)
            {
                if (dish.Id == id)
                {
                    return dish;
                }
            }
            return null;
        }

        public Order? GetOrderById(int id)
        {
            foreach (var order in Orders)
            {
                if (order.OrderId == id)
                {
                    return order;
                }
            }
            return null;
        }

        public void AddDish(params Dish[] dishes)
        {
            foreach (var dish in dishes)
            {
                Dishes.Add(dish);
                TotalCost += dish.Price;
            }
        }

        public static void ChangeOrder(
            Order order,
            bool changeTableId = false, int newTableId = 0,
            bool changeComment = false, string? newComment = null,
            bool changeWaiterId = false, int newWaiterId = 0)
        {
            if (changeTableId && newTableId > 0)
                order.TableId = newTableId;

            if (changeComment)
                order.Comment = newComment;

            if (changeWaiterId && newWaiterId > 0)
                order.WaiterId = newWaiterId;
        }

        public void PrintCheck(Order order)
        {
            if (!order.IsClosed)
            {
                Console.WriteLine("Чек можно распечатать только для закрытого заказа.");
                return;
            }

            string check = "*************************************************\n" +
                          $"Столик: {order.TableId}\n" +
                          $"Официант: {order.WaiterId}\n" +
                          $"Период обслуживания: с {order.OrderTime:HH:mm:ss} по {order.CloseTime:HH:mm:ss}\n\n";

            // Группируем блюда по категориям
            var groupedDishes = Dishes.GroupBy(d => d.Category);
            double grandTotal = 0;

            foreach (var categoryGroup in groupedDishes)
            {
                check += $"{categoryGroup.Key}:\n";

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
                    check += $"  {dishCount.Name} {dishCount.Count}*{dishCount.Dish.Price}={dishCount.SubTotal}\n";
                }

                double categoryTotal = (double)dishCounts.Sum(static dc => dc.SubTotal);
                check += $"  Под_итог категории: {categoryTotal}\n\n";

                grandTotal += categoryTotal;
            }

            check += $"Итог счета: {grandTotal}\n" +
                    "*************************************************\n";

            Console.Write(check);
        }
    }
}