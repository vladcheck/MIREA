#pragma once
#include "utils.h"

string addBasic(string a, string b)
{
    vector<int> aVec = split(a);
    vector<int> bVec = split(b);
    tie(aVec, bVec) = even_out(aVec, bVec);
    vector<int> res;
    for (int i = 0; i < aVec.size(); i++)
    {
        res.push_back(aVec[i] + bVec[i]);
    }
    return list_to_str(moveaway(res));
}
