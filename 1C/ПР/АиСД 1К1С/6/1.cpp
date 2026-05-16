#include <iostream>
#include <cmath>
#include <vector>
#include "get_smaller_string.h"
#include "mult.h"

std::string mult(std::string a, std::string b);
std::string compare_strings(std::string a, std::string b);

int a(std::vector<int> *arr)
{
    int res = 0;
    for (int n : *arr)
    {
        if (n % 2 == 1)
        {
            res++;
        }
    }
    return res;
}

int b(std::vector<int> *arr)
{
    int res = 0;
    int size = (*arr).size();
    for (double n : *arr)
    {
        double sq = std::sqrt(n);
        if (sq == (int)sq && (int)sq % 2 == 0)
        {
            res++;
        }
    }
    return res;
}

int c(std::vector<int> *arr)
{
    int res = 0;
    for (int n : *arr)
    {
        if (n % 3 == 0 && n % 5 != 0)
        {
            res++;
        }
    }
    return res;
}

std::string pow(int a, int b)
{
    std::string res = "1";
    std::string base = std::to_string(a);
    std::string exp = std::to_string(b);

    for (int i = 0; i < b; i++)
    {
        res = mult(res, base);
    }
    return res;
}

std::string factorial(int n)
{
    if (n == 0 || n == 1)
        return "1";
    std::string res = "1";
    for (int i = 1; i <= n; i++)
    {
        res = mult(res, std::to_string(i));
    }
    return res;
}

int d(std::vector<int> *arr)
{
    int res = 0;
    int size = (*arr).size();
    for (int i = 0; i < size; i++)
    {
        std::string n = std::to_string((*arr)[i]);
        std::string left = pow(2, i);
        std::string right = factorial(i);

        if (get_smaller_string(left, n) == left && get_smaller_string(n, right) == n)
        {
            res++;
        }
    }
    return res;
}

int e(std::vector<int> *arr)
{
    int res = 0;
    int size = (*arr).size();
    for (int i = 1; i < size - 1; i++)
    {
        int k = (*arr)[i];
        double k_left = (*arr)[i - 1], k_right = (*arr)[i + 1];

        if (k < (k_left + k_right) / 2)
        {
            res++;
        }
    }
    return res;
}

int f(std::vector<int> *arr)
{
    int res = 0;
    int size = (*arr).size();
    for (int i = 1; i < size - 1; i++)
    {
        if (i % 2 == 0 && (*arr)[i] % 2 == 1)
            res++;
    }
    return res;
}

double a_n(int n)
{
    return std::pow(2, n) + n;
}

int main()
{
    int n = 15;
    std::vector<int> arr;
    for (int i = 1; i <= n; i++)
    {
        double a = a_n(i);
        arr.push_back(a);
        std::cout << a << " ";
    }
    std::cout << std::endl;

    std::cout << "a)" << a(&arr) << std::endl;
    std::cout << "b)" << b(&arr) << std::endl;
    std::cout << "v)" << c(&arr) << std::endl;
    std::cout << "g)" << d(&arr) << std::endl;
    std::cout << "d)" << e(&arr) << std::endl;
    std::cout << "e)" << f(&arr) << std::endl;

    return 0;
}