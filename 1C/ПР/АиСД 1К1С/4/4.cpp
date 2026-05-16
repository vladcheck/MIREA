#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

template <typename T>
T sum(T num) {
    if (num < 0) num *= -1;
    if (num < 10)
        return num;
    return sum(num / 10) + num % 10;
}

int main()
{
    cout << sum(1234) << endl;
    cout << sum(-1121135) << endl;
    return 0;
}
