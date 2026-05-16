using wb3._2;

class Program
{
    static void Main()
    {
        var manager = new Manager();
        Console.WriteLine("=== СИСТЕМА БРОНИРОВАНИЯ ===\n");

        while (true)
        {
            PrintMenu();
            int input = Getters.TryGetInt("выбор (0-7)");

            switch (input)
            {
                case 0: Console.WriteLine("\nВыход из программы."); return;
                case 1: CreateTables(manager); break;
                case 2: CreateBookings(manager); break;
                case 3: EditTable(manager); break;
                case 4: ShowTable(manager); break;
                case 5: manager.ShowAllBookings(); break;
                case 6: SearchBooking(manager); break;
                case 7: ShowFreeTablesByFilter(manager); break;
                default: Console.WriteLine("Ошибка: введите число от 0 до 7.\n"); break;
            }
        }
    }

    static void PrintMenu()
    {
        Console.WriteLine("Что вы хотите сделать:");
        Console.WriteLine("0. Выход");
        Console.WriteLine("1. Создать столы");
        Console.WriteLine("2. Создать бронирования");
        Console.WriteLine("3. Редактировать стол по ID");
        Console.WriteLine("4. Показать информацию о столе");
        Console.WriteLine("5. Показать все бронирования");
        Console.WriteLine("6. Показать бронирования по фильтру (именя, последние 4 цифры номера телефона)");
        Console.WriteLine("7. Показать свободные столы по фильтру (время, количество мест)");
        Console.WriteLine();
    }

    static void SearchBooking(Manager M)
    {
        string partOfName = Getters.TryGetNonEmptyString("часть имени клиента");
        string last4NumbersOfPhone = Getters.TryGetString("последние 4 цифры номера телефона (Enter — не учитывать)") ?? "";

        Booking? booking = M.Search(partOfName, last4NumbersOfPhone);
        if (booking != null)
        {
            Console.WriteLine("Бронирование найдено:");
            Console.WriteLine(booking.ToString());
        }
        else
        {
            Console.WriteLine("Бронирование не найдено.");
        }
    }

    static void ShowFreeTablesByFilter(Manager M)
    {
        string timeSlot = Getters.TryGetNonEmptyString("временной промежуток (например, 12:00-13:00)");
        string minSeatsStr = Getters.TryGetString("минимальное количество мест (Enter — не учитывать)") ?? "";
        int? minSeats = null;
        if (!string.IsNullOrWhiteSpace(minSeatsStr) && int.TryParse(minSeatsStr, out int seats))
        {
            minSeats = seats;
        }
        Console.WriteLine();
        M.ShowFreeTables(timeSlot, minSeats);
        Console.WriteLine();
    }

    static void CreateTables(Manager manager)
    {
        int n = Getters.TryGetPositiveInt("количество столов (n > 0)");

        for (int i = 0; i < n; i++)
        {
            Console.WriteLine($"\n--- Стол {i + 1} из {n} ---");

            string location = Getters.TryGetNonEmptyString("место расположения стола");
            int seats = Getters.TryGetPositiveInt("количество мест (n > 0)");

            manager.AddTable(location, seats);
            Console.WriteLine($"Стол создан: стоит {location}, рассчитан на {seats} мест.\n");
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

        int n = Getters.TryGetPositiveInt("количество бронирований");

        for (int i = 0; i < n; i++)
        {
            Console.WriteLine($"\n--- Бронирование {i + 1} из {n} ---");

            string name = Getters.TryGetString("имя") ?? "гость";
            string phone = Getters.TryGetString("номер телефона") ?? "не указан";
            string? time = null;
            Table? selectedTable = null;

            while (true)
            {
                Console.Write("Время (например, 12:00-13:00): ");
                time = Getters.TryGetNonEmptyString("время (промежуток - час, например, 09:00-10:00)");

                bool isValidTime = manager.Tables.Any(t => t.Schedule.ContainsKey(time));
                if (!isValidTime)
                {
                    Console.WriteLine("Неверное время. Доступно: 09:00-10:00 ... 17:00-18:00");
                    continue;
                }

                List<Table> freeTables = [.. manager.Tables.Where(t => t.Schedule[time] == null)];
                if (freeTables.Count == 0)
                {
                    Console.WriteLine("На это время нет свободных столов. Выберите другое.");
                    continue;
                }

                Console.WriteLine("Свободные столы:");
                foreach (var t in freeTables)
                    Console.WriteLine($"  Стол {t.Id}: {t.Location}, {t.Seats} мест");

                int tableId = Getters.TryGetPositiveInt("ID");

                selectedTable = freeTables.Find(t => t.Id == tableId);
                if (selectedTable == null)
                {
                    Console.WriteLine("Стол занят или не существует. Выберите из списка.");
                    continue;
                }

                break;
            }

            string comment = Getters.TryGetString("примечание") ?? "";
            Booking booking = manager.Book(name, phone, time, comment, selectedTable);
            if (booking != null)
                Console.WriteLine($"Бронирование создано! ID клиента: {booking.ClientId}\n");
            else
                Console.WriteLine("Ошибка при создании.\n");
        }

        Console.WriteLine($"Готово: создано {n} бронирований.\n");
    }

    static void EditTable(Manager manager)
    {
        int id = Getters.TryGetPositiveInt("ID");

        Table table = manager.Tables.Find(t => t.Id == id);
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
        string newLoc = Getters.TryGetString() ?? "";
        Console.Write("Новое кол-во мест (Enter — не менять): ");
        string seatsStr = Getters.TryGetString() ?? "";

        string loc = string.IsNullOrWhiteSpace(newLoc) ? table.Location : newLoc;
        int seats = string.IsNullOrWhiteSpace(seatsStr) ? table.Seats : int.Parse(seatsStr);

        manager.EditTable(id, loc, seats);
        Console.WriteLine("Стол обновлён.\n");
    }

    static void ShowTable(Manager manager)
    {
        int id = Getters.TryGetPositiveInt("ID");
        Console.WriteLine();
        manager.ShowTable(id);
        Console.WriteLine();
    }
}