using System;

class Program
{
    static void Main()
    {
        long n = GetValidNumber();
        long reversed = ReverseNumber(n);
        Console.WriteLine($"Вывод: {reversed}");
    }

    static long GetValidNumber()
    {
        while (true)
        {
            Console.Write("Введите целое число: ");
            string? input = Console.ReadLine();

            if (!string.IsNullOrEmpty(input) && long.TryParse(input, out long number))
            {
                return number;
            }
            else
            {
                Console.WriteLine("Ошибка: введено невалидное значение. Попробуйте снова.");
            }
        }
    }

    static long ReverseNumber(long n)
    {
        if (n < 0)
        {
            return -ReverseNumber(-n);
        }
        return ReverseHelper(n, 0);
    }

    static long ReverseHelper(long n, long reversed)
    {
        if (n == 0)
        {
            return reversed;
        }
        long lastDigit = n % 10;
        long newReversed = reversed * 10 + lastDigit;
        long remaining = n / 10;
        return ReverseHelper(remaining, newReversed);
    }
}