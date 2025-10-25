static uint tryGetUInt(string description = "число")
{
    uint result = 0;
    do
    {
        Console.Write($"Введите {description}: ");
        if (UInt32.TryParse(Console.ReadLine(), out result) && result != 0)
        {
            return result;
        }
        else
        {
            Console.WriteLine("Введите число!");
        }
    } while (true);
}

static void printResults(uint totalWater, uint totalMilk, uint americanoCount, uint latteCount, uint cash)
{
    Console.WriteLine("\n*** Отчёт ***");
    Console.WriteLine("Ингредиентов осталось:");
    Console.WriteLine($"Вода: {totalWater} мл");
    Console.WriteLine($"Молоко: {totalMilk} мл");
    Console.WriteLine($"Кружек американо приготовлено: {americanoCount}");
    Console.WriteLine($"Кружек латте приготовлено: {latteCount}");
    Console.WriteLine($"Итого: {cash} рублей.");
}

static void main()
{
    do
    {
        uint totalWater = tryGetUInt("количество воды (мл)");
        uint totalMilk = tryGetUInt("количество молока (мл)");

        uint americanoCount = 0;
        uint latteCount = 0;
        uint cash = 0;

        while (true)
        {
            Console.Write("Выберите напиток (1 — американо, 2 — латте): ");
            string? choice = Console.ReadLine();

            if (string.IsNullOrEmpty(choice))
            {
                Console.WriteLine("Неверный выбор!");
                continue;
            }

            if (choice == "1")
            {
                if (totalWater >= 300)
                {
                    totalWater -= 300;
                    americanoCount++;
                    cash += 150;
                    Console.WriteLine("Ваш напиток готов.");
                }
                else
                {
                    Console.WriteLine("Недостаточно воды для приготовления американо.");
                    break;
                }
            }
            else if (choice == "2")
            {
                if (totalWater >= 30 && totalMilk >= 270)
                {
                    totalWater -= 30;
                    totalMilk -= 270;
                    latteCount++;
                    cash += 170;
                    Console.WriteLine("Ваш напиток готов.");
                }
                else
                {
                    Console.WriteLine("Недостаточно ингредиентов для приготовления латте.");
                    break;
                }
            }
            else
            {
                Console.WriteLine("Неверный выбор!");
                continue;
            }

            if (totalWater < 300 || (totalWater < 30 && totalMilk < 270))
            {
                break;
            }
        }

        printResults(totalWater, totalMilk, americanoCount, latteCount, cash);
    } while (true);
}

main();