namespace wb3._2
{
    internal class Getters
    {
        public static int TryGetInt(string description = "число")
        {
            do
            {
                Console.Write($"Введите {description}: ");
                if (Int32.TryParse(Console.ReadLine(), out int result))
                {
                    return result;
                }
                else
                {
                    Console.WriteLine("Ошибка!");
                }
            } while (true);
        }
        public static int TryGetPositiveInt(string description = "число")
        {
            do
            {
                Console.Write($"Введите {description}: ");
                if (Int32.TryParse(Console.ReadLine(), out int result))
                {
                    if (result <= 0)
                    {
                        Console.WriteLine("Число не может быть <= 0");
                    }
                    else
                    {
                        return result;
                    }
                }
                else
                {
                    Console.WriteLine("Ошибка!");
                }
            } while (true);
        }

        public static string? TryGetString(string description = "строку")
        {
            Console.Write($"Введите {description}: ");
            return Console.ReadLine();
        }

        public static string TryGetNonEmptyString(string description = "строку")
        {
            do
            {
                Console.Write($"Введите {description}: ");
                string? result = Console.ReadLine();
                if (String.IsNullOrEmpty(result) || String.IsNullOrWhiteSpace(result))
                {
                    Console.WriteLine("Строка не может быть пустой");
                }
                else
                {
                    return result;
                }
            } while (true);
        }
    }
}
