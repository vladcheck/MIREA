using System;
using System.Collections.Generic;
using System.Text;
using System.Xml.Linq;

namespace restaurant
{
    public class Order(int tableId,string comment, int waiterId)
    {
        public int OrderId { get; private set; }
        public int TableId { get; set; } = tableId;
        public List<Dish> Dishes { get; set; } = [];
        public string Comment { get; set; } = comment;
        public DateTime OrderTime { get; set; } = DateTime.Now;
        public int WaiterId { get; set; } = waiterId;
        public DateTime? CloseTime { get; set; }
        public double TotalCost { get; private set; } = 0;
        public bool IsClosed { get; private set; } = false;

        public void SetOrderId(int id)
        {
            OrderId = id;
        }

        public void PrintOrderInfo()
        {
            string info = $"ID заказа: {OrderId}\n" +
                         $"ID стола: {TableId}\n" +
                         $"ID официанта: {WaiterId}\n" +
                         $"Время принятия заказа: {OrderTime}\n" +
                         $"Время закрытия заказа: {(CloseTime.HasValue ? CloseTime.Value.ToString() : "Не закрыт")}\n" +
                         $"Комментарий: {Comment}\n" +
                         "Блюда в заказе:\n";

            foreach (var dish in Dishes)
            {
                info += $" - {dish.Name} ({dish.Price} руб.)\n";
            }

            info += $"Итоговая стоимость: {TotalCost} руб.\n" +
                   $"Статус: {(IsClosed ? "Закрыт" : "Открыт")}\n\n";

            Console.Write(info);
        }

        public void AddDish(Dish dish)
        {
            this.Dishes.Add(dish);  
        }

        public void CloseOrder()
        {
            CloseTime = DateTime.Now;
            IsClosed = true;
        }
    }
}
