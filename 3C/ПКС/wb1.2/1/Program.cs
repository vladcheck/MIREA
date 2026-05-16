using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _1._2
{
    internal class Program
    {
        static bool IsWeekend(int day, int dayOfTheWeek)
        {
            int offset = (int)(-dayOfTheWeek); // Offset puts weekend closer, so it's negative

            bool isWeekday = false;
            if ((day == 7 + offset || day == 8 + offset) ||
                (day == 14 + offset || day == 15 + offset) ||
                (day == 21 + offset || day == 22 + offset) ||
                (day == 28 + offset || day == 29 + offset))
            {
                isWeekday = true;
            }
            bool isHoliday = day <= 5 && day >= 1 || day >= 8 && day <= 10;

            return isHoliday || isWeekday;
        }

        static void Main()
        {
            do
            {
                Console.Write("Введите номер дня недели, с которого начинается месяц (1-пн,...7-вс): ");
                if (!int.TryParse(Console.ReadLine(), out int dayOfTheWeek) || dayOfTheWeek <= 0 || dayOfTheWeek > 7)
                {
                    Console.WriteLine("Принимаются только числа от 1 до 7");
                    continue;
                }

                Console.Write("Введите день месяца: ");
                if (!int.TryParse(Console.ReadLine(), out int day) || day <= 0 || day > 31)
                {
                    Console.WriteLine("Принимаются только числа от 1 до 31");
                    continue;
                }

                else
                {
                    Console.WriteLine("-----Проверяем выходной ли день-----");
                    if (IsWeekend(day, dayOfTheWeek))
                    {
                        Console.WriteLine("Выходной день");
                    }
                    else
                    {
                        Console.WriteLine("Рабочий день");
                    }
                }
            } while (true);
        }
    }
}
