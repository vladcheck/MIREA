using System;

class Program
{
    static void Main()
    {
        var manager = new Manager();
        Console.WriteLine("=== СИСТЕМА БРОНИРОВАНИЯ ===\n");

        while (true)
        {
            PrintMenu();
            Console.Write("Ваш выбор (1-5): ");
            string? input = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(input)) continue;

            switch (input)
            {
                case "1": CreateTables(manager); break;
                case "2": CreateBookings(manager); break;
                case "3": EditTable(manager); break;
                case "4": ShowTable(manager); break;
                case "5": Console.WriteLine("\nВыход из программы."); return;
                default: Console.WriteLine("Ошибка: выберите от 1 до 5.\n"); break;
            }
        }
    }

    static void PrintMenu()
    {
        Console.WriteLine("Что вы хотите сделать:");
        Console.WriteLine("1. Создать столы");
        Console.WriteLine("2. Создать бронирования");
        Console.WriteLine("3. Редактировать стол по ID");
        Console.WriteLine("4. Показать информацию о столе");
        Console.WriteLine("5. Выход\n");
    }

    static void CreateTables(Manager manager)
    {
        int n = 0;
        while (n <= 0)
        {
            Console.Write("\nСколько столов создать? (n > 0): ");
            if (!int.TryParse(Console.ReadLine(), out n) || n <= 0)
                Console.WriteLine("Ошибка: введите число больше 0.");
        }

        for (int i = 0; i < n; i++)
        {
            Console.WriteLine($"\n--- Стол {i + 1} из {n} ---");

            int id = 0;
            string? location = null;
            int seats = 0;

            while (id <= 0 || manager.Tables.Exists(t => t.Id == id))
            {
                Console.Write("ID (целое положительное число): ");
                if (!int.TryParse(Console.ReadLine(), out id) || id <= 0)
                {
                    Console.WriteLine("Ошибка: ID должен быть положительным числом.");
                    continue;
                }
                if (manager.Tables.Exists(t => t.Id == id))
                {
                    Console.WriteLine("Ошибка: стол с таким ID уже существует.");
                    id = 0;
                }
            }

            while (string.IsNullOrWhiteSpace(location))
            {
                Console.Write("Расположение (не может быть пустым): ");
                location = Console.ReadLine();
                if (string.IsNullOrWhiteSpace(location))
                    Console.WriteLine("Ошибка: расположение не может быть пустым.");
            }

            while (seats <= 0)
            {
                Console.Write("Количество мест (целое число > 0): ");
                if (!int.TryParse(Console.ReadLine(), out seats) || seats <= 0)
                    Console.WriteLine("Ошибка: количество мест должно быть больше 0.");
            }

            manager.AddTable(id, location, seats);
            Console.WriteLine($"Стол {id} создан: {location}, {seats} мест.\n");
        }

        Console.WriteLine($"Готово: создано {n} столов.\n");
    }

    static void CreateBookings(Manager manager)
    {
        if (manager.Tables.Count == 0)
        {
            Console.WriteLine("\nСначала создайте столы!\n");
            return;
        }

        int n = 0;
        while (n <= 0)
        {
            Console.Write("\nСколько бронирований создать? (n > 0): ");
            if (!int.TryParse(Console.ReadLine(), out n) || n <= 0)
                Console.WriteLine("Ошибка: введите число > 0.");
        }

        for (int i = 0; i < n; i++)
        {
            Console.WriteLine($"\n--- Бронирование {i + 1} из {n} ---");

            string? name = null, phone = null, time = null, comment = null;
            Table? selectedTable = null;

            while (string.IsNullOrWhiteSpace(name))
            {
                Console.Write("Имя: ");
                name = Console.ReadLine();
                if (string.IsNullOrWhiteSpace(name)) name = "Гость";
            }

            while (string.IsNullOrWhiteSpace(phone))
            {
                Console.Write("Телефон: ");
                phone = Console.ReadLine();
                if (string.IsNullOrWhiteSpace(phone)) phone = "не указан";
            }

            while (true)
            {
                Console.Write("Время (например, 12:00-13:00): ");
                time = Console.ReadLine();

                if (string.IsNullOrWhiteSpace(time))
                {
                    Console.WriteLine("Время не может быть пустым.");
                    continue;
                }

                bool validTime = manager.Tables.Any(t => t.Schedule.ContainsKey(time));
                if (!validTime)
                {
                    Console.WriteLine("Неверное время. Доступно: 09:00-10:00 ... 17:00-18:00");
                    continue;
                }

                var freeTables = manager.Tables.Where(t => t.Schedule[time] == null).ToList();
                if (!freeTables.Any())
                {
                    Console.WriteLine("На это время нет свободных столов. Выберите другое.");
                    continue;
                }

                Console.WriteLine("Свободные столы:");
                foreach (var t in freeTables)
                    Console.WriteLine($"  Стол {t.Id}: {t.Location}, {t.Seats} мест");

                Console.Write("Выберите ID стола: ");
                if (!int.TryParse(Console.ReadLine(), out int tableId))
                {
                    Console.WriteLine("Неверный ID. Повторите.");
                    continue;
                }

                selectedTable = freeTables.Find(t => t.Id == tableId);
                if (selectedTable == null)
                {
                    Console.WriteLine("Стол занят или не существует. Выберите из списка.");
                    continue;
                }

                break;
            }

            Console.Write("Комментарий (Enter — пусто): ");
            comment = Console.ReadLine() ?? "";

            var booking = manager.Book(name, phone, time!, comment, selectedTable!);
            if (booking != null)
                Console.WriteLine($"Бронирование создано! ID клиента: {booking.ClientId}\n");
            else
                Console.WriteLine("Ошибка при создании.\n");
        }

        Console.WriteLine($"Готово: создано {n} бронирований.\n");
    }

    static void EditTable(Manager manager)
    {
        Console.Write("\nID стола для редактирования: ");
        if (!int.TryParse(Console.ReadLine(), out int id))
        {
            Console.WriteLine("Неверный ID.\n");
            return;
        }

        var table = manager.Tables.Find(t => t.Id == id);
        if (table == null)
        {
            Console.WriteLine("Стол не найден.\n");
            return;
        }

        if (!table.CanEdit())
        {
            Console.WriteLine("Нельзя редактировать: есть брони.\n");
            return;
        }

        Console.WriteLine($"Текущие: {table.Location}, {table.Seats} мест");
        Console.Write("Новое расположение (Enter — не менять): ");
        string? newLoc = Console.ReadLine();
        Console.Write("Новое кол-во мест (Enter — не менять): ");
        string? seatsStr = Console.ReadLine();

        string loc = string.IsNullOrWhiteSpace(newLoc) ? table.Location : newLoc;
        int seats = string.IsNullOrWhiteSpace(seatsStr) ? table.Seats : int.Parse(seatsStr);

        manager.EditTable(id, loc, seats);
        Console.WriteLine("Стол обновлён.\n");
    }

    static void ShowTable(Manager manager)
    {
        Console.Write("\nID стола: ");
        if (!int.TryParse(Console.ReadLine(), out int id))
        {
            Console.WriteLine("Неверный ID.\n");
            return;
        }

        Console.WriteLine();
        manager.ShowTable(id);
        Console.WriteLine();
    }
}