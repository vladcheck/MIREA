static int tryGetInt(string description = "число")
{
    int result = 0;
    do
    {
        Console.Write($"Введите {description}: ");
        if (Int32.TryParse(Console.ReadLine(), out result))
        {
            return result;
        } else
        {
            Console.WriteLine("Ошибка!");
        }
    } while (true);
}

static void ReduceFraction(int num, int denom, out int reducedNumerator, out int reducedDenominator)
{
    if (num < 0 && denom < 0)
    {
        num = -num;
        denom = -denom;
    }
    else if (denom < 0)
    {
        num = -num;
        denom = -denom;
    }

    int gcd = FindGCD(Math.Abs(num), Math.Abs(denom));

    reducedNumerator = num / gcd;
    reducedDenominator = denom / gcd;
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
        int num = tryGetInt("числитель");
        int denom = tryGetInt("знаменатель");

        if (denom == 0)
        {
            Console.WriteLine("Ошибка! Знаменатель не может быть равен 0.");
            return;
        }

        int reducedNumerator;
        int reducedDenominator;

        ReduceFraction(num, denom, out reducedNumerator, out reducedDenominator);

        if (reducedDenominator != 1)
        {
            Console.WriteLine($"Результат: {reducedNumerator} / {reducedDenominator}");
        } else
        {
            Console.WriteLine($"Результат: {reducedNumerator}");
        }
    } while (true);
}

main();