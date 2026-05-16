#pragma once
#include "utils.h"

string subBasic(string a, string b)
{
    bool negate = compare(a, b) == -1;
    string maxNum, minNum;
    if (negate)
    {
        minNum = a;
        maxNum = b;
    }
    else
    {
        minNum = b;
        maxNum = a;
    }
    vector<int> maxVec = split(maxNum), minVec = split(minNum);
    tie(maxVec, minVec) = even_out(maxVec, minVec);
    vector<int> res(maxVec.size(), 0);
    bool borrow = false;

    for (int i = maxVec.size() - 1; i >= 0; i--)
    {
        int diff = maxVec[i] - minVec[i] - (borrow ? 1 : 0);
        if (diff < 0)
        {
            diff += 10;
            borrow = true;
        }
        else
        {
            borrow = false;
        }
        res[i] = diff;
    }

    string result = list_to_str(res);
    result.erase(0, min(result.find_first_not_of('0'), result.size() - 1));
    return (negate) ? "-" + result : result;
}
