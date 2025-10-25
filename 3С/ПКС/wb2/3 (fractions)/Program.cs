using System.Reflection.Metadata.Ecma335;

static int tryGetInt(string description = "число")
{
    int result = 0;
    do
    {
        Console.Write($"Введите {description}: ");
        if (Int32.TryParse(Console.ReadLine(), out result) && result != 0)
        {
            return result;
        } else if (result == 0)
        {
            Console.WriteLine("Число не может быть равным нулю");
        } else
        {
            Console.WriteLine("Ошибка!");
        }
    } while (true);
}

static void ReduceFraction(int numerator, int denominator, out int reducedNumerator, out int reducedDenominator)
{
    if (numerator < 0 && denominator < 0)
    {
        numerator = -numerator;
        denominator = -denominator;
    }
    else if (denominator < 0)
    {
        numerator = -numerator;
        denominator = -denominator;
    }

    int gcd = FindGCD(Math.Abs(numerator), Math.Abs(denominator));

    reducedNumerator = numerator / gcd;
    reducedDenominator = denominator / gcd;
}

// НОД
static int FindGCD(int a, int b)
{
    // Алгоритм Евклида
    while (b != 0)
    {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

static void main()
{
    do
    {
        int numerator = tryGetInt("числитель");
        int denominator = tryGetInt("знаменатель");

        if (denominator == 0)
        {
            Console.WriteLine("Ошибка! Знаменатель не может быть равен 0.");
            return;
        }

        int reducedNumerator;
        int reducedDenominator;

        ReduceFraction(numerator, denominator, out reducedNumerator, out reducedDenominator);

        Console.WriteLine($"Результат: {reducedNumerator} / {reducedDenominator}");
    } while (true);
}

main();