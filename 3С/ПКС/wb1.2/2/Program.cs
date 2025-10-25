void PrintCountOfBucks(long sum)
{
    if (sum <= 0)
    {
        Console.WriteLine($"Выдать {sum} рублей невозможно.");
        return;
    }
    if (sum % 100 != 0)
    {
        Console.WriteLine($"Выдать {sum} рублей невозможно - сумма не кратна стам.");
        return;
    }

    long cycles = sum / 150000; // Can't give more than 150000 at once
    sum -= cycles * 150000;

    long fiveThousand = sum / 5000 + cycles * 30;
    sum %= 5000;

    long oneThousand = sum / 1000;
    sum %= 1000;

    long fiveHundred = sum / 500;
    sum %= 500;

    long twoHundred = sum / 200;
    sum %= 200;

    long oneHundred = sum / 100;

    Console.WriteLine($"""
        Количество прогонов по 150к: {cycles}
        5000: {fiveThousand}
        1000: {oneThousand}
        500: {fiveHundred}
        200: {twoHundred}
        100: {oneHundred}
    """);
}

do
{
    Console.Write("Введите вашу сумму: ");
    long sum = Convert.ToInt64(Console.ReadLine());
    PrintCountOfBucks(sum);

    Console.Write("Продолжить работу? (y/n) ");
    char isContinue = Convert.ToChar(Console.ReadLine());
    if (isContinue == 'n') break;
} while (true);