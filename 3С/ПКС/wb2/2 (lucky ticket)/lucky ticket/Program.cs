static int tryGetInt(string description = "число")
{
    int result = 0;
    do
    {
        Console.Write($"Введите {description}: ");
        if (Int32.TryParse(Console.ReadLine(), out result) && result != 0)
        {
            return result;
        }
        else if (result == 0)
        {
            Console.WriteLine("Число не может быть равным нулю");
        }
        else
        {
            Console.WriteLine("Ошибка!");
        }
    } while (true);
}


static int get_nth_digit(int num, int n)
{
    int len = ($"{num}").Length;
    int result = num % (int)Math.Pow(10,len-n) / (int)Math.Pow(10, len-n+1);
    Console.WriteLine(result);
    return result;
}

static void main()
{
    do
    {
        int ticket;
        do
        {
            ticket = tryGetInt("номер билета");
            if (ticket > 0 && ticket < 1_000_000) break;
        } while (true);

        int sum1 = 0, sum2 = 0;
        for (int i = 0; i < 6; i++)
        {
            if (i < 3)
            {
                sum1 += get_nth_digit(ticket, i);
            }
            else
            {
                sum2 += get_nth_digit(ticket, i);
            }
        }

        Console.WriteLine((bool)(sum2 == sum1));
    } while (true);
}

main();