static decimal Factorial2(long x)
{
    if (x==0) return 1;

    decimal res = 1;
    for (long i = x; i > 0; i-=2)
    {
        res *= i;
    }
    return res;
}

static decimal nthValue(long x, uint n)
{
    if (n <= 1) return x;
    else {
        var nom = (decimal)Math.Pow(x, 2 * n - 1) * Factorial2(x);
        var denom = Factorial2(2 * n) * (2 * n + 1);
        return nthValue(x, n - 1) + (nom) / (denom);
    }
}

static void main()
{
    do
    {
        double e = 0;
        long x = 0;
        uint n = 0;

        do
        {
            Console.WriteLine("Введите точность (e < 0,01):");
            if (!Double.TryParse(Console.ReadLine(), out e) || e >= 0.01 || e <= 0) continue;
            else Console.WriteLine(e);

            Console.WriteLine("Введите первое число последовательности (x):");
            if (!Int64.TryParse(Console.ReadLine(), out x) || x == 0) continue;
            else Console.WriteLine(x);

            Console.WriteLine("Введите количество членов (n):");
            if (!UInt32.TryParse(Console.ReadLine(), out n) || n <= 0) continue;
            else Console.WriteLine(n);

            break;
        } while (true);

        Console.WriteLine($"Результат: {nthValue(x, n)}");

        Console.WriteLine("Продолжить?");
        if (Boolean.TryParse(Console.ReadLine(),out bool _) == false) break;
    } while (true);
}

main();