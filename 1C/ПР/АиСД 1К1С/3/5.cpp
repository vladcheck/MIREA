#include "./header files/5.h"
#include <cmath>
#include <chrono>

string karatsuba(long long base, long long a, long long b)
{
    long long m = ceil((to_string(a).size() + to_string(b).size()) / 4.0);
    long long B = pow(base, m);
    long long x0 = a / B;
    long long x1 = a % B;
    long long y0 = b / B;
    long long y1 = b % B;
    long long z2 = x0 * y0;
    long long z0 = x1 * y1;
    long long z1 = (x0 + x1) * (y0 + y1) - z0 - z2;
    return to_string(z2 * B * B + z1 * B + z0);
}

int main()
{
    auto start = chrono::high_resolution_clock::now();
    cout << karatsuba(10, 123234123, 23234) << endl;
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = end - start;
    cout << "Karatsuba(): " << elapsed.count() << " sec" << endl;
    double dur1 = elapsed.count();

    start = chrono::high_resolution_clock::now();
    mult("1232341999999999999999999999999999999999999999999999999123234199999999999999999999999999999999999999999999999999999999999999239999999999999923", "299999999999999999999999999999222222222222222222222222222222222323412323419999999999999999999999999999999999999999999999999999999999999923");
    end = chrono::high_resolution_clock::now();
    elapsed = end - start;
    cout << "Mult(): " << elapsed.count() << " sec" << endl;
    double dur2 = elapsed.count();

    cout << "Difference: " << abs(dur1 - dur2) << " sec" << endl;

    return 0;
}
