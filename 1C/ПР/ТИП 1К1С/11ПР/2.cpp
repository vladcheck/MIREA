#include <vector>
#include <limits>
#include <algorithm>
#include <iostream>
#include "debug.h"

// Минимальное значение в векторе
template <typename T>
T min(std::vector<T> vec) {
    int res = std::numeric_limits<int>::max();
    for (auto n : vec) {
        res = (res > n) ? n : res;
    }
    return res;
}

// Составить вектор из разниц соседних значений вектора на входе
template <typename T>
std::vector<T> differences(std::vector<T>& vec) {
    std::vector<T> res;
    for (int i = 1; i < vec.size(); i++) {
        res.push_back(vec[i] - vec[i-1]);
    }
    return res;
}

int min_difference_among_days(std::vector<int> &calories, int total_days) {
    if (calories.size() < total_days) return -1; // Пирожков не хватит на все дни
    if (calories.size() == total_days) return 0; // Пирожков нужно есть строго по одному за день

    int max_per_day = calories.size() / total_days; // Сколько пирожков будет съедать спортсмен каждый день (кроме первого)
    std::sort(calories.begin(),calories.end());

    std::vector<std::vector<int>> days(total_days,std::vector<int>{});
    int calorie_index = 0;

    for (int i = 0; i < days.size();i++) {
        // Продолжаем заполнять день пирожками, пока их не будет `max_per_day`
        // Либо `max_per_day + 1`, если это первый день
        while (days[i].size() < max_per_day || (i==0 && days[0].size() < max_per_day + 1)) {
            days[i].push_back(calories[calorie_index]);
            calorie_index++;
        }
    }

    std::vector<int> diffs; // Вектор минимальной разности в калориях за каждый день
    for (auto day : days) {
        print_vector(day);
        diffs.push_back(min(differences(day)));
    }
    return min(diffs); // Возвращаем минимальную разность в калориях за все дни
}

int main(int argc, char const *argv[])
{
    // Пример
    int N = 10, D = 4;
    std::vector<int> calories{120, 75, 320, 145, 250, 305, 175, 80, 215};
    std::cout << min_difference_among_days(calories, D) << std::endl; // 5
    return 0;
}
