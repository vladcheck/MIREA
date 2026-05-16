#include <vector>
#include <iostream>
#include <algorithm>
#include "debug.h"

int sum(std::vector<int>& vec) {
    int sum = 0;
    for (int n : vec) {
        sum += n;
    }
    return sum;
}

int max(std::vector<int>& prices, int amount_in_bouquet, int max_same) {
    // Распологаем цены в порядке убывания
    std::sort(prices.begin(),prices.end());
    std::reverse(prices.begin(),prices.end());

    std::vector<int> bouquet{};
    for (int i = 0; i < prices.size();i++) {
        // Больше не нужно цветов в букете
        if (bouquet.size() == amount_in_bouquet) {
            break;
        }
        // Добавим еще один цветок, если таких же по стоимости меньше, чем
        // Позволено максимально
        else if (std::count(bouquet.begin(),bouquet.end(),prices[i]) < max_same) {
            bouquet.push_back(prices[i]);
        }
    }
    // Для дебаггинга
    print_vector(bouquet);
    return sum(bouquet);
}

int main(int argc, char const *argv[])
{
    // Пример
    int N = 5, K = 4, L = 2;
    std::vector<int> prices{200,200,200,300,100};
    std::cout << max(prices,K,L) << std::endl; // 800
    return 0;
}
