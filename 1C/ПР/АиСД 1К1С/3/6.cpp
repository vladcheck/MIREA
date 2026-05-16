#include <cmath>
#include <iostream>
#include "./header files/addBasic.h"
#include "./header files/subBasic.h"
#include "./header files/mult.h"
#include "./header files/divide.h"
using namespace std;

string f(string a, string b, string p)
{
    return subBasic(a, mult(b, p));
}

pair<string, string> div_and_leftout(string a, string b)
{
    string l = "0";
    string r = a;
    string p;
    int count = 0;
    do
    {
        p = divideBy2(addBasic(l, r));
        cout << p << endl;
        if (mult(f(a, b, l), f(a, b, p))[0] != '0')
        {
            l = p;
        }
        else
        {
            r = p;
        }
        // cout << f(a, b, p) << endl;
        count++;
    } while (compare_strings(f(a, b, p), "0") > 0 && count < 100);
    string q = subBasic(a, mult(b, p));
    return make_pair(p, q);
}

int main()
{
    auto result1 = div_and_leftout("17", "5");
    cout << result1.first << ", " << result1.second << endl;

    auto result3 = div_and_leftout("312897", "1131");
    cout << result3.first << ", " << result3.second << endl;

    return 0;
}
