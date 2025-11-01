using System;
using System.Collections.Generic;

public class Table
{
    public int Id { get; }
    public string Location { get; set; }
    public int Seats { get; set; }
    public Dictionary<string, Booking?> Schedule { get; } = new();

    public Table(int id, string location, int seats)
    {
        Id = id;
        Location = location ?? "не указано";
        Seats = seats;

        for (int h = 9; h < 18; h++)
        {
            string slot = $"{h:00}:00-{(h + 1):00}:00";
            Schedule[slot] = null; 
        }
    }

    public void Print()
    {
        Console.WriteLine($"ID: {"".PadRight(80, '-')}{Id:D2}.");
        Console.WriteLine($"Расположение: {"".PadRight(60, '-')}\" {Location} \".");
        Console.WriteLine($"Количество мест: {"".PadRight(60, '-')}{Seats}");
        Console.WriteLine("Расписание:");
        foreach (var s in Schedule)
        {
            string line = $"{s.Key} ";
            if (s.Value == null)
                line += "-----------------------------------------------------";
            else
                line += $"-------------------ID {s.Value.ClientId}, {s.Value.Name}, {s.Value.Phone}";
            Console.WriteLine(line);
        }
    }

    public bool CanEdit()
    {
        foreach (var b in Schedule.Values)
            if (b != null) return false;
        return true;
    }
}