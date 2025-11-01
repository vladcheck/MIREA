using System;

class Program
{
    static void Main()
    {
        int m = GetValidNumber("m");
        int n = GetValidNumber("n");

        Console.WriteLine($"Ввод: m={m} n={n}");

        int result = Ackermann(m, n);

        Console.WriteLine($"Вывод: A(m,n)={result}");
    }
    static int GetValidNumber(string paramName)
    {
        while (true)
        {
            Console.Write($"Введите целое неотрицательное число {paramName}: ");
            string? input = Console.ReadLine();

            if (!string.IsNullOrEmpty(input) && int.TryParse(input, out int number) && number >= 0)
            {
                return number;
            }
            else
            {
                Console.WriteLine("Ошибка: введено невалидное значение. Введите неотрицательное целое число.");
            }
        }
    }
    static int Ackermann(int m, int n)
    {
        if (m == 0)
        {
            return n + 1;
        }
        else if (m > 0 && n == 0)
        {
            return Ackermann(m - 1, 1);
        }
        else
        {
            return Ackermann(m - 1, Ackermann(m, n - 1));
        }
    }
}