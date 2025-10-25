using Utils;

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
        uint bacteriaCount = Getters.tryGetUInt("количество бактерий");
        uint antibioticDrops = Getters.tryGetUInt("количество антибиотика (в каплях)");
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