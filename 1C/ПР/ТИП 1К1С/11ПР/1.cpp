#include <iostream>
#include <vector>
#include <array>
#include <utility>
#include <limits>
#include "debug.h"

const int MINIMUM = std::numeric_limits<int>::min();

std::vector<std::pair<short,short>> get_max_points(std::vector<std::vector<int>>& points, int rows, int cols) {
    std::vector<std::pair<short,short>> pairs = {std::make_pair(0,0)};
    int i = 0, j = 0;
    while (true) {
        int right = (j+1 < cols) ? points[i][j+1] : MINIMUM;
        int up = (i+1 < rows) ? points[i+1][j] : MINIMUM;
        // Мы дошли до конца, выходим из цикла
        if (right == MINIMUM && up == MINIMUM) { 
            break;
        }
        // Вверх некуда идти, идем вправо
        else if (right == MINIMUM && up != MINIMUM) {
            i++;
        }
        // Вправо некуда идти, идем вверх
        else if (right != MINIMUM && up == MINIMUM) {
            j++;
        }
        // Справа выгодней
        else if (right > up) {
            j++;
        // Слева выгодней
        } else {
            i++;
        }
        pairs.push_back(std::make_pair(i,j));
    }
    return pairs;
}

int main(int argc, char const *argv[])
{
    int rows, cols;
    std::cin >> rows >> cols;
    std::vector<std::vector<int>> points(rows, std::vector<int>(cols,0));
    
    // Заполняем сетку входными данными
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            int temp;
            std::cin >> temp;
            points[i][j] = temp;
        }
    }
    
    std::cout << std::endl;
    print_grid(points);
    std::cout << std::endl;

    auto pairs = get_max_points(points,rows,cols);
    // Печатаем точки маршрута
    for (auto pair : pairs) {
        std::cout << pair.first << " " << pair.second << std::endl;
    }
    return 0;
}
