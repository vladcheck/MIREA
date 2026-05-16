#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// Функция для получения координат соседних клеток
vector<pair<int, int>> get_coords(int i, int j, int n, int m)
{
    vector<pair<int, int>> coords = {};
    for (int di = i - 1; di <= i + 1; di++)
    {
        for (int dj = j - 1; dj <= j + 1; dj++)
        {
            // Пропускаем текущую клетку
            if (dj == j && di == i)
                continue;
            // Проверяем, находится ли соседка в пределах поля
            if (dj > -1 && di > -1 && dj < m && di < n)
            {
                pair<int, int> p = {di, dj};
                coords.push_back(p);
            }
        }
    }
    return coords;
}

void mushrooms(int n, int m, int w)
{
    vector<vector<int>> field;
    // Инициализируем поле нулями (отсутствием грибов)
    for (int i = 0; i < n; i++)
    {
        field.push_back({});
        for (int j = 0; j < m; j++)
        {
            field[i].push_back(0);
        }
    }

    // Вводим координаты грибов
    for (int i = 0; i < w; i++)
    {
        int row, col;
        cin >> row >> col;
        // Индексы в массиве начинаются с нуля, поэтому уменьшаем координаты на 1
        row--;
        col--;
        // Помечаем координаты грибов как -1
        field[row][col] = -1;
    }

    // Подсчитываем количество соседних грибов для каждой клетки
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < m; j++)
        {
            // Пропускаем клетки с грибами
            if (field[i][j] == -1)
                continue;
            vector<pair<int, int>> coords = get_coords(i, j, n, m);
            for (auto p : coords)
            {
                int row = p.first, col = p.second;
                // Если соседняя клетка содержит гриб, увеличиваем счетчик для текущей клетки
                if (field[row][col] == -1)
                    field[i][j]++;
            }
        }
    }

    // Выводим поле с количеством грибов вокруг каждой клетки
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < m; j++)
        {
            if (field[i][j] == -1)
            {
                cout << "*";
            }
            else
            {
                cout << field[i][j];
            }
            // Выводим пробел между клетками
            cout << " ";
        }
        cout << endl;
    }
}

int main()
{
    int n, m, w;
    cin >> n >> m >> w;
    mushrooms(n, m, w);
    return 0;
}