while (true)
{
    uint n = TryGetUInt("Введите количество модулей (n): ");
    uint a = TryGetUInt("Введите ширину модуля (a): ");
    uint b = TryGetUInt("Введите длину модуля (b): ");
    uint w = TryGetUInt("Введите ширину поля (w): ");
    uint h = TryGetUInt("Введите длину поля (h): ");

    uint maxD = FindMaxProtection(n, a, b, w, h);

    Console.WriteLine($"Максимальная толщина защиты (d) = {maxD}");
}

static uint TryGetUInt(string prompt)
{
    while (true)
    {
        Console.Write(prompt);
        string? input = Console.ReadLine();

        if (UInt32.TryParse(input, out uint value) && value != 0)
        {
            return value;
        }

        Console.WriteLine("Ошибка: введите положительное целое число.");
    }
}

static uint FindMaxProtection(uint n, uint a, uint b, uint w, uint h)
{
    uint maxD = 0;

    for (uint d = 0; d <= Math.Max(w, h); d++)
    {
        if (CanPlaceAllModules(n, a, b, w, h, d))
        {
            maxD = d;
        }
    }

    return maxD;
}

static bool CanPlaceAllModules(uint n, uint a, uint b, uint w, uint h, uint d)
{
    bool[,] field = new bool[w, h];
    return TryPlaceModules(field, n, a, b, w, h, d, 0);
}

static bool TryPlaceModules(bool[,] field, uint remainingModules, uint a, uint b, uint w, uint h, uint d, uint startPos)
{
    if (remainingModules == 0)
        return true;

    uint width1 = a + 2 * d;
    uint height1 = b + 2 * d;
    uint width2 = b + 2 * d;
    uint height2 = a + 2 * d;

    for (uint pos = startPos; pos < w * h; pos++)
    {
        uint x = pos % w;
        uint y = pos / w;

        if (CanPlace(field, x, y, width1, height1, w, h))
        {
            PlaceModule(field, x, y, width1, height1, true);
            if (TryPlaceModules(field, remainingModules - 1, a, b, w, h, d, pos + 1))
                return true;
            PlaceModule(field, x, y, width1, height1, false);
        }

        if (width2 != width1 || height2 != height1)
        {
            if (CanPlace(field, x, y, width2, height2, w, h))
            {
                PlaceModule(field, x, y, width2, height2, true);
                if (TryPlaceModules(field, remainingModules - 1, a, b, w, h, d, pos + 1))
                    return true;
                PlaceModule(field, x, y, width2, height2, false);
            }
        }
    }

    return false;
}

static bool CanPlace(bool[,] field, uint x, uint y, uint width, uint height, uint w, uint h)
{
    if (x + width > w || y + height > h)
        return false;

    for (uint i = x; i < x + width; i++)
    {
        for (uint j = y; j < y + height; j++)
        {
            if (field[i, j])
                return false;
        }
    }

    return true;
}

static void PlaceModule(bool[,] field, uint x, uint y, uint width, uint height, bool place)
{
    for (uint i = x; i < x + width; i++)
    {
        for (uint j = y; j < y + height; j++)
        {
            field[i, j] = place;
        }
    }
}
