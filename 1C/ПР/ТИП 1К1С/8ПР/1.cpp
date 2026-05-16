#include <iostream>
using namespace std;

long double pow(double long a, int b)
{
  cout << b << endl;
  if (b == 0)
    return 1;
  if (b % 2 == 0)
  {
    long double val = pow(a, b / 2); // раскладываем четную степень на две половины (2^6=2^3*2^3)
    return val * val;
  }
  else
  {
    return a * pow(a, b - 1); // считаем рекурсивно четную степень (b-1) и умножаем на a
  }
}

int main()
{
  long double a;
  int b;
  cin >> a >> b;
  cout << pow(a, b);
  return 0;
}