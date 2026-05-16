namespace Utils
{
    public static class Getters
    {
        public static int TryGetInt(string description)
        {
            return int.Parse(description);
        }

        public static uint TryGetUInt(string description)
        {
            uint result = 0;
            do
            {
                Console.Write($"Введите {description}: ");
                if (UInt32.TryParse(Console.ReadLine(), out result) && result != 0)
                {
                    return result;
                }
                else if (result < 0)
                {
                    Console.WriteLine("Число не может быть отрицательным");
                }
                else
                {
                    Console.WriteLine("Ошибка!");
                }
            } while (true);
        }
    }
}
