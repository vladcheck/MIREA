using System;
using System.Collections.Generic;
using System.Linq;

public class Manager
{
    public List<Table> Tables { get; } = new();
    public List<Booking> Bookings { get; } = new();
    private int nextId = 1;

    public Table AddTable(int id, string location, int seats)
    {
        if (Tables.Any(t => t.Id == id))
            throw new ArgumentException($"Стол с ID {id} уже существует.");

        var table = new Table(id, location, seats);
        Tables.Add(table);
        return table;
    }

    public Booking? Book(string name, string phone, string time, string comment, Table table)
    {
        if (string.IsNullOrWhiteSpace(time) || !table.Schedule.ContainsKey(time))
            return null;

        if (table.Schedule[time] != null)
        {
            Console.WriteLine($"Время {time} уже занято.");
            return null;
        }

        var booking = new Booking(nextId++, name, phone, time, comment, table);
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
                Console.WriteLine(b);
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

    public void Search(string namePart, string last4)
    {
        if (string.IsNullOrWhiteSpace(namePart) || string.IsNullOrWhiteSpace(last4)) return;

        var found = Bookings.Where(b =>
            b.Name.Contains(namePart, StringComparison.OrdinalIgnoreCase) &&
            b.Phone.Length >= 4 &&
            b.Phone.EndsWith(last4));

        if (!found.Any())
            Console.WriteLine("Ничего не найдено.");
        else
            foreach (var b in found)
                Console.WriteLine(b);
    }
}