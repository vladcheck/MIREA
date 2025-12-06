namespace restaurant
{
    public enum Category
    {
        Soup,
        Salad,
        MainCourse,
        Dessert,
        Beverage,
        Appetizer
    }

    public class Dish
    {
        public readonly int Id;
        public string Name { get; private set; }
        public string Composition { get; private set; }
        public string Weight { get; private set; }
        public double Price { get; private set; }
        public Category Category { get; private set; }
        public int CookingTime { get; private set; }
        public string[] Type { get; private set; }

        private static int _nextId = 1;

        public Dish(string name, string composition, string weight, double price, Category category, int cookingTime, string[] type)
        {
            Id = _nextId++;
            Name = name;
            Composition = composition;
            Weight = weight;
            Price = price;
            Category = category;
            CookingTime = cookingTime;
            Type = type ?? Array.Empty<string>();
        }

        public static bool ValidateWeightFormat(string weight)
        {
            if (string.IsNullOrWhiteSpace(weight))
                return false;

            var parts = weight.Split('/');
            foreach (var part in parts)
            {
                if (!int.TryParse(part, out int value) || value <= 0)
                    return false;
            }
            return true;
        }

        public void EditDish(
            bool changeName = false, string? newName = null,
            bool changeComposition = false, string? newComposition = null,
            bool changeWeight = false, string? newWeight = null,
            bool changePrice = false, double newPrice = 0,
            bool changeCategory = false, Category newCategory = default,
            bool changeCookingTime = false, int newCookingTime = 0,
            bool changeType = false, string[]? newType = null)
        {
            if (changeName && !string.IsNullOrWhiteSpace(newName))
                Name = newName;

            if (changeComposition && !string.IsNullOrWhiteSpace(newComposition))
                Composition = newComposition;

            if (changeWeight && ValidateWeightFormat(newWeight ?? ""))
                Weight = newWeight;

            if (changePrice && newPrice > 0)
                Price = newPrice;

            if (changeCategory)
                Category = newCategory;

            if (changeCookingTime && newCookingTime > 0)
                CookingTime = newCookingTime;

            if (changeType && newType != null)
                Type = newType;
        }

        public void PrintDishInfo()
        {
            Console.WriteLine($"ID: {Id}");
            Console.WriteLine($"Название: {Name}");
            Console.WriteLine($"Состав: {Composition}");
            Console.WriteLine($"Вес: {Weight}");
            Console.WriteLine($"Цена: {Price:F2} руб.");
            Console.WriteLine($"Категория: {Category}");
            Console.WriteLine($"Время готовки: {CookingTime} мин.");
            Console.WriteLine($"Типы: {string.Join(", ", Type)}");
            Console.WriteLine("------------------------");
        }
    }
}