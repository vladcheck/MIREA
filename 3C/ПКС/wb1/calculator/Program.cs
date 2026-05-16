using System;

class Calculator
{
    static void PrintLogo()
    {
        Console.WriteLine(
            """
             $$$$$$\    $$\ $$\          $$$$$$\   $$$$$$\  $$\       $$$$$$\  
            $$  __$$\   $$ \$$ \        $$  __$$\ $$  __$$\ $$ |     $$  __$$\ 
            $$ /  \__|$$$$$$$$$$\       $$ /  \__|$$ /  $$ |$$ |     $$ /  \__|
            $$ |      \_$$  $$   |      $$ |      $$$$$$$$ |$$ |     $$ |      
            $$ |      $$$$$$$$$$\       $$ |      $$  __$$ |$$ |     $$ |      
            $$ |  $$\ \_$$  $$  _|      $$ |  $$\ $$ |  $$ |$$ |     $$ |  $$\ 
            \$$$$$$  |  $$ |$$ |        \$$$$$$  |$$ |  $$ |$$$$$$$$\\$$$$$$  |
             \______/   \__|\__|         \______/ \__|  \__|\________|\______/ 
            """
        );
    }

    static void PrintOperationInstructions(bool useMemory)
    {
        Console.WriteLine(
            $"""

                Введите число для выбора операции:
                (1) Сложить два числа (+)
                (2) Вычесть два числа (-)
                (3) Умножить два числа (*)
                (4) Разделить два числа (/)
                (5) Остаток от деления (%)
                (6) 1/x
                (7) Квадрат числа
                (8) Квадратный корень из числа
                (9) Сохранить число в память (M+)
                (10) Очистить память (M-)
                (11) Использовать число из памяти как первое входное число? ({((useMemory) ? "да" : "нет")})
                (12) Посмотреть память (MR)
                (13) Показать эту инструкцию снова
                (0) ВЫЙТИ ИЗ ПРОГРАММЫ

            """
        );
    }

    static double GetValidatedNumber()
    {
        const double maxAllowed = 1e12;
        const double minAllowed = -1e12;

        Console.Write("Введите число: ");
        string input = Console.ReadLine().Replace('.', ',');

        if (!double.TryParse(input, out double number))
        {
            Console.WriteLine("Ошибка: введено не число!");
            return double.NaN;
        }

        if (number <= minAllowed || number >= maxAllowed)
        {
            Console.WriteLine("Ошибка: число вне допустимого диапазона!");
            return double.NaN;
        }

        return number;
    }

    public static void Main()
    {
        double memory = 0;
        bool useMemory = false;
        PrintLogo();
        PrintOperationInstructions(useMemory);

        while (true)
        {
            Console.Write("\nВведите операцию: ");
            string input = Console.ReadLine();

            if (!short.TryParse(input, out short operation))
            {
                Console.WriteLine("Неизвестная операция");
                continue;
            }

            double a, b, result;
            switch (operation)
            {
                case 0:
                    return;

                case 1:
                case 2:
                case 3:
                case 4:
                case 5:
                    a = useMemory ? memory : GetValidatedNumber();
                    if (double.IsNaN(a)) break;
                    b = GetValidatedNumber();
                    if (double.IsNaN(b)) break;

                    if (operation == 4 && b == 0)
                    {
                        Console.WriteLine("Ошибка: деление на ноль!");
                        break;
                    }

                    if (operation == 5 && b == 0)
                    {
                        Console.WriteLine("Ошибка: деление на ноль!");
                        break;
                    }

                    result = operation switch
                    {
                        1 => a + b,
                        2 => a - b,
                        3 => a * b,
                        4 => a / b,
                        5 => a % b,
                        _ => 0
                    };
                    Console.WriteLine($"Итог: {result}");
                    break;

                case 6:
                case 7:
                case 8:
                    a = useMemory ? memory : GetValidatedNumber();
                    if (double.IsNaN(a)) break;

                    if (operation == 6 && a == 0)
                    {
                        Console.WriteLine("Ошибка: деление на ноль!");
                        break;
                    }

                    if (operation == 8 && a < 0)
                    {
                        Console.WriteLine("Ошибка: квадратный корень из отрицательного числа!");
                        break;
                    }

                    result = operation switch
                    {
                        6 => 1.0 / a,
                        7 => a * a,
                        8 => Math.Sqrt(a),
                        _ => 0
                    };
                    Console.WriteLine($"Итог: {result}");
                    break;

                case 9:
                    a = GetValidatedNumber();
                    if (!double.IsNaN(a)) memory = a;
                    break;

                case 10:
                    memory = 0;
                    Console.WriteLine("Память очищена");
                    break;

                case 11:
                    useMemory = !useMemory;
                    Console.WriteLine($"Использование памяти: {(useMemory ? "вкл" : "выкл")}");
                    break;

                case 12:
                    Console.WriteLine($"Память: {memory}");
                    break;

                case 13:
                    PrintOperationInstructions(useMemory);
                    break;

                default:
                    Console.WriteLine("Неизвестная операция");
                    break;
            }
        }
    }
}