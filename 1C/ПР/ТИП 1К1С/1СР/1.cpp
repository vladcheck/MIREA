#include <iostream>
using namespace std;

int main()
{
    char action;
    int a, b;
    cin >> a >> action >> b;
    switch (action)
    {
    case '+':
        cout << a + b;
        break;
    case '-':
        cout << a - b;
        break;
    case '*':
        cout << a * b;
        break;
    case '/':
        cout << a / b;
        break;
    }
    return 0;
}