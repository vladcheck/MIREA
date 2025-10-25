static long getLong(string message)
{
    while (true)
    {
        Console.Write(message);
        string? input = Console.ReadLine();

        if (string.IsNullOrEmpty(input))
        {
            Console.WriteLine("Ошибка! Введите число.");
            continue;
        }

        if (long.TryParse(input, out long result) && result >= 0)
        {
            return result;
        }
        else
        {
            Console.WriteLine("Ошибка! Введите корректное положительное число.");
        }
    }
}

static bool Check(long d, long n, long a, long b, long w, long h)
{
    // Первая ориентация: a - ширина, b - высота
    long cols1 = w / (a + 2 * d);
    long rows1 = h / (b + 2 * d);
    long total1 = cols1 * rows1;

    // Вторая ориентация: b - ширина, a - высота
    long cols2 = w / (b + 2 * d);
    long rows2 = h / (a + 2 * d);
    long total2 = cols2 * rows2;

    return total1 >= n || total2 >= n;
}


static void main()
{
    do
    {
        long n = getLong("Введите количество модулей (n): ");
        long a = getLong("Введите ширину модуля в метрах (a): ");
        long b = getLong("Введите длину модуля в метрах (b): ");
        long w = getLong("Введите ширину поля для модулей в метрах (w): ");
        long h = getLong("Введите длину поля для модулей в метрах (h): ");

        long low = 0;
        long high = Math.Max(w, h) + 1;
        long answer = 0;

        while (low <= high)
        {
            long d = low + (high - low) / 2;

            if (Check(d, n, a, b, w, h))
            {
                answer = d;
                low = d + 1;
            }
            else
            {
                high = d - 1;
            }
        }

        Console.WriteLine($"Ответ d = {answer}м");
        Console.WriteLine();
    } while (true);
}

main();