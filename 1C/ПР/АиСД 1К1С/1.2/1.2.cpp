#include <iostream>
#include <cmath>

using namespace std;

int basedOnSubtraction(int a, int b)
{
    int big = max(a, b);
    int small = min(a, b);
    while (small != big)
    {
        int temp = small;
        small = big - small;
        big = temp;
    }
    return big;
}

int main(int argc, char const *argv[])
{
    // int a, b, c, d;
    // cin >> a;
    // cin >> b;
    // cin >> c;
    // cin >> d;
    cout << basedOnSubtraction(96, 128);
    return 0;
}
