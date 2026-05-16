
class Program
{
    static private readonly Dictionary<int, Dictionary<int, int>> memo = [];
    static void Main()
    {
        while (true)
        {
            int m = GetValidNumber("m", 3); // Эмпирически, при m > 3 программа всегда достигает stack overflow
            int n = GetValidNumber("n", 5); // Эмпирически, при n > 5 программа всегда достигает stack overflow

            Console.WriteLine($"Ввод: m={m} n={n}");

            int result = Ackermann(m, n);

            Console.WriteLine($"Вывод: A(m,n)={result}");
        }
    }
    static int GetValidNumber(string paramName, int limit)
    {
        while (true)
        {
            Console.Write($"Введите целое неотрицательное число {paramName}, не большее {limit}: ");
            string? input = Console.ReadLine();

            if (!string.IsNullOrEmpty(input) && int.TryParse(input, out int number) && number >= 0)
            {
                if (number > limit)
                {
                    Console.WriteLine($"Число слишком большое, введите число, не большее {limit}");
                } else
                {
                    return number;
                }
            }
            else
            {
                Console.WriteLine("Ошибка: введено невалидное значение.");
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

