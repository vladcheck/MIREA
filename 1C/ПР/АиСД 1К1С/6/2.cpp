#include <iostream>
#include <vector>
#include <algorithm>

std::pair<int, int> f(std::vector<int> *arr)
{
    int res = 0, sum = 0;
    for (auto n : *arr)
    {
        if (n % 5 == 0 && n % 7 != 0) 
        {
            res++;
            sum += n;
            std::cout << n << " ";
        }
    }
    std::cout << std::endl;
    return std::make_pair(res, sum);
}

int main()
{
    int n = 20;
    std::vector<int> arr;
    for (int i = 1; i < n; i++)
    {
        int n = 2 * i + 1;
        arr.push_back(n);
        std::cout << n << " ";
    }
    std::cout << std::endl;

    std::pair<int, int> res = f(&arr);
    std::cout << "Amount: " << res.first << std::endl;
    std::cout << "Sum: " << res.second << std::endl;

    return 0;
}