#include <iostream>
#include <vector>
#include <cstdlib>

bool is_sorted_in_decreasing_order(std::vector<int> *arr)
{
    for (int i = 1; i < arr->size(); i++)
    {
        if ((*arr)[i - 1] <= (*arr)[i])
            return false;
    }
    return true;
}

int main()
{
    srand(time(0));
    int n = rand() % 5 + 2;
    std::vector<int> arr;
    for (int i = n; i > 0; i--)
    {
        int val = i + rand() % 5;
        arr.push_back(val);
        std::cout << val << " ";
    }
    std::cout << std::endl;
    std::cout << is_sorted_in_decreasing_order(&arr) << std::endl;
    return 0;
}