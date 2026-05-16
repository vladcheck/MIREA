#include <iostream>
using namespace std;

int NOD(int a, int b)
{
    return (!b) ? a + b : NOD(b, a % b);
}

int main()
{
    int a;
    int b;
    cin >> a >> b;
    cout << NOD(a, b);
    return 0;
}