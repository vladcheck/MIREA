#include <vector>
#include <iostream>

template <typename T>
void print_grid(std::vector<std::vector<T>> &grid) {
    for (auto row : grid) {
        for (auto n : row) {
            std::cout << n << " ";
        }
        std::cout << std::endl;
    }
}

template <typename T>
void print_vector(std::vector<T> vec) {
    for (auto item : vec) {
        std::cout << item << " ";
    }
    std::cout << std::endl;
}
