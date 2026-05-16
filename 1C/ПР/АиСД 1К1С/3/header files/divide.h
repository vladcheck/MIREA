#include <string>
#include "subBasic.h"
#include "addBasic.h"
#include <iostream>
using namespace std;

string divideBy2(string num)
{
    string count = "0";
    while (num[0] != '-')
    {
        num = subBasic(num, "2");
        count = addBasic(count, "1");
    }
    cout << num + "   " + count << endl;
    return count;
}
