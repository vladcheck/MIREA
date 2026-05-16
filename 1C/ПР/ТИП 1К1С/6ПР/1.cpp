#include <iostream>
#include <cmath>
using namespace std;

int main()
{
    int n;
    cin >> n;
    for (int i = 1; i <= n; i++)
    {
        for (int j = 1; j <= n; j++)
        {
            if (i + j == n + 1) // Если элементы находятся на главной диагонали
            {
                cout << "1 ";
            }
            else if (abs(i + j) <= n) // Если элементы над главной диагональю
            {
                cout << "0 ";
            }
            else // Если элементы под гл. диаг.
            {
                cout << "2 ";
            }
        }
        cout << endl;
    }
    return 0;
}