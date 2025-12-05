using System;
using System.Collections.Generic;
using System.Text;



namespace restaurant
{
    public enum Category
    {
        Beverage,
        Salad,
        Cold,
        Hot,
        Soup,
        Desert
    }

    public class Dish(string name, string composition, string weight, double price, Category category, int cookingTime, params string[] type)
    {
        public int Id { get; private set; }
        public string Name { get; set; } = name;
        public string Composition { get; set; } = composition;
        public string Weight { get; set; } = weight;
        public double Price { get; set; } = price;
        public required Category Category { get; set; } = category;
        public required int CookingTime { get; set; } = cookingTime;
        public required string[] Type { get; set; } = type;

        public void EditDish(
            bool changeName = false, string? newName = null,
            bool changeComposition = false, string? newComposition = null,
            bool changeWeight = false, string? newWeight = null,
            bool changePrice = false, double newPrice = 0,
            bool changeCategory = false, Category newCategory = Category.Beverage,
            bool changeCookingTime = false, int newCookingTime = 0,
            params string[] newType)
        {
            if (changeName && !string.IsNullOrWhiteSpace(newName))
                Name = newName;

            if (changeComposition && !string.IsNullOrWhiteSpace(newComposition))
                Composition = newComposition;

            if (changeWeight && !string.IsNullOrWhiteSpace(newWeight))
            {
                if (ValidateWeightFormat(newWeight))
                    Weight = newWeight;
                else
                    throw new ArgumentException("Неверный формат веса. Ожидается формат: 100/20/50");
            }

            if (changePrice && newPrice > 0)
                Price = newPrice;

            if (changeCategory)
                Category = newCategory;

            if (changeCookingTime && newCookingTime > 0)
                CookingTime = newCookingTime;

            if (newType != null && newType.Length > 0)
                Type = newType;
        }

        public void SetId(int id)
        {
            Id = id;
        }

        public void PrintDishInfo()
        {
            string info = $"ID: {Id}\n" +
                         $"Название: {Name}\n" +
                         $"Состав: {Composition}\n" +
                         $"Вес: {Weight}\n" +
                         $"Цена: {Price}\n" +
                         $"Категория: {Category}\n" +
                         $"Время готовки: {CookingTime}\n" +
                         $"Тип: {string.Join(", ", Type)}\n\n";

            Console.Write(info);
        }

        public static bool DeleteDish(out bool success)
        {
            success = true;
            return success;
        }

        public static bool ValidateDish(in string name, in double price, out string message)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                message = "Название не может быть пустым";
                return false;
            }

            if (price <= 0)
            {
                message = "Цена должна быть положительной";
                return false;
            }

            message = "Блюдо валидно";
            return true;
        }

        public static bool ValidateWeightFormat(string weight)
        {
            // Проверяем формат веса: 100/20/50 или 200/30 и т.д.
            // Разрешены числа, разделенные слэшами
            if (string.IsNullOrWhiteSpace(weight))
                return false;

            string[] parts = weight.Split('/');
            foreach (string part in parts)
            {
                if (!int.TryParse(part.Trim(), out int value) || value <= 0)
                    return false;
            }

            return true;
        }
    }

    
}
