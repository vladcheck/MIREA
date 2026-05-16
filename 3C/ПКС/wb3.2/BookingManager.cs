public class Manager
{
    public List<Table> Tables { get; } = [];
    public List<Booking> Bookings { get; } = [];
    protected int NextId { get => nextId; set => nextId = value; }

    private int nextId = 1;

    public int GetFreeId()
    {
        return this.NextId;
    }

    public Table AddTable(string location, int seats)
    {
        var table = new Table(this.NextId, location, seats);
        this.NextId++;
        Tables.Add(table);
        return table;
    }

    public Booking? Book(string name, string phone, string time, string comment, Table table)
    {
        if (string.IsNullOrWhiteSpace(time) || !table.Schedule.TryGetValue(time, out Booking? value))
            return null;

        if (value != null)
        {
            Console.WriteLine($"Время {time} уже занято.");
            return null;
        }

        var booking = new Booking(NextId++, name, phone, time, comment, table);
        Bookings.Add(booking);
        return booking;
    }

    public void EditTable(int id, string newLocation, int newSeats)
    {
        var table = Tables.Find(t => t.Id == id);
        if (table == null)
        {
            Console.WriteLine($"Стол с ID {id} не найден.");
            return;
        }

        if (!table.CanEdit())
        {
            Console.WriteLine($"Нельзя изменить стол {id}: есть брони.");
            return;
        }

        table.Location = newLocation ?? table.Location;
        table.Seats = newSeats > 0 ? newSeats : table.Seats;
        Console.WriteLine($"Стол {id} обновлён.");
    }

    public void ShowTable(int id)
    {
        var table = Tables.Find(t => t.Id == id);
        if (table == null)
            Console.WriteLine($"Стол с ID {id} не найден.");
        else
            table.Print();
    }

    public void ShowAllBookings()
    {
        if (!Bookings.Any())
            Console.WriteLine("Нет бронирований.");
        else
            foreach (var b in Bookings)
                Console.WriteLine(b.ToString());
    }

    public void ShowFreeTables(string time, int? minSeats = null)
    {
        if (string.IsNullOrWhiteSpace(time)) return;

        var free = Tables.Where(t =>
            t.Schedule.ContainsKey(time) &&
            t.Schedule[time] == null &&
            (!minSeats.HasValue || t.Seats >= minSeats.Value));

        Console.WriteLine($"Свободные столы на {time}:");
        foreach (var t in free)
            Console.WriteLine($"  Стол {t.Id}: {t.Location}, {t.Seats} мест");
    }

    public Booking? Search(string namePart, string last4)
    {
        if (string.IsNullOrWhiteSpace(namePart)) return null;

        var found = Bookings.Where(b =>
            b.Name.Contains(namePart, StringComparison.OrdinalIgnoreCase));

        if (last4.Length > 0)
        {
            found = found.Where(b =>
                b.Phone.Length >= 4 &&
                b.Phone[^4..].Equals(last4));
        }

        if (!found.Any())
            return null;
        else
            foreach (var b in found)
                return b;
        return null;
    }

    public List<Booking> ShowFreeTablesByFilter(string? clientNamePart)
    {
        if (String.IsNullOrEmpty(clientNamePart))
        {
            return this.Tables
                .SelectMany(t => t.Schedule.Values)
                .Where(b => b != null)
                .ToList()!;
        } else
        {
            return this.Tables
                .SelectMany(t => t.Schedule.Values)
                .Where(b => b != null && b.Name.Contains(clientNamePart, StringComparison.OrdinalIgnoreCase))
                .ToList()!;
        }
    }
}