#include <iostream>
#include <vector>
using namespace std;

int n, m;
vector<vector<int>> visited(1000, vector<int>(1000, 0));

vector<pair<int, int>> get_direction_of_moving(int x, int y)
{
    vector<pair<int, int>> directions;
    const int dx[] = {0, 0, 1, -1}; // Право, лево, низ, верх
    const int dy[] = {1, -1, 0, 0};

    for (int i = 0; i < 4; ++i)
    {
        int newX = x + dx[i];
        int newY = y + dy[i];
        if (newX >= 0 && newX < n && newY >= 0 && newY < m && visited[newX][newY] == 0)
        {
            visited[newX][newY] = 1;
            directions.emplace_back(newX, newY);
        }
    }
    return directions;
}

int lab(const vector<vector<string>> &labirinth, int x, int y)
{
    int sum = 0;
    for (const auto &[newX, newY] : get_direction_of_moving(x, y))
    {
        if (labirinth[newX][newY] == "P")
            sum += 1;
        if (labirinth[newX][newY] != "1")
            sum += lab(labirinth, newX, newY);
    }
    return sum;
}

int main()
{
    int sx = -1, sy = -1;
    cin >> n >> m;
    vector<vector<string>> labirinth(n, vector<string>(m));

    for (int i = 0; i < n; ++i)
    {
        for (int j = 0; j < m; ++j)
        {
            cin >> labirinth[i][j];
            if (labirinth[i][j] == "S")
            {
                sx = i;
                sy = j;
            }
        }
    }

    if (sx != -1 && sy != -1)
        cout << lab(labirinth, sx, sy) << endl;
    else
    {
        cout << "Нет начала!" << endl;
        return 1;
    }
    return 0;
}
