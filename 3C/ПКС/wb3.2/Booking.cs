public class Booking
{
    public int ClientId { get; }
    public string Name { get; }
    public string Phone { get; }
    public string TimeSlot { get; }
    public string Comment { get; }
    public Table Table { get; }

    public Booking(int id, string name, string phone, string time, string comment, Table table)
    {
        ClientId = id;
        Name = name ?? "Гость";
        Phone = phone ?? "";
        TimeSlot = time ?? throw new ArgumentNullException(nameof(time));
        Comment = comment ?? "";
        Table = table ?? throw new ArgumentNullException(nameof(table));


        Table.Schedule[TimeSlot] = this;
    }

    public void Cancel()
    {
        if (Table.Schedule.ContainsKey(TimeSlot))
            Table.Schedule[TimeSlot] = null;
    }

    public override string ToString()
    {
        return $"ID {ClientId}: {Name}, {Phone}, {TimeSlot}, Стол {Table.Id}";
    }
}