#include <iostream>
using namespace std;

int main()
{
    int n, m, k;
    cin >> n >> m >> k;
    // можно отломить k кусочков, если они кратны какой-либо из сторон плитки
    // и если k кусочков <= общему кол-ву кусочков (т.е. n*m)
    cout << (k % n == 0 || k % m == 0) && (k <= n * m);
    return 0;
}