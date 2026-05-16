#pragma once

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

vector<int> pushout(vector<int> &a)
{
    int toPush = 0;
    if (a[0] >= 10)
    {
        toPush = a[0] / 10;
        a[0] %= 10;
        a.insert(a.begin(), toPush);
    }
    return a;
}

vector<int> moveaway(vector<int> &a)
{
    reverse(a.begin(), a.end());
    for (int j = 0; j < a.size() - 1; j++)
    {
        a[j + 1] += a[j] / 10;
        a[j] %= 10;
    }
    reverse(a.begin(), a.end());
    return a;
}

vector<int> split(string a)
{
    vector<int> result;
    for (char c : a)
    {
        result.push_back(c - '0');
    }
    return result;
}

string list_to_str(const vector<int> &a)
{
    string result;
    for (int digit : a)
    {
        result += to_string(digit);
    }
    while (result.size() > 1 && result[0] == '0')
    {
        result.erase(result.begin());
    }
    return result;
}

short compare_strings(const std::string &a, const std::string &b)
{
    if (a.size() < b.size())
        return -1;
    if (a.size() > b.size())
        return 1;

    for (size_t i = 0; i < a.size(); i++)
    {
        if (a[i] < b[i])
            return -1;
        if (a[i] > b[i])
            return 1;
    }

    return 0;
}

/*
Возвращает 0, если a == b
Возвращает 1, если a < b
Возвращает -1, если a > b
*/
short compare(std::string a, std::string b)
{
    size_t pos_a = a.find('.');
    size_t pos_b = b.find('.');

    std::string int_a = (pos_a == std::string::npos) ? a : a.substr(0, pos_a);
    std::string frac_a = (pos_a == std::string::npos) ? "" : a.substr(pos_a + 1);

    std::string int_b = (pos_b == std::string::npos) ? b : b.substr(0, pos_b);
    std::string frac_b = (pos_b == std::string::npos) ? "" : b.substr(pos_b + 1);

    short int_comparison = compare_strings(int_a, int_b);
    if (int_comparison != 0)
    {
        return int_comparison;
    }

    return compare_strings(frac_a, frac_b);
}

pair<vector<int>, vector<int>> even_out(vector<int> &a, vector<int> &b)
{
    int lenMax = max(a.size(), b.size()) + 1;
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
