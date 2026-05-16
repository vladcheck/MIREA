#include <iostream>
using namespace std;

int NOD(int a, int b)
{
    if (a == b)
        return a;
    return (a > b) ? NOD(a - b, b) : NOD(a, b - a);
}

int main()
{
    cout << NOD(15, 3) << endl;
    cout << NOD(17, 3) << endl;
    cout << NOD(15, 15) << endl;
    return 0;
}