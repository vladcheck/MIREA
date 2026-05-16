#include <vector>
#include <iostream>
#include <cstdlib>

bool has_two_zeros(std::vector<int> *arr)
{
    for (int i = 1; i < (*arr).size(); i++)
    {
        if ((*arr)[i - 1] == 0 && (*arr)[i] == 0)
            return true;
    }
    return false;
}

bool has_three_zeros(std::vector<int> *arr)
{
    for (int i = 2; i < (*arr).size(); i++)
    {
        if ((*arr)[i - 2] == 0 && (*arr)[i - 1] == 0 && (*arr)[i] == 0)

            return true;
    }
    return false;
}

int main()
{
    std::srand(time(0));

    int n = 20;
    std::vector<int> arr;
    for (int i = 1; i < n; i++)
    {
        int n = (std::rand() % 10 < 5) ? 0 : 1;
        arr.push_back(n);
        std::cout << n << " ";
    }
    std::cout << std::endl;

    std::cout << has_two_zeros(&arr) << std::endl;
    std::cout << has_three_zeros(&arr) << std::endl;
    return 0;
}