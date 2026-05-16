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


static void printResult(uint bacteriaCount)
{
    if (bacteriaCount <= 0)
    {
        Console.WriteLine("Антибиотик победил!");
    }
    else
    {
        Console.WriteLine("Антибиотик проиграл! Бактерии выжили.");
    }
}

static void main()
{
    do
    {
        uint bacteriaCount = tryGetUInt("количество бактерий");
        uint antibioticDrops = tryGetUInt("количество антибиотика (в каплях)");
        uint hour = 0;
        uint antibioticStrength = 10 * antibioticDrops;

        // Симуляция процесса
        while (bacteriaCount > 0 && antibioticStrength > 0)
        {
            hour++;
            bacteriaCount *= 2;

            if (antibioticStrength > bacteriaCount)
            {
                break; // Завершаем цикл, если бактерий не осталось
            }
            else
            {
                bacteriaCount -= antibioticStrength;
                antibioticStrength--;
                Console.WriteLine($"После {hour} часа бактерий осталось {bacteriaCount}");
            }
        }

        printResult(bacteriaCount);
    } while (true);
}

main();