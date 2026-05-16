#include <iostream>
#include <vector>
#include <cmath>
using namespace std;


template <typename T> T deikstra(T num)
{
    if (num == 1)
        return 1;
    if (num % 2 == 0)
        return deikstra(num / 2);
    return deikstra((num - 1) / 2) + deikstra(num + 1);
}

int main()
{
    cout << deikstra(4) << endl;
    cout << deikstra(41) << endl;
    cout << deikstra(412) << endl;
    return 0;
}
