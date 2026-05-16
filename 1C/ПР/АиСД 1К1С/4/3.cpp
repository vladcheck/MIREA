#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

long double f(long double x)
{
    return 3 * x - 14 + exp(x) - exp(-x);
}

vector<long double> half_division(long double L, long double R, long double B)
{
    if (R - L <= pow(10, -10))
        return {B, f(B)};
    B = (L + R) / 2;
    return (f(L) * f(B) < 0) ? half_division(L, B, B) : half_division(B, R, B);
}

int main()
{
    vector<long double> res = half_division(1, 3, (1+3)/2.0);
    cout << res[0] << " " << res[1] << endl;
    return 0;
}
