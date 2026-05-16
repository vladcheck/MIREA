static void PlayGame()
{
    int low = 0;
    int high = 63;
    int questions = 0;
    const uint MAX_QUESTIONS = 7;

    Console.WriteLine("Загадайте число от 0 до 63, а я попробую его угадать!");
    Console.WriteLine("Отвечайте на вопросы: 'да' или 'нет'");
    Console.WriteLine();

    while (low < high && questions <= MAX_QUESTIONS)
    {
        int mid = (low + high) / 2;
        questions++;

        Console.Write($"({questions}) Ваше число больше {mid}? (да/нет): ");
        string? input = Console.ReadLine()?.ToLowerInvariant().Trim();

        if (string.IsNullOrEmpty(input))
        {
            Console.WriteLine("Пожалуйста, введите 'да' или 'нет'");
            questions--; // Question wasted
            continue;
        }

        if (input == "да" || input == "д" || input == "yes" || input == "y")
        {
            // Число больше mid, ищем в правой половине
            low = mid + 1;
        }
        else if (input == "нет" || input == "н" || input == "no" || input == "n")
        {
            // Число меньше или равно mid, ищем в левой половине
            high = mid;
        }
        else
        {
            Console.WriteLine("Пожалуйста, введите 'да' или 'нет'");
            questions--; // Question wasted
        }
    }

    if (low >= high)
    {
        Console.WriteLine();
        Console.WriteLine($"Ваше число: {low}");
    }
    else if (questions > MAX_QUESTIONS)
    {
        Console.WriteLine("Я проиграл! Не смог угадать ваше число.");
    }
}

static void main()
{
    while (true)
    {
        PlayGame();
    }
}

main();