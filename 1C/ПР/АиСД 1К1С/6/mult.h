#include <vector>
#include <algorithm>
#include <string>
#include <iostream>

std::vector<int> split(std::string a)
{
    std::vector<int> res;
    for (auto c : a)
    {
        res.push_back(c - '0');
    }
    return res;
}

std::string vector_to_string(std::vector<int> vec)
{
    std::string res = "";
    for (auto d : vec)
    {
        res = res + std::to_string(d);
    }
    while (res[0] == '0' && res.size() > 1)
    {
        res.erase(res.begin());
    }
    return res;
}

std::pair<std::vector<int>, std::vector<int>> even_out(std::vector<int> &a, std::vector<int> &b)
{
    int lenMax = std::max(a.size(), b.size()) + 1;
    while (a.size() < lenMax)
    {
        a.insert(a.begin(), 0);
    }
    while (b.size() < lenMax)
    {
        b.insert(b.begin(), 0);
    }
    return make_pair(a, b);
}

std::vector<int> multiply_vector_by_int(std::vector<int> vec, int n)
{
    std::vector<int> res;
    int left = 0;
    for (int i = vec.size() - 1; i >= 0; i--)
    {
        res.insert(res.begin(), vec[i] * n % 10 + left);
        left = vec[i] * n / 10;
    }
    return res;
}

std::vector<std::vector<int>> get_addition_rows(std::vector<int> a, std::vector<int> b)
{
    std::vector<std::vector<int>> res;
    for (auto d : b)
    {
        res.push_back(multiply_vector_by_int(a, d));
    }
    std::reverse(res.begin(), res.end());
    for (int i = 0; i < res.size(); i++)
    {
        for (int j = 0; j < i; j++)
        {
            res[i].push_back(0);
        }
    }
    for (int i = 0; i < res.size(); i++)
    {
        while (res[i].size() < res.back().size())
        {
            res[i].insert(res[i].begin(), 0);
        }
    }
    return res;
}

std::vector<int> add_vectors(std::vector<std::vector<int>> vecs)
{
    std::vector<int> res;
    int left = 0;
    for (int i = vecs.back().size() - 1; i >= 0; i--)
    {
        int sum = 0;
        for (auto vec : vecs)
        {
            sum += vec[i];
        }
        res.insert(res.begin(), (sum + left) % 10);
        left = (sum + left) / 10;
    }
    return res;
}

std::string get_rid_of_minus(std::string a)
{
    return (a[0] == '-') ? a.substr(1, a.size() - 2) : a;
}

std::string mult(std::string a, std::string b)
{
    if (a == "0" || b == "0")
        return "0";
    bool negative = (a[0] == '-' && b[0] != '-') || (a[0] != '-' && b[0] == '-');
    a = get_rid_of_minus(a);
    b = get_rid_of_minus(b);
    std::vector<int> top = split(a);
    std::vector<int> bottom = split(b);
    std::tie(top, bottom) = even_out(top, bottom);
    std::vector<std::vector<int>> addition_rows = get_addition_rows(top, bottom);
    std::string res = vector_to_string(add_vectors(addition_rows));
    return (negative) ? "-" + res : res;
}