#include "./header files/utils.h"
using namespace std;

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

string subBasic(string a, string b)
{
    bool negate = compare(a, b) == -1;
    string maxNum, minNum;
    if (negate == -1)
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
    vector<int> res;
    for (int i = 0; i < maxVec.size(); i++)
    {
        int diff = maxVec[i] - minVec[i];
        res.push_back(diff < 0 ? diff + 10 : diff);
        if (diff < 0)
        {
            maxVec[i - 1] -= 1;
        }
    }
    string result = list_to_str(res);
    if (negate)
    {
        result = "-" + result;
    }
    return result;
}

int main()
{
    string a = "99999999999999999999999999999999999999999999999999999";
    string b = "1111111111111111111111111111111111111111111111111111111111111111";
    cout << addBasic(a, b) << endl;
    cout << subBasic(a, b) << endl;

    return 0;
}
